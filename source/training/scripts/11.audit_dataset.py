import json
import statistics
import numpy as np
import faiss
from pathlib import Path
from tqdm import tqdm
import os
import logging
import argparse
from openai import AzureOpenAI
import random
import time

# =========================================================
# Configuración general del proceso de auditoría
# =========================================================

BASE_DIR = Path(__file__).resolve().parent.parent

QA_PATH = BASE_DIR / "data" / "qa_pairs.jsonl"
CLEANED_QA_PATH = BASE_DIR / "data" / "qa_pairs.cleaned.jsonl"
LOW_FIDELITY_PATH = BASE_DIR / "data" / "qa_pairs.low_fidelity.jsonl"

EMBEDDINGS_PATH = BASE_DIR / "data" / "embeddings.npy"
METADATA_PATH = BASE_DIR / "data" / "embeddings_metadata.jsonl"
FAISS_INDEX_PATH = BASE_DIR / "data" / "faiss.index"

REPORT_PATH = BASE_DIR / "data" / "audit_report.json"
LOG_PATH = BASE_DIR / "logs" / "audit_dataset.log"

LOG_PATH.parent.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    filename=str(LOG_PATH),
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)

client = AzureOpenAI(
    api_key=os.getenv("AZURE_OPENAI_KEY"),
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
    api_version=os.getenv("AZURE_OPENAI_API_VERSION")
)

EMBEDDING_MODEL = "text-embedding-3-large"

# =========================================================
# Argumentos de ejecución
# =========================================================

parser = argparse.ArgumentParser(description="Audit and optionally clean QA dataset.")
parser.add_argument("--fix", action="store_true", help="Apply cleaning actions to dataset.")
args = parser.parse_args()

APPLY_FIX = args.fix

# =========================================================
# Carga de datos
# =========================================================

logging.info("Loading dataset...")
qa_pairs = [json.loads(line) for line in open(QA_PATH, "r", encoding="utf-8")]

logging.info("Loading FAISS index...")
index = faiss.read_index(str(FAISS_INDEX_PATH))

logging.info("Loading embeddings...")
embeddings = np.load(EMBEDDINGS_PATH)

logging.info("Loading metadata...")
metadata = [json.loads(line) for line in open(METADATA_PATH, "r", encoding="utf-8")]

# =========================================================
# Validación de consistencia FAISS/metadata
# =========================================================

if len(metadata) != index.ntotal:
    logging.error(f"Metadata size ({len(metadata)}) != FAISS index size ({index.ntotal})")
    raise ValueError("Metadata and FAISS index mismatch — regenerate embeddings + FAISS.")

# =========================================================
# Funciones auxiliares
# =========================================================

def embed_text(text: str, retries=2):
    """Generate embedding with automatic retry."""
    for attempt in range(retries):
        try:
            response = client.embeddings.create(
                model=EMBEDDING_MODEL,
                input=text
            )
            return np.array(response.data[0].embedding, dtype=np.float32)
        except Exception as e:
            logging.error(f"Embedding error (attempt {attempt+1}): {e}")
            time.sleep(1)
    return None

def contains_noise(text: str):
    """Detect unwanted characters or foreign-language noise."""
    if any(ord(c) > 255 for c in text):
        return True
    if "总结" in text or "根据" in text or "下游" in text:
        return True
    return False

def cosine_similarity(a, b):
    """Compute cosine similarity between two vectors."""
    if a is None or b is None:
        return 0.0
    return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))

def extract_chunk(meta):
    """Extract the text content from metadata using flexible key matching."""
    possible_keys = ["content", "text", "chunk", "body", "content_text", "raw"]
    for key in possible_keys:
        if key in meta:
            return meta[key]
    return None

# =========================================================
# Auditoría 1: Validez estructural
# =========================================================

logging.info("Running structural audit...")

invalid_fields = 0

for item in qa_pairs:
    if "question" not in item or "answer" not in item:
        invalid_fields += 1
    if not isinstance(item.get("question"), str):
        invalid_fields += 1
    if not isinstance(item.get("answer"), str):
        invalid_fields += 1

# =========================================================
# Auditoría 2: Duplicados
# =========================================================

logging.info("Checking duplicates...")

questions_seen = set()
answers_seen = set()
pairs_seen = set()

dup_questions = 0
dup_answers = 0
dup_pairs = 0

duplicate_indices = set()

for idx, item in enumerate(qa_pairs):
    q = item["question"]
    a = item["answer"]

    if q in questions_seen:
        dup_questions += 1
        duplicate_indices.add(idx)
    questions_seen.add(q)

    if a in answers_seen:
        dup_answers += 1
        duplicate_indices.add(idx)
    answers_seen.add(a)

    pair = (q, a)
    if pair in pairs_seen:
        dup_pairs += 1
        duplicate_indices.add(idx)
    pairs_seen.add(pair)

# =========================================================
# Auditoría 3: Ruido y respuestas cortas
# =========================================================

logging.info("Detecting noise...")

noise_indices = set()
short_indices = set()

for idx, item in enumerate(qa_pairs):
    ans = item["answer"]
    if contains_noise(ans):
        noise_indices.add(idx)
    if len(ans.split()) < 5:
        short_indices.add(idx)

# =========================================================
# Auditoría 4: Estadísticas de longitud
# =========================================================

logging.info("Computing length statistics...")

answer_lengths = [len(item["answer"].split()) for item in qa_pairs]

avg_len = statistics.mean(answer_lengths)
med_len = statistics.median(answer_lengths)
std_len = statistics.stdev(answer_lengths)

# =========================================================
# Auditoría 5: Fidelidad semántica
# =========================================================

logging.info("Validating semantic fidelity...")

semantic_scores = []
semantic_scores_random = []
semantic_scores_cross = []

low_fidelity_indices = set()

random_indices = random.sample(range(len(qa_pairs)), min(300, len(qa_pairs)))

for idx, item in enumerate(tqdm(qa_pairs, desc="Semantic fidelity")):
    q = item["question"]
    a = item["answer"]

    a_emb = embed_text(a)
    q_emb = embed_text(q)

    if a_emb is None or q_emb is None:
        continue

    q_emb = q_emb.reshape(1, -1)

    try:
        scores, idxs = index.search(q_emb, 3)
    except Exception as e:
        logging.error(f"FAISS search error: {e}")
        continue

    context_text = ""
    for i in idxs[0]:
        chunk = extract_chunk(metadata[i])
        if chunk:
            context_text += chunk + " "

    ctx_emb = embed_text(context_text)
    if ctx_emb is None:
        continue

    sim = cosine_similarity(a_emb, ctx_emb)
    if not np.isnan(sim):
        semantic_scores.append(sim)

# =========================================================
# Distribución inicial
# =========================================================

logging.info("Computing distribution...")

p10 = float(np.percentile(semantic_scores, 10))
p25 = float(np.percentile(semantic_scores, 25))
p50 = float(np.percentile(semantic_scores, 50))
p75 = float(np.percentile(semantic_scores, 75))
p90 = float(np.percentile(semantic_scores, 90))
std_sim = float(np.std(semantic_scores))

hist, bins = np.histogram(semantic_scores, bins=20)

# =========================================================
# Calibración robusta
# =========================================================

logging.info("Calibrating metrics...")

def safe_embed(text):
    if not text or not isinstance(text, str):
        return None
    return embed_text(text)

def try_append_similarity(target_list, emb_a, emb_b):
    if emb_a is None or emb_b is None:
        return
    sim = cosine_similarity(emb_a, emb_b)
    if sim is not None and not np.isnan(sim):
        target_list.append(sim)

for idx in random_indices:
    item = qa_pairs[idx]
    a_emb = safe_embed(item["answer"])
    random_chunk = extract_chunk(random.choice(metadata))
    ctx_emb = safe_embed(random_chunk)
    try_append_similarity(semantic_scores_random, a_emb, ctx_emb)

for idx in random_indices:
    item = qa_pairs[idx]
    q_emb = safe_embed(item["question"])
    random_chunk = extract_chunk(random.choice(metadata))
    ctx_emb = safe_embed(random_chunk)
    try_append_similarity(semantic_scores_cross, q_emb, ctx_emb)

baseline_random = float(np.mean(semantic_scores_random)) if len(semantic_scores_random) >= 10 else p10 * 0.5
baseline_cross = float(np.mean(semantic_scores_cross)) if len(semantic_scores_cross) >= 10 else p25 * 0.7
baseline_real = float(np.mean(semantic_scores))

semantic_fidelity_normalized = (
    (baseline_real - baseline_random) /
    (baseline_real - baseline_random + 1e-9)
) if baseline_real > baseline_random else 0.0

# =========================================================
# Umbral dinámico
# =========================================================

threshold_dynamic = p10

for idx, sim in enumerate(semantic_scores):
    if sim < threshold_dynamic:
        low_fidelity_indices.add(idx)

# =========================================================
# Limpieza opcional
# =========================================================

before_report = {
    "total_pairs": len(qa_pairs),
    "duplicate_questions": dup_questions,
    "duplicate_answers": dup_answers,
    "duplicate_pairs": dup_pairs,
    "noise_count": len(noise_indices),
    "short_answers": len(short_indices),
    "low_fidelity": len(low_fidelity_indices),
    "semantic_fidelity_raw": baseline_real,
    "semantic_fidelity_normalized": semantic_fidelity_normalized,
    "semantic_distribution": {
        "p10": p10,
        "p25": p25,
        "p50": p50,
        "p75": p75,
        "p90": p90,
        "std": std_sim
    },
    "semantic_histogram": hist.tolist(),
    "semantic_bins": bins.tolist(),
    "baseline_random": baseline_random,
    "baseline_crosslingual": baseline_cross,
    "threshold_dynamic": threshold_dynamic
}

if APPLY_FIX:
    logging.info("Applying automatic cleaning...")

    indices_to_remove = (
        duplicate_indices |
        noise_indices |
        short_indices |
        low_fidelity_indices
    )

    cleaned = []
    low_fidelity_items = []

    for idx, item in enumerate(qa_pairs):
        if idx in low_fidelity_indices:
            low_fidelity_items.append(item)
        elif idx not in indices_to_remove:
            cleaned.append(item)

    with open(CLEANED_QA_PATH, "w", encoding="utf-8") as f:
        for item in cleaned:
            f.write(json.dumps(item, ensure_ascii=False) + "\n")

    with open(LOW_FIDELITY_PATH, "w", encoding="utf-8") as f:
        for item in low_fidelity_items:
            f.write(json.dumps(item, ensure_ascii=False) + "\n")

    after_report = {
        "total_pairs": len(cleaned),
        "duplicate_questions": 0,
        "duplicate_answers": 0,
        "duplicate_pairs": 0,
        "noise_count": 0,
        "short_answers": 0,
        "low_fidelity": 0,
        "removed_pairs": len(indices_to_remove),
        "semantic_fidelity_raw": baseline_real,
        "semantic_fidelity_normalized": semantic_fidelity_normalized,
        "semantic_distribution": {
            "p10": p10,
            "p25": p25,
            "p50": p50,
            "p75": p75,
            "p90": p90,
            "std": std_sim
        },
        "semantic_histogram": hist.tolist(),
        "semantic_bins": bins.tolist(),
        "baseline_random": baseline_random,
        "baseline_crosslingual": baseline_cross,
        "threshold_dynamic": threshold_dynamic
    }

else:
    after_report = None

# =========================================================
# Guardar reporte final
# =========================================================

logging.info("Saving final report...")

final_report = {
    "before": before_report,
    "after": after_report,
    "cleaned_file": str(CLEANED_QA_PATH) if APPLY_FIX else None,
    "low_fidelity_file": str(LOW_FIDELITY_PATH) if APPLY_FIX else None
}

with open(REPORT_PATH, "w", encoding="utf-8") as f:
    json.dump(final_report, f, indent=4, ensure_ascii=False)

logging.info("Audit completed successfully.")
print("\n=== AUDIT COMPLETE ===")
print(f"Report saved to: {REPORT_PATH}")
print(f"Log saved to: {LOG_PATH}")
if APPLY_FIX:
    print(f"Clean dataset saved to: {CLEANED_QA_PATH}")
    print(f"Low-fidelity pairs saved to: {LOW_FIDELITY_PATH}")
