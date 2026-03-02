import json
from pathlib import Path
import logging

# ---------------------------------------------------------
# Configuración general del proceso de conversión
# ---------------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent.parent

CLEANED_QA_PATH = BASE_DIR / "data" / "qa_pairs.cleaned.jsonl"
INSTRUCT_PATH = BASE_DIR / "data" / "qa_pairs.instruct.jsonl"
LOG_PATH = BASE_DIR / "logs" / "convert_to_instruct.log"

LOG_PATH.parent.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    filename=str(LOG_PATH),
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)

# ---------------------------------------------------------
# Carga del dataset limpio
# ---------------------------------------------------------

print("Loading cleaned dataset...")
logging.info("Loading cleaned dataset...")

qa_pairs = []
with open(CLEANED_QA_PATH, "r", encoding="utf-8") as f:
    for line in f:
        try:
            qa_pairs.append(json.loads(line))
        except Exception as e:
            logging.error(f"Error reading line: {e}")

print(f"Total pairs loaded: {len(qa_pairs)}")
logging.info(f"Total pairs loaded: {len(qa_pairs)}")

# ---------------------------------------------------------
# Conversión al formato instruct
# ---------------------------------------------------------

print("Converting to instruct format...")
logging.info("Converting to instruct format...")

with open(INSTRUCT_PATH, "w", encoding="utf-8") as out_f:
    for item in qa_pairs:
        q = item.get("question", "").strip()
        a = item.get("answer", "").strip()

        if not q or not a:
            logging.warning("Invalid pair detected and skipped.")
            continue

        instruct_item = {
            "instruction": q,
            "input": "",
            "output": a
        }

        out_f.write(json.dumps(instruct_item, ensure_ascii=False) + "\n")

print(f"Conversion complete. File saved to: {INSTRUCT_PATH}")
logging.info(f"Instruct file saved to: {INSTRUCT_PATH}")

print("\n=== CONVERSION COMPLETE ===")
print(f"Log saved to: {LOG_PATH}")
