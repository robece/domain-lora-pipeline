import json
import logging
from pathlib import Path
from tqdm import tqdm
import os
import numpy as np
import faiss
from openai import AzureOpenAI

# ---------------------------------------------------------
# Configuración general del proceso de validación
# ---------------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent.parent

QUESTIONS_PATH = BASE_DIR / "data" / "generated_questions.jsonl"
EMBEDDINGS_PATH = BASE_DIR / "data" / "embeddings.npy"
METADATA_PATH = BASE_DIR / "data" / "embeddings_metadata.jsonl"
FAISS_INDEX_PATH = BASE_DIR / "data" / "faiss.index"

OUTPUT_VALID = BASE_DIR / "data" / "validated_questions.jsonl"
OUTPUT_INVALID = BASE_DIR / "data" / "invalid_questions.jsonl"

LOG_PATH = BASE_DIR / "logs" / "validate_questions.log"
LOG_PATH.parent.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    filename=str(LOG_PATH),
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)

# Cliente Azure OpenAI
client = AzureOpenAI(
    api_key=os.getenv("AZURE_OPENAI_KEY"),
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
    api_version=os.getenv("AZURE_OPENAI_API_VERSION")
)

EMBEDDING_MODEL = "text-embedding-3-large"
LLM_MODEL = "gpt-4o"

# ---------------------------------------------------------
# Carga de FAISS y embeddings
# ---------------------------------------------------------

index = faiss.read_index(str(FAISS_INDEX_PATH))
embeddings = np.load(EMBEDDINGS_PATH)

metadata = []
with open(METADATA_PATH, "r", encoding="utf-8") as f:
    for line in f:
        metadata.append(json.loads(line))

# ---------------------------------------------------------
# Prompt de validación
# ---------------------------------------------------------

VALIDATION_PROMPT = """
You are a strict validator.

Determine whether the following question can be answered strictly using the provided context.

Rules:
- If the context contains enough information to answer the question → respond "VALID".
- If the context does NOT contain enough information → respond "INVALID".
- Do NOT explain. Only output VALID or INVALID.

QUESTION:
{question}

CONTEXT:
{context}
"""

# ---------------------------------------------------------
# Preparación de archivos de salida
# ---------------------------------------------------------

if OUTPUT_VALID.exists():
    OUTPUT_VALID.unlink()

if OUTPUT_INVALID.exists():
    OUTPUT_INVALID.unlink()

questions = [json.loads(line) for line in open(QUESTIONS_PATH, "r", encoding="utf-8")]

valid_count = 0
invalid_count = 0

# ---------------------------------------------------------
# Función para generar embeddings con Azure OpenAI
# ---------------------------------------------------------

def embed_text(text: str):
    """Generate embedding using Azure OpenAI."""
    response = client.embeddings.create(
        model=EMBEDDING_MODEL,
        input=text
    )
    return np.array(response.data[0].embedding, dtype=np.float32)

# ---------------------------------------------------------
# Bucle principal de validación masiva
# ---------------------------------------------------------

with open(OUTPUT_VALID, "a", encoding="utf-8") as f_valid, \
     open(OUTPUT_INVALID, "a", encoding="utf-8") as f_invalid:

    for item in tqdm(questions, desc="Validating questions"):
        question = item["question"]

        # Generar embedding de la pregunta
        q_emb = embed_text(question).reshape(1, -1)

        # Recuperar contexto desde FAISS
        scores, idxs = index.search(q_emb, 5)

        context_chunks = []
        for idx in idxs[0]:
            meta = metadata[idx]
            context_chunks.append(json.dumps(meta, ensure_ascii=False))

        context_text = "\n\n".join(context_chunks)

        # Construir prompt de validación
        prompt = VALIDATION_PROMPT.format(
            question=question,
            context=context_text
        )

        # Llamada al modelo Azure OpenAI
        try:
            response = client.chat.completions.create(
                model=LLM_MODEL,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.0,
            )

            raw = response.choices[0].message.content.strip().upper()

            # Validar que el modelo devolvió un veredicto correcto
            if raw not in ("VALID", "INVALID"):
                logging.error(f"[INVALID_VERDICT] question={question} raw='{raw}'")
                continue

            verdict = raw

            if verdict == "VALID":
                valid_count += 1
                f_valid.write(json.dumps(item, ensure_ascii=False) + "\n")
            else:
                invalid_count += 1
                f_invalid.write(json.dumps(item, ensure_ascii=False) + "\n")

        except Exception as e:
            logging.error(f"Error validating question: {e}")

# ---------------------------------------------------------
# Resumen final del proceso
# ---------------------------------------------------------

print("\n=== VALIDATION SUMMARY ===")
print(f"Valid questions:   {valid_count}")
print(f"Invalid questions: {invalid_count}")
print(f"Saved valid questions to:   {OUTPUT_VALID}")
print(f"Saved invalid questions to: {OUTPUT_INVALID}")
