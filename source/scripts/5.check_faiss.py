import json
import faiss
import numpy as np
from pathlib import Path

# ---------------------------------------------------------
# Configuración general del proceso de validación FAISS
# ---------------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent.parent

INDEX_PATH = BASE_DIR / "data" / "faiss.index"
METADATA_PATH = BASE_DIR / "data" / "embeddings_metadata.jsonl"

print("=== FAISS INDEX CHECK ===")

# ---------------------------------------------------------
# Cargar índice FAISS
# ---------------------------------------------------------

if not INDEX_PATH.exists():
    raise FileNotFoundError(f"FAISS index not found at {INDEX_PATH}")

index = faiss.read_index(str(INDEX_PATH))

print(f"Index type: {type(index)}")
print(f"Vector dimension: {index.d}")
print(f"Total vectors in FAISS: {index.ntotal}")

# ---------------------------------------------------------
# Contar líneas de metadata
# ---------------------------------------------------------

if not METADATA_PATH.exists():
    raise FileNotFoundError(f"Metadata file not found at {METADATA_PATH}")

with open(METADATA_PATH, "r", encoding="utf-8") as f:
    metadata_lines = sum(1 for _ in f)

print(f"Metadata lines: {metadata_lines}")

# ---------------------------------------------------------
# Validar alineación FAISS ↔ metadata
# ---------------------------------------------------------

if metadata_lines == index.ntotal:
    print("✔ FAISS and metadata are ALIGNED")
else:
    print("❌ MISALIGNMENT: FAISS vector count differs from metadata")

# ---------------------------------------------------------
# Validar IDs consecutivos en metadata
# ---------------------------------------------------------

print("\n=== VALIDATING IDs ===")
ids = []

with open(METADATA_PATH, "r", encoding="utf-8") as f:
    for line in f:
        item = json.loads(line)
        ids.append(item.get("id"))

if ids == list(range(len(ids))):
    print("✔ IDs are consecutive and correct")
else:
    print("❌ IDs are NOT consecutive or are corrupted")

# ---------------------------------------------------------
# Mostrar muestra de metadata
# ---------------------------------------------------------

print("\n=== SAMPLE METADATA ===")
with open(METADATA_PATH, "r", encoding="utf-8") as f:
    for i, line in enumerate(f):
        print(line.strip())
        if i >= 3:
            break

# ---------------------------------------------------------
# Probar búsqueda dummy
# ---------------------------------------------------------

print("\n=== SEARCH TEST ===")

dummy = np.random.rand(1, index.d).astype("float32")
dummy /= np.linalg.norm(dummy)

D, I = index.search(dummy, 5)

print("Returned IDs:", I[0])
print("Scores:", D[0])
