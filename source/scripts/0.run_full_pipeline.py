import subprocess
import sys
from pathlib import Path

# ---------------------------------------------------------
# Configuración general del pipeline de ejecución
# ---------------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent

# Lista de scripts en el orden exacto en que deben ejecutarse.
# Cada entrada puede ser:
#   - "script.py" (sin parámetros)
#   - ("script.py", "--param1 --param2") (con parámetros)
SCRIPTS = [
    "1.parse_toc.py",
    "2.clean_markdown.py",
    "3.build_clean_corpus.py",
    "4.generate_embeddings.py",
    "5.check_faiss.py",
    "6.retriever.py",
    "7.rag_query.py",
    "8.generate_questions.py",
    "9.generate_answers.py",
#   "10.validate_question.py",
    ("11.audit_dataset.py", "--fix"),
    "12.convert_to_instruct.py",
    ("13.train_lora.py", "--push_to_hub")
]

# ---------------------------------------------------------
# Función para ejecutar un script individual
# ---------------------------------------------------------

def run_script(entry):
    """Execute a Python script with or without parameters."""

    # Caso 1: entrada simple → "script.py"
    if isinstance(entry, str):
        script_name = entry
        args = ""
    # Caso 2: entrada extendida → ("script.py", "--flags")
    else:
        script_name, args = entry

    script_path = BASE_DIR / script_name

    print(f"\n=== RUNNING: {script_name} {args} ===")

    if not script_path.exists():
        print(f"[ERROR] Script not found: {script_name}")
        sys.exit(1)

    # Construcción del comando
    cmd = [sys.executable, str(script_path)]
    if args:
        cmd.extend(args.split())

    # Ejecución con salida visible en tiempo real
    result = subprocess.run(
        cmd,
        stdout=sys.stdout,
        stderr=sys.stderr,
        text=True
    )

    # Si el script falla, detener el pipeline inmediatamente
    if result.returncode != 0:
        print(f"[ERROR] Script failed: {script_name}")
        sys.exit(result.returncode)

    print(f"=== COMPLETED: {script_name} ===\n")

# ---------------------------------------------------------
# Ejecución principal del pipeline
# ---------------------------------------------------------

def main():
    print("======================================")
    print("   EVENT GRID EXPERT FULL PIPELINE    ")
    print("======================================")

    for entry in SCRIPTS:
        run_script(entry)

    print("\n======================================")
    print("   PIPELINE COMPLETED SUCCESSFULLY    ")
    print("======================================")

if __name__ == "__main__":
    main()
