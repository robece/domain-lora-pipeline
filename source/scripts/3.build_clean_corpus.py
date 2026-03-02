import json
import logging
import re
from pathlib import Path

# ---------------------------------------------------------
# Configuración general del proceso de construcción del corpus
# ---------------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent.parent

CLEAN_CHUNKS_DIR = BASE_DIR / "data" / "clean_chunks"
OUTPUT_CORPUS = BASE_DIR / "data" / "corpus_clean.jsonl"
CONTAM_REPORT = BASE_DIR / "data" / "contamination_report.jsonl"
LOG_PATH = BASE_DIR / "logs" / "build_clean_corpus.log"

OUTPUT_CORPUS.parent.mkdir(parents=True, exist_ok=True)
LOG_PATH.parent.mkdir(parents=True, exist_ok=True)

# ---------------------------------------------------------
# Filtro de contaminación (opcional)
# ---------------------------------------------------------

ENABLE_CONTAMINATION_FILTER = True

NON_LATIN_REGEX = re.compile(r"[^\x00-\x7F]+")

BAD_PATTERNS = [
    r"下游任务", r"总结一下", r"根据提供的上下文",
    r"请根据", r"指令", r"训练", r"数据集",
    r"以下内容", r"回答下列问题",
    r"作为一个AI", r"作为一个模型",
    r"请用中文回答", r"请用英文回答",
]

def contains_bad_patterns(text: str) -> bool:
    for p in BAD_PATTERNS:
        if re.search(p, text):
            return True
    return False

def contains_non_latin(text: str) -> bool:
    return bool(NON_LATIN_REGEX.search(text))

# ---------------------------------------------------------
# Configuración del logger
# ---------------------------------------------------------

logging.basicConfig(
    filename=str(LOG_PATH),
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)

logging.info("=== START: Building Clean Corpus ===")
logging.info(f"Contamination filter enabled: {ENABLE_CONTAMINATION_FILTER}")

# ---------------------------------------------------------
# Funciones auxiliares
# ---------------------------------------------------------

def load_json(path: Path):
    """Load JSON content from file."""
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        logging.error(f"[ERROR] Could not load JSON {path}: {str(e)}")
        return None

def write_jsonl(path: Path, data: dict):
    """Append a JSON object to a JSONL file."""
    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(data, ensure_ascii=False) + "\n")

# ---------------------------------------------------------
# Proceso principal de construcción del corpus
# ---------------------------------------------------------

def main():
    if OUTPUT_CORPUS.exists():
        OUTPUT_CORPUS.unlink()
    if CONTAM_REPORT.exists():
        CONTAM_REPORT.unlink()

    chunk_files = list(CLEAN_CHUNKS_DIR.glob("*.json"))
    logging.info(f"Clean chunks found: {len(chunk_files)}")

    total_chunks = 0
    skipped_empty = 0
    skipped_contaminated = 0
    seen_ids = set()

    for idx, chunk_file in enumerate(chunk_files):
        data = load_json(chunk_file)
        if not data:
            continue

        text = data.get("text", "").strip()
        if not text:
            skipped_empty += 1
            logging.warning(f"[SKIPPED EMPTY] {chunk_file}")
            continue

        # Filtro de contaminación
        if ENABLE_CONTAMINATION_FILTER:
            has_non_latin = contains_non_latin(text)
            has_bad = contains_bad_patterns(text)

            if has_non_latin or has_bad:
                skipped_contaminated += 1

                contam_entry = {
                    "chunk_file": str(chunk_file),
                    "chunk_id": data.get("chunk_id"),
                    "source_article": data.get("source_article"),
                    "toc_path": data.get("toc_path"),
                    "text_excerpt": text[:300],
                    "non_latin": has_non_latin,
                    "bad_pattern": has_bad,
                }
                write_jsonl(CONTAM_REPORT, contam_entry)

                logging.warning(
                    f"[CONTAMINATED] {chunk_file} "
                    f"non_latin={has_non_latin} bad_pattern={has_bad}"
                )
                continue

        # ID incremental único
        corpus_id = idx

        if corpus_id in seen_ids:
            logging.error(f"[DUPLICATE ID] {corpus_id} in {chunk_file}")
            continue

        seen_ids.add(corpus_id)

        corpus_entry = {
            "id": corpus_id,
            "chunk_id": data.get("chunk_id"),
            "source_article": data.get("source_article"),
            "toc_path": data.get("toc_path"),
            "text": text,
        }

        write_jsonl(OUTPUT_CORPUS, corpus_entry)
        total_chunks += 1

    # Resumen final
    logging.info("=== FINAL SUMMARY ===")
    logging.info(f"Total chunks written: {total_chunks}")
    logging.info(f"Skipped empty chunks: {skipped_empty}")
    logging.info(f"Skipped contaminated chunks: {skipped_contaminated}")
    logging.info("=== END ===")

    print("=== BUILD CLEAN CORPUS REPORT ===")
    print(f"Total chunks written: {total_chunks}")
    print(f"Skipped empty chunks: {skipped_empty}")
    print(f"Skipped contaminated chunks: {skipped_contaminated}")
    print(f"Output file: {OUTPUT_CORPUS}")
    print(f"Contamination report: {CONTAM_REPORT}")

# ---------------------------------------------------------
# Entry point
# ---------------------------------------------------------

if __name__ == "__main__":
    main()
