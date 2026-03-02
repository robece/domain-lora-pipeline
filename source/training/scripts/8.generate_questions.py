import json
import time
from pathlib import Path
import logging
import os
from openai import AzureOpenAI
from tqdm import tqdm

# ---------------------------------------------------------
# Configuración general del generador de preguntas
# ---------------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent.parent

CORPUS_PATH = BASE_DIR / "data" / "corpus_clean.jsonl"
OUTPUT_PATH = BASE_DIR / "data" / "generated_questions.jsonl"
LOG_PATH = BASE_DIR / "logs" / "generate_questions.log"

LOG_PATH.parent.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    filename=str(LOG_PATH),
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

logging.info("=== START: Question Generation Script ===")

# ---------------------------------------------------------
# Cliente Azure OpenAI
# ---------------------------------------------------------

client = AzureOpenAI(
    api_key=os.getenv("AZURE_OPENAI_KEY"),
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
    api_version=os.getenv("AZURE_OPENAI_API_VERSION")
)

LLM_MODEL = "gpt-4o-mini"

# ---------------------------------------------------------
# Carga del corpus y reconstrucción de artículos completos
# ---------------------------------------------------------

def extract_chunk(entry):
    """Extract the text field from a corpus entry using multiple fallback keys."""
    possible_keys = ["content", "text", "chunk", "body", "content_text", "raw"]
    for key in possible_keys:
        if key in entry:
            return entry[key]
    return None

articles = {}

with open(CORPUS_PATH, "r", encoding="utf-8") as f:
    for line in f:
        item = json.loads(line)

        article = item["source_article"]
        chunk_text = extract_chunk(item)

        if chunk_text is None:
            logging.error(f"[CORPUS_ERROR] No valid text field found in entry: {item}")
            continue

        articles.setdefault(article, []).append(chunk_text)

# Merge chunks into full article text
for article in articles:
    articles[article] = "\n".join(articles[article]).strip()

logging.info(f"Articles reconstructed: {len(articles)}")

# ---------------------------------------------------------
# Prompt estricto para generación de preguntas
# ---------------------------------------------------------

def build_prompt(article_name, text):
    return f"""
You are an expert technical question generator.

Generate between 20 and 40 high‑quality, technical, precise questions strictly based on the following article content.

Rules:
- Do NOT invent anything not present in the text.
- Cover all important concepts, edge cases, configurations, limitations, and examples.
- Questions must be specific, not generic.
- No answers, only questions.
- No duplicates.
- No trivial questions.
- No Chinese text.
- No internal instructions.

ARTICLE NAME:
{article_name}

ARTICLE CONTENT:
\"\"\"
{text}
\"\"\"

Return ONLY a JSON object with a single field "questions", where the value is a JSON list of strings.
"""

# ---------------------------------------------------------
# Llamada al modelo Azure OpenAI
# ---------------------------------------------------------

def call_llm(prompt: str):
    response = client.chat.completions.create(
        model=LLM_MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.2,
        response_format={"type": "json_object"}
    )
    return response.choices[0].message.content

# ---------------------------------------------------------
# Proceso principal
# ---------------------------------------------------------

def main():
    fout = open(OUTPUT_PATH, "a", encoding="utf-8")

    for article, full_text in tqdm(articles.items(), desc="Generating questions"):

        if len(full_text) < 200:
            logging.info(f"[SKIPPED] Article too small: {article}")
            continue

        prompt = build_prompt(article, full_text)

        try:
            result = call_llm(prompt)
        except Exception as e:
            logging.error(f"[LLM_ERROR] article={article} error={e}")
            continue

        try:
            data = json.loads(result)
            questions = data.get("questions") or data.get("items") or data
        except Exception as e:
            logging.error(f"[JSON_PARSE_ERROR] article={article} error={e}")
            continue

        if not isinstance(questions, list):
            logging.error(f"[INVALID_FORMAT] article={article} result={result}")
            continue

        for q in questions:
            fout.write(json.dumps({
                "article": article,
                "question": q
            }, ensure_ascii=False) + "\n")

        logging.info(f"[OK] {article} → {len(questions)} questions")

        time.sleep(0.15)

    fout.close()
    logging.info("=== END OF QUESTION GENERATION ===")
    print("Questions generated successfully.")

if __name__ == "__main__":
    main()
