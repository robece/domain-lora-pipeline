import logging
from pathlib import Path
import requests
import importlib.util

# ---------------------------------------------------------
# Carga dinámica del retriever numerado
# ---------------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent
retriever_path = BASE_DIR / "6.retriever.py"

spec = importlib.util.spec_from_file_location("retriever", retriever_path)
retriever = importlib.util.module_from_spec(spec)
spec.loader.exec_module(retriever)

search = retriever.search

# ---------------------------------------------------------
# Configuración general del RAG Query
# ---------------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent.parent
LOG_PATH = BASE_DIR / "logs" / "rag_query.log"

LLM_URL = "http://ollama:11434/api/generate"
LLM_MODEL = "qwen2.5:14b"

TOP_K = 5

LOG_PATH.parent.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    filename=str(LOG_PATH),
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)

logging.info("=== START: RAG Query Initialized ===")

# ---------------------------------------------------------
# Construcción del contexto
# ---------------------------------------------------------

def build_context(results):
    context_blocks = []
    for r in results:
        source = r.get("source_article", "unknown")
        toc_path = " > ".join(r.get("toc_path", []))
        text = r.get("text", "")
        block = f"[Source: {source} | Path: {toc_path}]\n{text}"
        context_blocks.append(block)
    return "\n\n---\n\n".join(context_blocks)

# ---------------------------------------------------------
# Modos de prompt
# ---------------------------------------------------------

def prompt_default(question, context):
    return f"""
You must answer ONLY using the information in the CONTEXT.

CONTEXT:
{context}

QUESTION:
{question}

ANSWER:
""".strip()

def prompt_strict(question, context):
    return f"""
STRICT MODE:
You are forbidden from using any information that is not present in the CONTEXT.
If the answer is not fully supported by the context, respond exactly:
"I don't know based on the provided context."

Do NOT infer, assume, generalize, or guess.

CONTEXT:
{context}

QUESTION:
{question}

STRICT ANSWER:
""".strip()

def prompt_developer(question, context):
    return f"""
Developer Mode:
Provide a technical explanation using ONLY the CONTEXT.

Your answer must include:
- a high-level summary
- a step-by-step breakdown
- relevant constraints or edge cases
- references to the source/path when applicable

Avoid conversational tone.

CONTEXT:
{context}

QUESTION:
{question}

TECHNICAL ANSWER:
""".strip()

def prompt_bullets(question, context):
    return f"""
Format your answer using:
- bullet points
- short sections
- clear headings (if helpful)

Each bullet must be directly supported by the CONTEXT.

CONTEXT:
{context}

QUESTION:
{question}

STRUCTURED ANSWER:
""".strip()

# ---------------------------------------------------------
# Detección automática del modo
# ---------------------------------------------------------

def detect_mode(question: str) -> str:
    q = question.lower()

    if any(x in q for x in ["cómo funciona", "como funciona", "cómo opera", "flujo", "proceso", "arquitectura"]):
        return "developer"

    if any(x in q for x in ["lista", "pasos", "puntos", "resumen", "bullets", "enumerar"]):
        return "bullets"

    if any(x in q for x in ["exactamente", "estrictamente", "según el contexto", "solo con el contexto"]):
        return "strict"

    return "default"

# ---------------------------------------------------------
# Selector de prompt
# ---------------------------------------------------------

def build_prompt(question: str, context: str, mode: str):
    mode = mode.lower().strip()

    if mode == "strict":
        return prompt_strict(question, context)
    elif mode == "developer":
        return prompt_developer(question, context)
    elif mode == "bullets":
        return prompt_bullets(question, context)
    else:
        return prompt_default(question, context)

# ---------------------------------------------------------
# Llamada al LLM local (Ollama)
# ---------------------------------------------------------

def call_llm(prompt: str) -> str:
    payload = {
        "model": LLM_MODEL,
        "prompt": prompt,
        "stream": False,
    }

    logging.info("Calling local LLM (Ollama)...")
    r = requests.post(LLM_URL, json=payload)

    if r.status_code != 200:
        logging.error(f"LLM error: {r.text}")
        return f"[LLM ERROR] {r.text}"

    return r.json().get("response", "")

# ---------------------------------------------------------
# Función principal de RAG
# ---------------------------------------------------------

def rag_query(question: str, k: int = TOP_K, mode: str = "auto"):
    logging.info(f"Processing RAG question: {question} | mode={mode}")

    if mode.lower() == "auto":
        mode = detect_mode(question)
        logging.info(f"Auto-selected mode: {mode}")

    results = search(question, k=k)
    context = build_context(results)
    prompt = build_prompt(question, context, mode)
    answer = call_llm(prompt)

    logging.info("RAG answer generated successfully.")
    return answer, results

# ---------------------------------------------------------
# CLI
# ---------------------------------------------------------

if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python3 7.rag_query.py \"your question\" [mode]")
        exit()

    question = sys.argv[1]
    mode = sys.argv[2] if len(sys.argv) > 2 else "auto"

    answer, results = rag_query(question, mode=mode)

    print("\n=== ANSWER ===\n")
    print(answer)

    print("\n=== SOURCES ===\n")
    for r in results:
        source = r.get("source_article", "unknown")
        toc_path = " > ".join(r.get("toc_path", []))
        score = r.get("score", 0.0)
        print(f"- {source} | {toc_path} | score={score:.4f}")
