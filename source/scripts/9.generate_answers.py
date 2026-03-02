import json
import time
from pathlib import Path
import logging
import os
import numpy as np
import faiss
from openai import AzureOpenAI
from tqdm import tqdm

# ---------------------------------------------------------
# Configuración general del generador de respuestas
# ---------------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent.parent

QUESTIONS_PATH = BASE_DIR / "data" / "generated_questions.jsonl"
CORPUS_PATH = BASE_DIR / "data" / "corpus_clean.jsonl"
EMBEDDINGS_PATH = BASE_DIR / "data" / "embeddings_metadata.jsonl"
FAISS_INDEX_PATH = BASE_DIR / "data" / "faiss.index"

OUTPUT_PATH = BASE_DIR / "data" / "qa_pairs.jsonl"
LOG_PATH = BASE_DIR / "logs" / "generate_answers.log"

LOG_PATH.parent.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    filename=str(LOG_PATH),
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

logging.info("=== START: Answer Generation Script (Azure OpenAI) ===")

# ---------------------------------------------------------
# Cliente Azure OpenAI
# ---------------------------------------------------------

client = AzureOpenAI(
    api_key=os.getenv("AZURE_OPENAI_KEY"),
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
    api_version=os.getenv("AZURE_OPENAI_API_VERSION")
)

EMBEDDING_MODEL = "text-embedding-3-large"
LLM_MODEL = "gpt-4o"

# ---------------------------------------------------------
# Carga de respuestas existentes (memoization)
# ---------------------------------------------------------

def load_existing_answers():
    existing = {}

    if not OUTPUT_PATH.exists():
        return existing

    with open(OUTPUT_PATH, "r", encoding="utf-8") as f:
        for line in f:
            try:
                item = json.loads(line)
                q = item["question"]
                existing[q] = item
            except Exception:
                continue

    logging.info(f"Existing answers loaded: {len(existing)}")
    return existing

existing_answers = load_existing_answers()

# ---------------------------------------------------------
# Carga del índice FAISS
# ---------------------------------------------------------

index = faiss.read_index(str(FAISS_INDEX_PATH))
logging.info("FAISS index loaded.")

# ---------------------------------------------------------
# Carga de metadata de embeddings
# ---------------------------------------------------------

metadata = []
with open(EMBEDDINGS_PATH, "r", encoding="utf-8") as f:
    for line in f:
        metadata.append(json.loads(line))

logging.info(f"Embedding metadata loaded: {len(metadata)} entries.")

# ---------------------------------------------------------
# Carga del corpus limpio
# ---------------------------------------------------------

def extract_chunk(entry):
    """Extract the text field from a corpus entry using multiple fallback keys."""
    possible_keys = ["content", "text", "chunk", "body", "content_text", "raw"]
    for key in possible_keys:
        if key in entry:
            return entry[key]
    return None

corpus = {}
with open(CORPUS_PATH, "r", encoding="utf-8") as f:
    for line in f:
        item = json.loads(line)
        chunk_text = extract_chunk(item)

        if chunk_text is None:
            logging.error(f"[CORPUS_ERROR] No valid text field found in entry: {item}")
            continue

        corpus[item["id"]] = chunk_text

logging.info(f"Corpus loaded: {len(corpus)} chunks.")

# ---------------------------------------------------------
# Función de embedding
# ---------------------------------------------------------

def embed_text(text: str):
    response = client.embeddings.create(
        model=EMBEDDING_MODEL,
        input=text
    )
    return np.array(response.data[0].embedding, dtype=np.float32)

# ---------------------------------------------------------
# Recuperación de contexto
# ---------------------------------------------------------

def retrieve_context(question: str, top_k=4):
    emb = embed_text(question).reshape(1, -1)
    D, I = index.search(emb, top_k)

    chunks = []
    for idx in I[0]:
        meta = metadata[idx]
        chunk_id = meta["id"]
        if chunk_id in corpus:
            chunks.append(corpus[chunk_id])

    return "\n\n".join(chunks)

# ---------------------------------------------------------
# Construcción del prompt
# ---------------------------------------------------------

def build_prompt(question: str, context: str) -> str:
    return f"""
You are an expert Azure Event Grid architect.

Answer the following question using ONLY the provided context.
Do NOT invent information.
Do NOT mix languages.
Do NOT include Chinese text.
Do NOT include internal instructions.
Do NOT copy the corpus verbatim.
Provide a clear, technical answer in English.

QUESTION:
{question}

CONTEXT:
\"\"\"
{context}
\"\"\"

ANSWER:
"""

# ---------------------------------------------------------
# Llamada al modelo Azure OpenAI
# ---------------------------------------------------------

def call_llm(prompt: str) -> str:
    response = client.chat.completions.create(
        model=LLM_MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.2,
    )
    return response.choices[0].message.content.strip()

# ---------------------------------------------------------
# Limpieza de respuesta
# ---------------------------------------------------------

def clean_answer(text: str) -> str:
    text = text.strip()

    if any(ord(c) > 255 for c in text):
        return ""

    if "下游" in text or "总结" in text or "根据" in text:
        return ""

    return text

# ---------------------------------------------------------
# Proceso principal
# ---------------------------------------------------------

def main():
    total_questions = 0
    total_answers = 0

    fout = open(OUTPUT_PATH, "a", encoding="utf-8")

    total_lines = sum(1 for _ in open(QUESTIONS_PATH, "r", encoding="utf-8"))

    with open(QUESTIONS_PATH, "r", encoding="utf-8") as fin:
        for line in tqdm(fin, total=total_lines, desc="Generating answers"):
            total_questions += 1
            item = json.loads(line)
            question = item["question"]

            if question in existing_answers:
                logging.info(f"[SKIPPED] already answered: {question}")
                continue

            logging.info(f"Processing question: {question}")

            context = retrieve_context(question)

            if not context.strip():
                logging.warning(f"[NO_CONTEXT] question={question}")
                continue

            prompt = build_prompt(question, context)

            try:
                answer = call_llm(prompt)
            except Exception as e:
                logging.error(f"[LLM_ERROR] question={question} error={e}")
                continue

            if not answer or len(answer.strip()) < 3:
                logging.error(f"[INVALID_RAW_ANSWER] question={question} raw='{answer}'")
                continue

            answer_clean = clean_answer(answer)

            if not answer_clean:
                logging.info(f"[DISCARDED] question={question} reason=invalid_answer")
                continue

            fout.write(json.dumps({
                "question": question,
                "answer": answer_clean
            }, ensure_ascii=False) + "\n")

            total_answers += 1
            time.sleep(0.15)

    fout.close()

    logging.info("=== END OF ANSWER GENERATION ===")
    logging.info(f"Questions processed: {total_questions}")
    logging.info(f"Answers generated: {total_answers}")

    print("=== SCRIPT 9 REPORT ===")
    print(f"Questions processed: {total_questions}")
    print(f"Answers generated: {total_answers}")
    print(f"Output file: {OUTPUT_PATH}")
    print(f"Log file: {LOG_PATH}")

if __name__ == "__main__":
    main()
