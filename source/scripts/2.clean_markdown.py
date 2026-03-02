import json
import logging
import re
from pathlib import Path
from bs4 import BeautifulSoup
from markdown_it import MarkdownIt

# ---------------------------------------------------------
# Configuración general del proceso de limpieza de Markdown
# ---------------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent.parent

FILES_LIST = BASE_DIR / "data" / "eventgrid_files.json"
CLEAN_DOCS_DIR = BASE_DIR / "data" / "clean_docs"
CHUNKS_DIR = BASE_DIR / "data" / "clean_chunks"

LOG_PATH = BASE_DIR / "logs" / "clean_markdown.log"

CLEAN_DOCS_DIR.mkdir(parents=True, exist_ok=True)
CHUNKS_DIR.mkdir(parents=True, exist_ok=True)
LOG_PATH.parent.mkdir(parents=True, exist_ok=True)

# ---------------------------------------------------------
# Configuración del logger
# ---------------------------------------------------------

logging.basicConfig(
    filename=str(LOG_PATH),
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)

logging.info("=== START: Clean Markdown Processing ===")

# ---------------------------------------------------------
# Funciones auxiliares
# ---------------------------------------------------------

def load_markdown(path: Path) -> str:
    """Load raw markdown content from file."""
    with open(path, "r", encoding="utf-8") as f:
        return f.read()

def remove_front_matter(md: str) -> str:
    """Remove YAML front matter if present."""
    if md.startswith("---"):
        parts = md.split("---", 2)
        if len(parts) >= 3:
            return parts[2].strip()
    return md

def markdown_to_html(md: str) -> str:
    """Convert markdown to HTML using markdown-it."""
    md_parser = MarkdownIt()
    return md_parser.render(md)

def html_to_text(html: str) -> str:
    """Convert HTML to clean plain text."""
    soup = BeautifulSoup(html, "html.parser")

    # Remove code blocks, images, scripts, styles
    for tag in soup(["code", "pre", "img", "script", "style"]):
        tag.decompose()

    # Remove admonition blocks (NOTE, WARNING, etc.)
    for div in soup.find_all("div", class_=re.compile("admonition")):
        div.decompose()

    text = soup.get_text(separator="\n")
    return text

def normalize_text(text: str) -> str:
    """Normalize whitespace, line breaks, and noise."""
    text = re.sub(r"\n{2,}", "\n", text)
    text = re.sub(r"[ \t]+", " ", text)
    return text.strip()

def split_into_chunks(text: str, max_chars=1200):
    """Split text into semantic chunks without breaking sentences."""
    paragraphs = [p.strip() for p in text.split("\n") if p.strip()]
    chunks = []
    buf = ""

    for p in paragraphs:
        if len(buf) + len(p) < max_chars:
            buf += p + "\n"
        else:
            chunks.append(buf.strip())
            buf = p + "\n"

    if buf.strip():
        chunks.append(buf.strip())

    return chunks

# ---------------------------------------------------------
# Proceso principal de limpieza y chunking
# ---------------------------------------------------------

try:
    with open(FILES_LIST, "r", encoding="utf-8") as f:
        entries = json.load(f)

    total_files = len(entries)
    processed_ok = 0
    processed_failed = 0
    total_chunks = 0

    logging.info(f"Files to process: {total_files}")

    for entry in entries:
        try:
            md_path = Path(entry["resolved_path"])
            md_text = load_markdown(md_path)

            # 1. Remove front matter
            md_text = remove_front_matter(md_text)

            # 2. Markdown → HTML
            html = markdown_to_html(md_text)

            # 3. HTML → plain text
            clean_text = html_to_text(html)

            # 4. Normalize text
            clean_text = normalize_text(clean_text)

            # 5. Save full cleaned document
            clean_doc = {
                "title": entry.get("title"),
                "href": entry.get("href"),
                "toc_path": entry.get("toc_path"),
                "source_path": entry.get("resolved_path"),
                "clean_text": clean_text,
            }

            clean_doc_path = CLEAN_DOCS_DIR / f"{md_path.stem}.json"
            with open(clean_doc_path, "w", encoding="utf-8") as f_out:
                json.dump(clean_doc, f_out, indent=2, ensure_ascii=False)

            # 6. Semantic chunking
            chunks = split_into_chunks(clean_text)
            total_chunks += len(chunks)

            for idx, chunk in enumerate(chunks, start=1):
                chunk_output = {
                    "source_article": entry.get("href"),
                    "toc_path": entry.get("toc_path"),
                    "chunk_id": f"{md_path.stem}_chunk_{idx}",
                    "text": chunk,
                }

                out_file = CHUNKS_DIR / f"{md_path.stem}_chunk_{idx}.json"
                with open(out_file, "w", encoding="utf-8") as f_out:
                    json.dump(chunk_output, f_out, indent=2, ensure_ascii=False)

            processed_ok += 1
            logging.info(f"[OK] {entry['href']} → {len(chunks)} chunks")

        except Exception as e:
            processed_failed += 1
            logging.error(f"[ERROR] {entry.get('href')} - {str(e)}")

    logging.info("=== SUMMARY ===")
    logging.info(f"Total files: {total_files}")
    logging.info(f"Processed OK: {processed_ok}")
    logging.info(f"Failed: {processed_failed}")
    logging.info(f"Total chunks generated: {total_chunks}")
    logging.info("=== END OF PROCESS ===")

except Exception as e:
    logging.exception(f"Critical error during markdown cleaning: {str(e)}")
