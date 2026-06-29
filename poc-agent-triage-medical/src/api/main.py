import os, sys, asyncio, time, uuid, json, httpx, gradio as gr, uvicorn
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from contextlib import asynccontextmanager
from pathlib import Path

# --- CONFIGURATION (Déplacé vers config.py) ---
# Importation de la configuration centralisée
from src.api.config import (
    VLLM_BINARY_PATH, MODEL_PATH, LOG_FILE, VLLM_PORT, API_PORT,
    VLLM_HOST, VLLM_SERVER_ARGS, VLLM_LOG_FILE, IS_PRODUCTION
)

# Forçage des variables d'environnement Mac M1
# Uniquement en développement local sur Mac
if not IS_PRODUCTION:
    os.environ.update({
        "VLLM_TARGET_DEVICE": "mps",
        "PYTORCH_ENABLE_MPS_FALLBACK": "1",
        "HF_HUB_OFFLINE": "1"
    })

vllm_process = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    global vllm_process
    Path(LOG_FILE).parent.mkdir(parents=True, exist_ok=True)
    Path(VLLM_LOG_FILE).parent.mkdir(parents=True, exist_ok=True)
    
    print(f"📥 [vLLM] Initialisation du moteur sur GPU Metal (MPS)...")
    
    # Lancement du processus vLLM
    vllm_process = await asyncio.create_subprocess_exec(
        VLLM_BINARY_PATH, "serve", MODEL_PATH,
        *VLLM_SERVER_ARGS,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )
    
    # Boucle de Health Check
    print("⏳ Attente du chargement des poids (environ 60s)...")
    for i in range(3):
        await asyncio.sleep(5)
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                resp = await client.get(f"http://{VLLM_HOST}:{VLLM_PORT}/health")
                if resp.status_code == 200:
                    print("✅ [vLLM] Moteur opérationnel.")
                    break
        except:
            print(f"   ... attente {i+1}/20")
            
    # Log des sorties du processus vLLM pour le débogage
    async def log_stream(stream, log_file):
        with open(log_file, 'ab') as f:
            async for line in stream:
                f.write(line)
    asyncio.create_task(log_stream(vllm_process.stdout, VLLM_LOG_FILE))
    asyncio.create_task(log_stream(vllm_process.stderr, VLLM_LOG_FILE))

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
    patient_id: Optional[str] = "A1"

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
                f"http://{VLLM_HOST}:{VLLM_PORT}/v1/chat/completions", 
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
            r = await client.post(f"http://127.0.0.1:{API_PORT}/chat", json={"history": api_history, "patient_id": "gradio_user"}, timeout=120.0)
            return r.json()["assistant_response"]
    except Exception as e:
        return f"⏳ Erreur de communication... ({e})"

demo = gr.ChatInterface(fn=gradio_chat,  title="🏥 Agent Triage CHSA")
app = gr.mount_gradio_app(app, demo, path="/")

#if __name__ == "__main__":
    # Ce bloc est pour le développement local uniquement.
uvicorn.run("src.api.main:app", host="127.0.0.1", port=API_PORT, reload=True)