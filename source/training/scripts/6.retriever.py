import json
import logging
import numpy as np
from pathlib import Path
import faiss
import os
from openai import AzureOpenAI

# ---------------------------------------------------------
# Configuración general del retriever
# ---------------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent.parent

INDEX_PATH = BASE_DIR / "data" / "faiss.index"
METADATA_PATH = BASE_DIR / "data" / "embeddings_metadata.jsonl"
CORPUS_PATH = BASE_DIR / "data" / "corpus_clean.jsonl"
LOG_PATH = BASE_DIR / "logs" / "retriever.log"

TOP_K = 5
EMBEDDING_MODEL = "text-embedding-3-large"

LOG_PATH.parent.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    filename=str(LOG_PATH),
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)

logging.info("=== START: Retriever Initialized ===")

# ---------------------------------------------------------
# Cliente Azure OpenAI
# ---------------------------------------------------------

client = AzureOpenAI(
    api_key=os.getenv("AZURE_OPENAI_KEY"),
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
    api_version=os.getenv("AZURE_OPENAI_API_VERSION"),
)

logging.info(f"Using Azure OpenAI embedding model: {EMBEDDING_MODEL}")

# ---------------------------------------------------------
# Carga del índice FAISS
# ---------------------------------------------------------

if not INDEX_PATH.exists():
    raise FileNotFoundError(f"FAISS index not found: {INDEX_PATH}")

index = faiss.read_index(str(INDEX_PATH))
dim = index.d

logging.info(f"FAISS index loaded with dim={dim} and total={index.ntotal}")

# ---------------------------------------------------------
# Carga de metadata
# ---------------------------------------------------------

metadata = []
with open(METADATA_PATH, "r", encoding="utf-8") as f:
    for line in f:
        metadata.append(json.loads(line))

logging.info(f"Metadata entries loaded: {len(metadata)}")

# ---------------------------------------------------------
# Carga del corpus
# ---------------------------------------------------------

corpus = []
with open(CORPUS_PATH, "r", encoding="utf-8") as f:
    for line in f:
        corpus.append(json.loads(line))

logging.info(f"Corpus chunks loaded: {len(corpus)}")

# ---------------------------------------------------------
# Función de embedding
# ---------------------------------------------------------

def embed_query(text: str) -> np.ndarray:
    """Generate normalized embedding for a query using Azure OpenAI."""
    logging.info(f"Embedding query: {text}")

    response = client.embeddings.create(
        model=EMBEDDING_MODEL,
        input=[text],
    )

    emb = np.array(response.data[0].embedding, dtype=np.float32)
    emb /= np.linalg.norm(emb)

    return emb.reshape(1, -1)

# ---------------------------------------------------------
# Función de búsqueda
# ---------------------------------------------------------

def search(query: str, k: int = TOP_K):
    """Retrieve top‑k relevant chunks using FAISS."""
    logging.info(f"Searching top-{k} for query: {query}")

    q_emb = embed_query(query)
    D, I = index.search(q_emb, k)

    results = []

    for idx, score in zip(I[0], D[0]):
        meta = metadata[idx]
        chunk = corpus[idx]

        results.append({
            "score": float(score),
            "id": chunk["id"],
            "chunk_id": chunk["chunk_id"],
            "source_article": chunk["source_article"],
            "toc_path": chunk["toc_path"],
            "text": chunk["text"],
        })

    logging.info(f"Retrieved {len(results)} results.")
    return results

# ---------------------------------------------------------
# CLI
# ---------------------------------------------------------

if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python3 retriever.py \"your question\"")
        exit()

    query = sys.argv[1]
    results = search(query)

    print("\n=== RESULTS ===\n")
    for r in results:
        print(f"[score={r['score']:.4f}] {r['source_article']} → {r['toc_path']}")
        print(r["text"])
        print()
