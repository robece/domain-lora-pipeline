from pathlib import Path

# ---------------------------------------------------------
# Configuración general del proceso de limpieza
# ---------------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent.parent

AUDIT_REPORT = BASE_DIR / "data" / "audit_report.json"
LOG_PATH = BASE_DIR / "logs" / "audit_dataset.log"
CLEANED_QA = BASE_DIR / "data" / "qa_pairs.cleaned.jsonl"
LOW_FIDELITY_QA = BASE_DIR / "data" / "qa_pairs.low_fidelity.jsonl"

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
    print("=== CLEANING AUDIT DATASET OUTPUTS ===")

    safe_delete(AUDIT_REPORT)
    safe_delete(LOG_PATH)
    safe_delete(CLEANED_QA)
    safe_delete(LOW_FIDELITY_QA)

    print("=== CLEANUP COMPLETE ===")

if __name__ == "__main__":
    main()
