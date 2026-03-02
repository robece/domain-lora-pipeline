from pathlib import Path

# ---------------------------------------------------------
# Configuración general del proceso de limpieza
# ---------------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent.parent

EMBEDDINGS_PATH = BASE_DIR / "data" / "embeddings.npy"
METADATA_PATH = BASE_DIR / "data" / "embeddings_metadata.jsonl"
FAISS_INDEX_PATH = BASE_DIR / "data" / "faiss.index"
LOG_PATH = BASE_DIR / "logs" / "generate_embeddings.log"

# ---------------------------------------------------------
# Funciones auxiliares de limpieza
# ---------------------------------------------------------

def safe_delete(path: Path):
    """Delete a file if it exists."""
    if path.exists():
        path.unlink()
        print(f"Deleted: {path}")
    else:
        print(f"Not found (skipped): {path}")

# ---------------------------------------------------------
# Ejecución principal del proceso de limpieza
# ---------------------------------------------------------

def main():
    print("=== CLEANING EMBEDDING GENERATION OUTPUTS ===")

    safe_delete(EMBEDDINGS_PATH)
    safe_delete(METADATA_PATH)
    safe_delete(FAISS_INDEX_PATH)
    safe_delete(LOG_PATH)

    print("=== CLEANUP COMPLETE ===")

if __name__ == "__main__":
    main()
