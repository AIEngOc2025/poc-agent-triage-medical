"""Orchestration de l'agent d'échecs FFE via un graphe d'états LangGraph."""

import os
from typing import Annotated, Literal, Sequence
from typing_extensions import TypedDict

from langchain_core.messages import BaseMessage, SystemMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.graph import END, StateGraph, START
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode

# Imports sécurisés de vos outils locaux
from tools.milvus_tools import query_wikichess
from tools.stockfish_tools import evaluate_position
from tools.youtube_tools import search_chess_videos


# 1. Définition de l'état du graphe (State)
class AgentState(TypedDict):
    """L'état du graphe, contenant la séquence cumulative des messages."""

    messages: Annotated[Sequence[BaseMessage], add_messages]


# 2. Initialisation du LLM et liaison avec les outils (Tool Binding)
tools = [query_wikichess, evaluate_position, search_chess_videos]

model = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    google_api_key=os.getenv("GOOGLE_API_KEY"),
    temperature=0.2,
).bind_tools(tools)


# 3. Définition des nœuds (Nodes)
def call_model(state: AgentState) -> dict:
    """Nœud chargé d'interroger le LLM avec l'historique des messages."""
    messages = list(state["messages"])

    sys_prompt = (
        "Tu es un Grand Maître International d'échecs, entraîneur pour la "
        "Fédération Française des Échecs (FFE). Tu accompagnes de jeunes espoirs. "
        "Sois précis, pédagogue et utilise tes outils dès qu'une position FEN, "
        "une ouverture ou un besoin de vidéo est détecté. Réponds toujours en français."
    )

    # Injection du prompt système si non présent au début
    if not messages or messages[0].type != "system":
        messages = [SystemMessage(content=sys_prompt)] + messages

    response = model.invoke(messages)
    return {"messages": [response]}


# 4. Logique de routage conditionnel (Conditional Edges)
def should_continue(state: AgentState) -> Literal["tools", "__end__"]:
    """Détermine si le LLM a demandé l'exécution d'outils ou s'il faut s'arrêter."""
    messages = state["messages"]
    last_message = messages[-1]

    if hasattr(last_message, "tool_calls") and last_message.tool_calls:
        return "tools"
    return END


# 5. Construction et compilation du graphe (Workflow)
workflow = StateGraph(AgentState)

# Ajout des nœuds fonctionnels
workflow.add_node("agent", call_model)
workflow.add_node("tools", ToolNode(tools))

# Configuration des liaisons (Edges)
workflow.add_edge(START, "agent")
workflow.add_conditional_edges(
    "agent",
    should_continue,
)
workflow.add_edge("tools", "agent")

# !!
#importée par main.py pour l'exécution du graphe dans le backend FastAPI
chess_agent_graph = workflow.compile()