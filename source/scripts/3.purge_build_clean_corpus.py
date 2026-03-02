from pathlib import Path

# ---------------------------------------------------------
# Configuración general del proceso de limpieza
# ---------------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent.parent

OUTPUT_CORPUS = BASE_DIR / "data" / "corpus_clean.jsonl"
CONTAM_REPORT = BASE_DIR / "data" / "contamination_report.jsonl"
LOG_PATH = BASE_DIR / "logs" / "build_clean_corpus.log"

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
    print("=== CLEANING BUILD CLEAN CORPUS OUTPUTS ===")

    safe_delete(OUTPUT_CORPUS)
    safe_delete(CONTAM_REPORT)
    safe_delete(LOG_PATH)

    print("=== CLEANUP COMPLETE ===")

if __name__ == "__main__":
    main()
