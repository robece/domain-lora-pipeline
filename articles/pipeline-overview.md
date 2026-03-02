[← Back to Home](../README.md)

## Table of Contents

- [7.1 End‑to‑End Pipeline Summary](#71-endtoend-pipeline-summary)

# 7. Pipeline Overview

The pipeline is organized as a deterministic, script‑driven workflow in
which each stage transforms the documentation into increasingly
structured, validated, and semantically enriched artifacts. Every script
has a single responsibility, a clearly defined input and output, and a
predictable role within the larger system. This modular design ensures
traceability, reproducibility, and full control over each transformation
step—from raw markdown ingestion to LoRA fine‑tuning. The following
table provides a complete and precise overview of the entire pipeline
exactly as implemented.

## 7.1 End‑to‑End Pipeline Summary

| **Step** | **Script**             | **Functional Objective**      | **Technical Description**                                                                                                                                 |
|----------|------------------------|-------------------------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------|
| **1**    | parse_toc.py           | Extract structured hierarchy  | Parses markdown files to identify headings, subheadings, and parent–child relationships. Produces section‑level structured content in markdown_sections/. |
| **2**    | clean_markdown.py      | Normalize content             | Removes noise, fixes formatting inconsistencies, standardizes markdown, and preserves semantic meaning. Outputs cleaned documents in clean_docs/.         |
| **3**    | build_clean_corpus.py  | Build clean corpus            | Converts cleaned documents into structured chunks, preserving section boundaries. Outputs chunked corpus in clean_chunks/.                                |
| **4**    | generate_embeddings.py | Semantic indexing             | Generates 3072‑dimensional embeddings using Azure OpenAI for each chunk. Saves embeddings.npy and embeddings_metadata.jsonl.                              |
| **5**    | check_faiss.py         | Validate FAISS index          | Builds and validates the FAISS index (faiss.index). Checks dimensional consistency and basic retrieval correctness.                                       |
| **6**    | retriever.py           | Retrieve relevant context     | Performs semantic search over the FAISS index to return the most relevant chunks for a given query.                                                       |
| **7**    | rag_query.py           | Simulate multi‑turn reasoning | Combines retrieved context with the query to simulate RAG‑style reasoning and multi‑step thought.                                                         |
| **8**    | generate_questions.py  | Generate technical questions  | Produces diverse, high‑quality questions grounded in retrieved context. Saves them to generated_questions.jsonl.                                          |
| **9**    | generate_answers.py    | Generate precise answers      | Uses GPT‑4o to produce accurate, well‑structured answers for each question. Saves initial QA pairs to qa_pairs.jsonl.                                     |
| **10**   | validate_question.py   | Validate QA pairs             | Ensures semantic fidelity, clarity, and consistency. Produces qa_pairs.cleaned.jsonl and flags low‑quality samples.                                       |
| **11**   | audit_dataset.py       | Audit dataset quality         | Detects duplicates, noise, contamination, and low‑fidelity examples. Outputs audit_report.json and contamination_report.jsonl.                            |
| **12**   | convert_to_instruct.py | Format for training           | Converts validated QA pairs into single‑turn instruct format. Saves qa_pairs.instruct.jsonl.                                                              |
| **13**   | train_lora.py          | Train LoRA adapter            | Fine‑tunes Qwen2.5‑3B‑Instruct using the instruct dataset. Produces LoRA weights in models/ and optionally pushes to Hugging Face.                        |

---
[← Back to Home](../README.md)
