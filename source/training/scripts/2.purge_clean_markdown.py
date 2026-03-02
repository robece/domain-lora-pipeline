import shutil
from pathlib import Path

# ---------------------------------------------------------
# Configuración general del proceso de limpieza
# ---------------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent.parent

CLEAN_DOCS_DIR = BASE_DIR / "data" / "clean_docs"
CLEAN_CHUNKS_DIR = BASE_DIR / "data" / "clean_chunks"
LOG_PATH = BASE_DIR / "logs" / "clean_markdown.log"

# ---------------------------------------------------------
# Funciones auxiliares de limpieza
# ---------------------------------------------------------

def clean_directory(path: Path):
    """Delete all files inside a directory."""
    if path.exists():
        for file in path.iterdir():
            if file.is_file():
                file.unlink()
        print(f"Cleaned directory: {path}")
    else:
        print(f"Directory not found (skipped): {path}")

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
    print("=== CLEANING CLEAN-MARKDOWN OUTPUTS ===")

    clean_directory(CLEAN_DOCS_DIR)
    clean_directory(CLEAN_CHUNKS_DIR)
    safe_delete(LOG_PATH)

    print("=== CLEANUP COMPLETE ===")

if __name__ == "__main__":
    main()
