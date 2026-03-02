import yaml
import logging
from pathlib import Path
from datetime import datetime
import json

# ---------------------------------------------------------
# Configuración general del proceso de parseo del TOC
# ---------------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent.parent
TOC_PATH = BASE_DIR / "data" / "toc.yml"
AZURE_DOCS_ROOT = BASE_DIR / "azure-docs" / "articles" / "event-grid"
OUTPUT_LIST = BASE_DIR / "data" / "eventgrid_files.json"
LOG_PATH = BASE_DIR / "logs" / "parse_toc.log"

LOG_PATH.parent.mkdir(parents=True, exist_ok=True)

# ---------------------------------------------------------
# Configuración del logger
# ---------------------------------------------------------

logging.basicConfig(
    filename=str(LOG_PATH),
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)

logging.info("=== START: Event Grid TOC Parsing ===")

# ---------------------------------------------------------
# Funciones auxiliares
# ---------------------------------------------------------

def load_toc(path: Path):
    """Load the toc.yml file."""
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

def flatten_toc_items(items, parent_path=None):
    """Convert the hierarchical TOC structure into a flat list."""
    flat = []
    parent_path = parent_path or []

    for item in items:
        title = item.get("name") or item.get("title")
        href = item.get("href")
        children = item.get("items") or item.get("children") or []

        current_path = parent_path + [title] if title else parent_path

        if href:
            flat.append({
                "title": title,
                "href": href,
                "toc_path": current_path,
            })

        if children:
            flat.extend(flatten_toc_items(children, current_path))

    return flat

def resolve_md_path(href: str) -> Path:
    """Resolve the real markdown file path inside the cloned repository."""
    return (AZURE_DOCS_ROOT / href).resolve()

# ---------------------------------------------------------
# Proceso principal de parseo del TOC
# ---------------------------------------------------------

try:
    toc = load_toc(TOC_PATH)
    flat_entries = flatten_toc_items(toc["items"])

    total_in_toc = len(flat_entries)
    logging.info(f"Articles listed in TOC: {total_in_toc}")

    processed_ok = 0
    processed_failed = 0
    missing_files = []
    resolved_entries = []

    for entry in flat_entries:
        href = entry["href"]
        md_path = resolve_md_path(href)

        if md_path.exists():
            processed_ok += 1
            logging.info(f"[OK] {href} → {md_path}")
            entry["resolved_path"] = str(md_path)
            resolved_entries.append(entry)
        else:
            processed_failed += 1
            missing_files.append(href)
            logging.error(f"[ERROR] File not found: {href}")

    # Guardar lista de archivos encontrados
    with open(OUTPUT_LIST, "w", encoding="utf-8") as f:
        json.dump(resolved_entries, f, indent=2, ensure_ascii=False)

    # Resumen final del proceso
    logging.info("=== SUMMARY ===")
    logging.info(f"Total in TOC: {total_in_toc}")
    logging.info(f"Found: {processed_ok}")
    logging.info(f"Missing: {processed_failed}")

    if missing_files:
        logging.info("Missing files:")
        for m in missing_files:
            logging.info(f" - {m}")

    logging.info("=== END OF PROCESS ===")

except Exception as e:
    logging.exception(f"Critical error during TOC parsing: {str(e)}")
