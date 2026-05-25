import os
import random
import traceback
from typing import Optional
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from langchain_core.messages import HumanMessage
from dotenv import load_dotenv

# 1. Chargement de l'environnement
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# 2. Initialisation FastAPI
app = FastAPI(title="FFE Chess Agent API", version="2.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:4200"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# 3. Modèles Pydantic (Le contrat de données)
class ChatRequest(BaseModel):
    prompt: str = Field(..., description="Message de l'utilisateur")

class AnalysisRequest(BaseModel):
    fen: Optional[str] = Field(None, description="Position FEN")

class AgentResponse(BaseModel):
    status: str
    response: str

# 4. Simulation de secours (si LangGraph est indisponible)
def générer_analyse_simulée(fen: str) -> str:
    return f"🤖 [Mode Secours] Analyse pour : {fen[:15]}... La position est équilibrée."

# 5. Endpoints API (Standardisés /api/v1/)

@app.get("/")
def read_root():
    return {"status": "online", "framework": "FastAPI + LangGraph"}

@app.post("/api/v1/chat", response_model=AgentResponse)
async def chat_with_agent(payload: ChatRequest):
    """Dialogue ouvert avec l'agent."""
    try:
        # Ici tu inséreras ton appel chess_agent_graph.ainvoke(...)
        return AgentResponse(status="success", response=f"Echo du Maître : {payload.prompt}")
    except Exception as e:
        return AgentResponse(status="error", response=f"Erreur : {str(e)}")

@app.post("/api/v1/analyze-position", response_model=AgentResponse)
async def analyze_position(payload: AnalysisRequest):
    """Analyse de position FEN."""
    fen = payload.fen or "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"
    
    try:
        # Ici ton analyse réelle
        return AgentResponse(status="success", response=générer_analyse_simulée(fen))
    except Exception as e:
        return AgentResponse(status="error", response=f"Erreur d'analyse : {str(e)}")

# Lancement
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)