[← Back to Home](../README.md)

## Table of Contents

- [15.1 Purpose of This Stage](#151-purpose-of-this-stage)
- [15.2 How the Question Generator Works (generate_questions.py)](#152-how-the-question-generator-works-generatequestionspy)
- [15.3 Why This Stage Matters](#153-why-this-stage-matters)
- [15.4 Cleaning Previous Outputs (purge_generate_questions.py)](#154-cleaning-previous-outputs-purgegeneratequestionspy)
- [15.5 Inputs and Outputs of This Stage](#155-inputs-and-outputs-of-this-stage)
- [15.6 Role of This Stage in the Pipeline](#156-role-of-this-stage-in-the-pipeline)

# 15. Technical Question Generation (generate_questions.py + purge_generate_questions.py)

This stage transforms the cleaned and reconstructed documentation into
high‑quality technical questions. It is the first half of the
dataset‑creation process: instead of answering questions, the system now
*creates* them. The goal is to generate diverse, precise, and
context‑grounded questions for every article in the corpus, ensuring
that the future LoRA model learns to reason about Azure Event Grid in a
detailed and domain‑accurate way.

## 15.1 Purpose of This Stage

The purpose of this stage is to take each full article reconstructed
from the corpus and generate a set of 20–40 technical questions that:

- are grounded strictly in the article’s content

- cover important concepts, configurations, and edge cases

- avoid hallucinations or invented details

- avoid trivial or generic questions

- avoid duplicates

- follow a consistent JSON format

These questions form the “Q” side of the QA dataset used later for
answer generation and LoRA training.

## 15.2 How the Question Generator Works (generate_questions.py)

The script performs several steps to reconstruct articles, build
prompts, call Azure OpenAI, and save the generated questions.

**1. Reconstruct full articles from chunks**

The corpus is stored as individual chunks, but question generation
requires full articles. The script:

- loads every entry from corpus_clean.jsonl

- groups chunks by their source_article

- extracts the text field from each chunk

- concatenates all chunks belonging to the same article

The result is a dictionary where each key is an article name and each
value is the full article text.

This ensures that the model sees the entire document, not isolated
fragments.

**2. Build a strict question‑generation prompt**

For each article, the script constructs a detailed prompt that instructs
the model to:

- generate 20–40 technical questions

- avoid inventing information

- avoid trivial or generic questions

- avoid duplicates

- avoid Chinese text

- avoid internal instructions

- return only a JSON object with a "questions" list

This strict prompt ensures consistency and prevents contamination.

**3. Call Azure OpenAI to generate questions**

The script uses the model gpt‑4o‑mini to generate the questions. For
each article:

- it sends the prompt

- receives a JSON object

- extracts the "questions" list

If the model returns malformed JSON or an unexpected structure, the
script logs the error and skips the article.

**4. Save each question to a JSONL file**

Each question is written as a separate line in
generated_questions.jsonl, containing:

- the article name

- the question text

This format is ideal for downstream processing.

**5. Skip very small articles**

If an article has fewer than 200 characters of content, the script skips
it. This prevents generating low‑quality or meaningless questions.

**6. Log progress and errors**

The script logs:

- how many articles were processed

- how many questions were generated per article

- any LLM or JSON parsing errors

This makes debugging and quality control easier.

## 15.3 Why This Stage Matters

This stage is essential because it creates the raw material for the QA
dataset. High‑quality questions lead to:

- better answer generation

- better training data

- a more capable LoRA model

If the questions are weak, generic, or hallucinated, the entire dataset
suffers. This script ensures that the questions are grounded, technical,
and aligned with the Azure Event Grid documentation.

## 15.4 Cleaning Previous Outputs (purge_generate_questions.py)

This companion script resets the outputs of the question‑generation
stage.

**What it removes**

- generated_questions.jsonl

- generate_questions.log

**Why it’s useful**

It allows you to regenerate the entire question set from scratch,
especially after:

- updating the corpus

- adjusting contamination filters

- modifying the prompt

- switching models

This keeps the dataset clean and reproducible.

## 15.5 Inputs and Outputs of This Stage

**Inputs**

- corpus_clean.jsonl — the unified clean corpus

- Azure OpenAI model (gpt‑4o‑mini)

- strict question‑generation prompt

**Outputs**

- generated_questions.jsonl — all generated questions

- generate_questions.log — detailed log of the process

## 15.6 Role of This Stage in the Pipeline

This stage is the first half of dataset creation. It transforms
documentation into structured questions that reflect the domain’s
complexity. These questions will be paired with grounded answers in the
next stage, forming the complete QA dataset used for LoRA training.

---
[← Back to Home](../README.md)
