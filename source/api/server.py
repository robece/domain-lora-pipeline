from fastapi import FastAPI, Request
from pydantic import BaseModel
from typing import List
from transformers import AutoModelForCausalLM, AutoTokenizer
from peft import PeftModel
from openai import AzureOpenAI
import torch
import faiss
import json
import numpy as np
import os
import logging
from datetime import datetime

# =========================================================
# Rutas reales de tu pipeline
# =========================================================

RAG_DIR = "/workspace/data"
FAISS_INDEX_PATH = os.path.join(RAG_DIR, "faiss.index")
METADATA_PATH = os.path.join(RAG_DIR, "embeddings_metadata.jsonl")
CORPUS_PATH = os.path.join(RAG_DIR, "corpus_clean.jsonl")

# =========================================================
# Modelo base + LoRA (Qwen2.5-3B)
# =========================================================

BASE_MODEL = "Qwen/Qwen2.5-3B-Instruct"
LORA_MODEL = "/workspace/models/qwen2.5-3b-lora-eventgrid"

print("Cargando tokenizer...")
tokenizer = AutoTokenizer.from_pretrained(BASE_MODEL, use_fast=False)

if tokenizer.pad_token is None:
    tokenizer.pad_token = tokenizer.eos_token

print("Cargando modelo base en GPU ROCm (BF16)...")
base_model = AutoModelForCausalLM.from_pretrained(
    BASE_MODEL,
    dtype=torch.bfloat16,
    device_map="auto",
)

print("Cargando LoRA en GPU ROCm...")
model = PeftModel.from_pretrained(
    base_model,
    LORA_MODEL,
    dtype=torch.bfloat16,
    device_map="auto",
)

model.eval()

# =========================================================
# Azure OpenAI embeddings
# =========================================================

AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_KEY")
AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
AZURE_OPENAI_API_VERSION = "2024-02-01"
AZURE_EMBEDDING_MODEL = "text-embedding-3-large"

client = AzureOpenAI(
    api_key=AZURE_OPENAI_API_KEY,
    api_version=AZURE_OPENAI_API_VERSION,
    azure_endpoint=AZURE_OPENAI_ENDPOINT,
)

def embed_texts(texts: List[str]) -> np.ndarray:
    vectors = []
    for t in texts:
        response = client.embeddings.create(
            model=AZURE_EMBEDDING_MODEL,
            input=t,
        )
        vec = np.array(response.data[0].embedding, dtype="float32")
        vec = vec / np.linalg.norm(vec)
        vectors.append(vec)
    return np.vstack(vectors)

# =========================================================
# Cargar FAISS + metadata + corpus
# =========================================================

print("Cargando índice FAISS...")
index = faiss.read_index(FAISS_INDEX_PATH)

print("Cargando metadata...")
metadata = []
with open(METADATA_PATH, "r", encoding="utf-8") as f:
    for line in f:
        metadata.append(json.loads(line))

print("Cargando corpus limpio...")
corpus = []
with open(CORPUS_PATH, "r", encoding="utf-8") as f:
    for line in f:
        obj = json.loads(line)
        corpus.append(obj["text"])

print(f"Chunks cargados: {len(corpus)}")
print(f"Metadata cargada: {len(metadata)}")

# =========================================================
# Logging
# =========================================================

LOG_DIR = "/logs"
os.makedirs(LOG_DIR, exist_ok=True)

LOG_PATH = os.path.join(LOG_DIR, "requests.log")

logging.basicConfig(
    filename=LOG_PATH,
    level=logging.INFO,
    format="%(message)s"
)

# =========================================================
# FastAPI
# =========================================================

app = FastAPI()

class Query(BaseModel):
    question: str
    top_k: int = 5

MAX_NEW_TOKENS = 500

# =========================================================
# Health check
# =========================================================

@app.get("/health")
def ping():
    return {"status": "ok"}

# =========================================================
# RAG
# =========================================================

def retrieve_context(question: str, top_k: int = 5) -> List[str]:
    q_emb = embed_texts([question])
    distances, indices = index.search(q_emb, top_k)
    return [corpus[idx] for idx in indices[0]]

# =========================================================
# Prompt
# =========================================================

def build_prompt(question: str, contexts: List[str]) -> str:
    context_block = "\n\n".join(contexts)
    return f"""Instruction: Answer using only the provided context. Do not use any external knowledge.
Input:
Context:
{context_block}

Question:
{question}

Answer:"""

# =========================================================
# Endpoint principal
# =========================================================

@app.post("/generate")
def generate_answer(q: Query, full_response: bool = False, request: Request = None):
    contexts = retrieve_context(q.question, q.top_k)
    prompt = build_prompt(q.question, contexts)

    inputs = tokenizer(prompt, return_tensors="pt").to(model.device)

    with torch.no_grad():
        outputs = model.generate(
            **inputs,
            max_new_tokens=MAX_NEW_TOKENS,
            temperature=0.2,
            top_p=0.9,
            repetition_penalty=1.1,
            do_sample=False,
        )

    text = tokenizer.decode(outputs[0], skip_special_tokens=True)

    # Extraer solo la parte después de "Answer:"
    final_text = text
    if not full_response and "Answer:" in text:
        final_text = text.split("Answer:", 1)[1].strip()

    # Logging
    log_entry = {
        "timestamp": datetime.utcnow().isoformat(),
        "client_ip": request.client.host if request else "unknown",
        "question": q.question,
        "response": final_text,
        "full_response": full_response,
        "top_k": q.top_k,
    }
    logging.info(json.dumps(log_entry, ensure_ascii=False))

    # =========================================================
    # FIX: respuesta minimal cuando full_response = false
    # =========================================================
    if not full_response:
        return {
            "question": q.question,
            "answer": final_text
        }

    # Respuesta completa si full_response = true
    return {
        "question": q.question,
        "contexts": contexts,
        "response": final_text,
        "max_tokens_used": MAX_NEW_TOKENS,
        "full_response": full_response,
    }
