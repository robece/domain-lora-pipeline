import subprocess
import sys
from pathlib import Path

# ---------------------------------------------------------
# Configuración general del pipeline de limpieza
# ---------------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent

# Lista de cleaners en el orden exacto en que deben ejecutarse
CLEANERS = [
    "1.purge_parse_toc.py",
    "2.purge_clean_markdown.py",
    "3.purge_build_clean_corpus.py",
    "4.purge_generate_embeddings.py",
    "6.purge_retriever.py",
    "7.purge_rag_query.py",
    "8.purge_generate_questions.py",
    "9.purge_generate_answers.py",
    "10.purge_validate_question.py",
    "11.purge_audit_dataset.py",
    "12.purge_convert_to_instruct.py",
    "13.purge_train_lora.py"
]

# ---------------------------------------------------------
# Función para ejecutar cada cleaner individualmente
# ---------------------------------------------------------

def run_cleaner(script_name):
    """Execute a cleaner script and stop the pipeline if it fails."""
    script_path = BASE_DIR / script_name

    print(f"\n=== RUNNING CLEANER: {script_name} ===")

    if not script_path.exists():
        print(f"[ERROR] Cleaner not found: {script_name}")
        sys.exit(1)

    result = subprocess.run(
        [sys.executable, str(script_path)],
        capture_output=True,
        text=True
    )

    # Mostrar salida estándar del cleaner
    print(result.stdout)

    # Si el cleaner falla, detener el pipeline inmediatamente
    if result.returncode != 0:
        print(f"[ERROR] Cleaner failed: {script_name}")
        print(result.stderr)
        sys.exit(result.returncode)

    print(f"=== COMPLETED CLEANER: {script_name} ===\n")

# ---------------------------------------------------------
# Ejecución principal del pipeline de limpieza
# ---------------------------------------------------------

def main():
    print("======================================")
    print("   FULL CLEANUP OF EVENT GRID PIPELINE")
    print("======================================")

    for cleaner in CLEANERS:
        run_cleaner(cleaner)

    print("\n======================================")
    print("   ALL CLEANERS EXECUTED SUCCESSFULLY ")
    print("======================================")

if __name__ == "__main__":
    main()
