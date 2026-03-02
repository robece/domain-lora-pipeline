[← Back to Home](../README.md)

## Table of Contents

- [5.1 Folder-Level Organization](#51-folder-level-organization)
- [5.2 File-Level Organization in /data/](#52-file-level-organization-in-data)
- [5.3 Mapping Between Pipeline Steps and Artifacts](#53-mapping-between-pipeline-steps-and-artifacts)
- [5.5 Benefits of This Structure](#55-benefits-of-this-structure)

# 5. Directory Structure and Artifact Governance

A consistent and transparent directory structure is essential for
maintaining reproducibility, traceability, and clean separation of
responsibilities across the pipeline. The project organizes all
artifacts—raw documentation, cleaned content, corpus chunks, embeddings,
indexes, datasets, and model outputs—into a layout that mirrors the
actual flow of the system. These directories are mounted as shared
volumes across containers, ensuring that each stage of the pipeline
reads from and writes to predictable locations.

## 5.1 Folder-Level Organization

| **Folder**                  | **Contents**                      | **Role in the Pipeline**                  |
|-----------------------------|-----------------------------------|-------------------------------------------|
| **api/**                    | FastAPI server code               | Deployment of the LoRA model              |
| **data/**                   | Subfolders + generated artifacts  | Central data hub for the entire pipeline  |
| **data/raw_docs/**          | Original markdown files           | Entry point of the pipeline               |
| **data/markdown_sections/** | Extracted document sections       | Output of structural parsing (Step 1)     |
| **data/clean_docs/**        | Cleaned and normalized markdown   | Output of cleaning (Step 2)               |
| **data/clean_chunks/**      | Final corpus chunks               | Structured corpus for embeddings (Step 3) |
| **logs/**                   | Execution logs                    | Debugging and reproducibility             |
| **models/**                 | LoRA adapters and model artifacts | Output of training (Step 13)              |
| **notes/**                  | Project notes                     | Auxiliary documentation                   |
| **scripts/**                | Scripts for Steps 1–13            | Implementation of the full pipeline       |

## 5.2 File-Level Organization in /data/

| **File**                        | **Description**                             | **Pipeline Stage** |
|---------------------------------|---------------------------------------------|--------------------|
| **audit_report.json**           | Dataset audit summary                       | Step 11            |
| **contamination_report.jsonl**  | Cross-contamination detection               | Step 11            |
| **embeddings.npy**              | Embedding matrix                            | Step 4             |
| **embeddings_metadata.jsonl**   | Metadata for each embedded chunk            | Step 4             |
| **eventgrid_files.json**        | Inventory of processed files                | Preprocessing      |
| **faiss.index**                 | FAISS semantic index                        | Step 5             |
| **generated_questions.jsonl**   | Generated questions                         | Step 8             |
| **qa_pairs.jsonl**              | Initial QA pairs                            | Step 9             |
| **qa_pairs.cleaned.jsonl**      | Validated QA pairs                          | Step 10            |
| **qa_pairs_low_fidelity.jsonl** | Low-quality samples flagged during auditing | Step 11            |
| **qa_pairs.instruct.jsonl**     | Final instruction-formatted dataset         | Step 12            |

## 5.3 Mapping Between Pipeline Steps and Artifacts

| **Pipeline Step** | **Related Folder / File**                                                  | **Description**            |
|-------------------|----------------------------------------------------------------------------|----------------------------|
| **1**             | markdown_sections/                                                         | Structural extraction      |
| **2**             | clean_docs/                                                                | Cleaning and normalization |
| **3**             | clean_chunks/                                                              | Corpus construction        |
| **4**             | embeddings.npy, embeddings_metadata.jsonl                                  | Embedding generation       |
| **5**             | faiss.index                                                                | Index validation           |
| **6–7**           | clean_chunks/, faiss.index                                                 | Retrieval + RAG reasoning  |
| **8**             | generated_questions.jsonl                                                  | Question generation        |
| **9**             | qa_pairs.jsonl                                                             | Answer generation          |
| **10**            | qa_pairs.cleaned.jsonl                                                     | QA validation              |
| **11**            | qa_pairs_low_fidelity.jsonl, audit_report.json, contamination_report.jsonl | Dataset auditing           |
| **12**            | qa_pairs.instruct.jsonl                                                    | Instruction formatting     |
| **13**            | models/                                                                    | LoRA training              |

## 5.5 Benefits of This Structure

This directory layout provides:

- **Deterministic execution** — each stage reads from and writes to a
  fixed location.

- **Auditability** — every transformation leaves a traceable artifact.

- **Modularity** — individual steps can be rerun without affecting
  others.

- **Portability** — the entire project can be moved or containerized
  without breaking paths.

- **Scalability** — new components (evaluation, monitoring, multi‑model
  training) can be added without restructuring.

---
[← Back to Home](../README.md)
