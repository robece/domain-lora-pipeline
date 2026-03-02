from pathlib import Path

# ---------------------------------------------------------
# Configuración general del proceso de limpieza
# ---------------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent.parent
LOG_PATH = BASE_DIR / "logs" / "retriever.log"

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
    print("=== CLEANING RETRIEVER OUTPUTS ===")

    safe_delete(LOG_PATH)

    print("=== CLEANUP COMPLETE ===")

if __name__ == "__main__":
    main()
