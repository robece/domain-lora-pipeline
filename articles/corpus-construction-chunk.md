[← Back to Home](../README.md)

## Table of Contents

- [10.1 Purpose of This Stage](#101-purpose-of-this-stage)
- [10.2 How the Corpus Builder Works (build_clean_corpus.py)](#102-how-the-corpus-builder-works-buildcleancorpuspy)
- [10.3 Why This Stage Matters](#103-why-this-stage-matters)
- [10.4 Cleaning Previous Outputs (purge_build_clean_corpus.py)](#104-cleaning-previous-outputs-purgebuildcleancorpuspy)
- [10.5 Inputs and Outputs of This Stage](#105-inputs-and-outputs-of-this-stage)
- [10.6 Role of This Stage in the Pipeline](#106-role-of-this-stage-in-the-pipeline)

# 10. Corpus Construction and Chunk Filtering (build_clean_corpus.py + purge_build_clean_corpus.py)

This stage takes all the cleaned chunks produced earlier and turns them
into a single, unified corpus file that the rest of the pipeline will
use. It also performs basic quality checks to ensure that only
meaningful, usable chunks make it into the final dataset. The goal is to
consolidate everything into a clean, consistent, and contamination‑free
corpus that is ready for embeddings, retrieval, and QA generation.

## 10.1 Purpose of This Stage

The previous step produced many small chunk files—one per chunk of text.
This stage brings them together into a single JSONL corpus while
filtering out anything that could harm the quality of the dataset. It
ensures that:

- empty chunks are removed

- contaminated chunks are excluded

- each chunk receives a unique ID

- the final corpus is clean, consistent, and ready for semantic indexing

This is the first moment where the pipeline produces a **single, unified
dataset**.

## 10.2 How the Corpus Builder Works (build_clean_corpus.py)

The script processes every chunk file in clean_chunks/ and decides
whether it should be included in the final corpus.

**1. Load all chunk files**

It scans the clean_chunks/ directory and loads each JSON file one by
one.

**2. Skip empty chunks**

If a chunk has no text or only whitespace, it is ignored. This prevents
meaningless entries from polluting the corpus.

**3. Apply contamination filtering (optional but enabled)**

The script checks each chunk for two types of contamination:

- **Non‑Latin characters** (e.g., Chinese text)

- **Unwanted patterns** such as: “as an AI…”, “training data”, “please
  answer”, “summarize”, “respond in Chinese”, etc.

If a chunk contains any of these patterns, it is:

- excluded from the corpus

- logged as contaminated

- saved into a separate contamination_report.jsonl for review

This ensures that the corpus contains only clean, domain‑relevant
content.

**4. Assign a unique incremental ID**

Each accepted chunk receives a unique numeric ID. This ID becomes the
reference point for embeddings, retrieval, and QA generation.

**5. Write the chunk into the unified corpus**

Each valid chunk is written as one line in corpus_clean.jsonl,
containing:

- the unique ID

- the original chunk ID

- the source article

- the TOC path

- the cleaned text

This JSONL format is ideal for large‑scale processing.

**6. Log a complete summary**

At the end, the script prints and logs:

- total chunks written

- empty chunks skipped

- contaminated chunks skipped

- paths to the output files

This gives full visibility into the quality of the corpus.

## 10.3 Why This Stage Matters

This step ensures that the dataset is:

- **clean** — no noise, no garbage text

- **consistent** — all entries follow the same structure

- **traceable** — every chunk retains its origin

- **safe** — contamination is removed before training

- **ready for embeddings** — the next stage requires a unified corpus

Without this stage, the pipeline would be working with thousands of
small files, inconsistent quality, and potential contamination that
could degrade the model.

## 10.4 Cleaning Previous Outputs (purge_build_clean_corpus.py)

This companion script resets the outputs of the corpus‑building stage.

**What it removes**

- all cleaned documents in clean_docs/

- all chunk files in clean_chunks/

- the cleaning log file

**Why it’s useful**

It allows you to restart the cleaning and chunking process from scratch,
ensuring that no outdated or inconsistent files remain.

## 10.5 Inputs and Outputs of This Stage

**Inputs**

- all chunk files in data/clean_chunks/

- contamination filter rules (built into the script)

**Outputs**

- corpus_clean.jsonl — the unified, clean corpus

- contamination_report.jsonl — list of excluded chunks

- build_clean_corpus.log — detailed log of the process

## 10.6 Role of This Stage in the Pipeline

This stage is the bridge between raw text processing and semantic
indexing. It consolidates the entire dataset into a single, high‑quality
corpus that is ready for embedding generation. It also ensures that the
dataset is free from contamination and structural inconsistencies, which
is essential for producing reliable embeddings and high‑quality QA
pairs.

---
[← Back to Home](../README.md)
