import json
import logging
import numpy as np
from pathlib import Path
from tqdm import tqdm
import faiss
import os
from openai import AzureOpenAI

# ---------------------------------------------------------
# Configuración general del proceso de generación de embeddings
# ---------------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent.parent

CORPUS_PATH = BASE_DIR / "data" / "corpus_clean.jsonl"
EMBEDDINGS_PATH = BASE_DIR / "data" / "embeddings.npy"
METADATA_PATH = BASE_DIR / "data" / "embeddings_metadata.jsonl"
FAISS_INDEX_PATH = BASE_DIR / "data" / "faiss.index"
LOG_PATH = BASE_DIR / "logs" / "generate_embeddings.log"

LOG_PATH.parent.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    filename=str(LOG_PATH),
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)

logging.info("=== START: Generating Embeddings for Clean Corpus ===")

# ---------------------------------------------------------
# Cliente Azure OpenAI
# ---------------------------------------------------------

client = AzureOpenAI(
    api_key=os.getenv("AZURE_OPENAI_KEY"),
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
    api_version=os.getenv("AZURE_OPENAI_API_VERSION"),
)

EMBEDDING_MODEL = "text-embedding-3-large"
logging.info(f"Using Azure OpenAI embedding model: {EMBEDDING_MODEL}")

# ---------------------------------------------------------
# Carga del corpus limpio
# ---------------------------------------------------------

logging.info(f"Loading corpus from {CORPUS_PATH}")

corpus_entries = []
with open(CORPUS_PATH, "r", encoding="utf-8") as f:
    for line in f:
        try:
            corpus_entries.append(json.loads(line))
        except Exception as e:
            logging.error(f"[ERROR] Invalid JSON line: {e}")

logging.info(f"Corpus entries loaded: {len(corpus_entries)}")

# ---------------------------------------------------------
# Preparación de archivos de salida
# ---------------------------------------------------------

if METADATA_PATH.exists():
    METADATA_PATH.unlink()
if EMBEDDINGS_PATH.exists():
    EMBEDDINGS_PATH.unlink()
if FAISS_INDEX_PATH.exists():
    FAISS_INDEX_PATH.unlink()

# ---------------------------------------------------------
# Preparación de textos y metadata
# ---------------------------------------------------------

texts = []
metadata = []

for entry in corpus_entries:
    text = entry.get("text", "")
    if not text or not text.strip():
        logging.warning(f"Skipping empty text for ID={entry.get('id')}")
        continue

    texts.append(text)
    metadata.append({
        "id": entry.get("id"),
        "chunk_id": entry.get("chunk_id"),
        "source_article": entry.get("source_article"),
        "toc_path": entry.get("toc_path"),
    })

logging.info(f"Valid texts for embedding: {len(texts)}")

if not texts:
    logging.error("No valid texts found for embedding. Aborting.")
    print("No valid texts found for embedding. Aborting.")
    raise SystemExit(1)

# ---------------------------------------------------------
# Generación de embeddings
# ---------------------------------------------------------

batch_size = 32
all_embeddings = []

logging.info("Starting embedding generation with Azure OpenAI...")

for i in tqdm(range(0, len(texts), batch_size)):
    batch = texts[i:i + batch_size]

    try:
        response = client.embeddings.create(
            model=EMBEDDING_MODEL,
            input=batch,
        )
        batch_embeddings = [item.embedding for item in response.data]
        all_embeddings.append(np.array(batch_embeddings, dtype=np.float32))

    except Exception as e:
        logging.error(f"Error generating embeddings for batch {i}: {e}")

if not all_embeddings:
    logging.error("No embeddings were generated. Aborting.")
    print("No embeddings were generated. Aborting.")
    raise SystemExit(1)

embeddings = np.vstack(all_embeddings)
logging.info(f"Embeddings shape (before normalization): {embeddings.shape}")

# ---------------------------------------------------------
# Normalización L2 para búsquedas por producto interno
# ---------------------------------------------------------

faiss.normalize_L2(embeddings)
logging.info("Embeddings normalized with L2 for inner product search.")

np.save(EMBEDDINGS_PATH, embeddings)
logging.info(f"Embeddings saved to {EMBEDDINGS_PATH}")

with open(METADATA_PATH, "w", encoding="utf-8") as f:
    for m in metadata:
        f.write(json.dumps(m, ensure_ascii=False) + "\n")

logging.info(f"Metadata saved to {METADATA_PATH}")

# ---------------------------------------------------------
# Construcción del índice FAISS
# ---------------------------------------------------------

dim = embeddings.shape[1]
logging.info(f"Building FAISS IndexFlatIP with dim={dim}")

index = faiss.IndexFlatIP(dim)
index.add(embeddings)

faiss.write_index(index, str(FAISS_INDEX_PATH))
logging.info(f"FAISS index saved to {FAISS_INDEX_PATH}")

logging.info("=== END: Embeddings + FAISS generation complete ===")

print(f"Embeddings saved: {EMBEDDINGS_PATH}")
print(f"Metadata saved: {METADATA_PATH}")
print(f"FAISS index saved: {FAISS_INDEX_PATH}")
