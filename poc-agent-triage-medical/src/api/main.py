import os, sys, asyncio, time, uuid, json, httpx, gradio as gr, uvicorn
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
from contextlib import asynccontextmanager
from pathlib import Path

# --- CONFIGURATION ---
VENV_PYTHON = "/Users/mpaga/.venv-vllm-metal/bin/python"
VLLM_BINARY = "/Users/mpaga/.venv-vllm-metal/bin/vllm"

# On force les chemins absolus pour éviter les erreurs de vLLM
BASE_DIR = Path(__file__).resolve().parent.parent.parent
MODEL_PATH = str( "models/merged_dpo_final_chsa")
LOG_FILE = str(BASE_DIR / "logs" / "audit_medical.jsonl")

VLLM_PORT = 8000
API_PORT = 8001

# Forçage des variables d'environnement Mac M1
os.environ.update({
    "VLLM_TARGET_DEVICE": "mps",
    "PYTORCH_ENABLE_MPS_FALLBACK": "1",
    "HF_HUB_OFFLINE": "1"
})

#if sys.executable != VENV_PYTHON:
    #os.execv(VENV_PYTHON, [VENV_PYTHON] + sys.argv)

vllm_process = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    global vllm_process
    Path(LOG_FILE).parent.mkdir(exist_ok=True)
    
    print(f"📥 [vLLM] Initialisation du moteur sur GPU Metal (MPS)...")
    
    # Lancement du processus vLLM
    vllm_process = await asyncio.create_subprocess_exec(
        VLLM_BINARY, "serve", MODEL_PATH,
        "--port", str(VLLM_PORT),
        "--host", "127.0.0.1",
        stdout=None, stderr=None 
    )
    
    # Boucle de Health Check
    print("⏳ Attente du chargement des poids (environ 60s)...")
    for i in range(20):
        await asyncio.sleep(5)
        try:
            async with httpx.AsyncClient() as client:
                resp = await client.get(f"http://127.0.0.1:{VLLM_PORT}/health")
                if resp.status_code == 200:
                    print("✅ [vLLM] Moteur opérationnel.")
                    break
        except:
            print(f"   ... attente {i+1}/20")
            
    yield
    if vllm_process:
        print("🛑 Arrêt du service.")
        try:
            vllm_process.terminate()
            await vllm_process.wait()
        except: pass

app = FastAPI(title="CHSA AI Gateway", lifespan=lifespan)

class Message(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    history: List[Message]
    patient_id: str = "A1"

@app.post("/chat")
async def chat_endpoint(request: ChatRequest):
    start_time = time.time()
    
    # ATTENTION : Le nom du modèle dans le payload doit être le chemin exact
    payload = {
        "model": MODEL_PATH,
        "messages": [m.model_dump() for m in request.history],
        "temperature": 0.3,
        "repetition_penalty": 1.15,
        "max_tokens": 1024
    }

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"http://127.0.0.1:{VLLM_PORT}/v1/chat/completions", 
                json=payload, 
                timeout=120.0 # Timeout long pour le raisonnement
            )
        
        if response.status_code != 200:
            print(f"❌ Erreur vLLM : {response.text}")
            raise HTTPException(status_code=500, detail=f"Moteur vLLM Erreur: {response.text}")

        result = response.json()
        ai_response = result["choices"][0]["message"]["content"]
        
        # Log Audit (Conformité Traçabilité)
        log = {"id": str(uuid.uuid4()), "patient": request.patient_id, "lat": round(time.time()-start_time, 3), "out": ai_response}
        with open(LOG_FILE, "a") as f: f.write(json.dumps(log, ensure_ascii=False) + "\n")

        return {"assistant_response": ai_response, "audit_ref": log["id"]}

    except Exception as e:
        print(f"❌ Crash Inférence : {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

async def gradio_chat(message, history):
    api_history = [{"role": "system", "content": "Tu es l'infirmier du CHSA. Sois concis et bilingue."}]
    for msg in history:
        content = msg["content"]
        if isinstance(content, list): content = content[0]["text"]
        api_history.append({"role": msg["role"], "content": content})
    api_history.append({"role": "user", "content": message})
    
    try:
        async with httpx.AsyncClient() as client:
            r = await client.post(f"http://127.0.0.1:{API_PORT}/chat", json={"history": api_history}, timeout=120.0)
            return r.json()["assistant_response"]
    except Exception as e:
        return f"⏳ Erreur de communication... ({e})"

demo = gr.ChatInterface(fn=gradio_chat,  title="🏥 Agent Triage CHSA")
app = gr.mount_gradio_app(app, demo, path="/")

#if __name__ == "__main__":
uvicorn.run(app, host="127.0.0.1", port=API_PORT, workers=1)