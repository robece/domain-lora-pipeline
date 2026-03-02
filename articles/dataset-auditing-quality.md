[← Back to Home](../README.md)

## Table of Contents

- [18.1 Purpose of This Stage](#181-purpose-of-this-stage)
- [18.2 How the Audit Script Works (audit_dataset.py)](#182-how-the-audit-script-works-auditdatasetpy)
- [18.3 Why This Stage Matters](#183-why-this-stage-matters)
- [18.4 Cleaning Previous Outputs (purge_audit_dataset.py)](#184-cleaning-previous-outputs-purgeauditdatasetpy)
- [18.5 Inputs and Outputs of This Stage](#185-inputs-and-outputs-of-this-stage)
- [18.6 Role of This Stage in the Pipeline](#186-role-of-this-stage-in-the-pipeline)

# 18. Dataset Auditing and Quality Assurance (audit_dataset.py + purge_audit_dataset.py)

This stage performs a deep, multi‑layer audit of the entire QA dataset.
It is the most rigorous quality‑control step in the pipeline, combining
structural checks, duplication detection, noise filtering, semantic
fidelity scoring, statistical analysis, and optional automatic cleaning.
The goal is to ensure that the dataset used for LoRA training is clean,
consistent, and semantically aligned with the Azure Event Grid
documentation.

## 18.1 Purpose of This Stage

The audit step evaluates the QA dataset from multiple angles to detect:

- malformed or incomplete QA pairs

- duplicated questions, answers, or full pairs

- noise or contamination (e.g., Chinese text, internal instructions)

- extremely short or low‑quality answers

- answers that do not match the documentation (low semantic fidelity)

- distribution anomalies in answer lengths or semantic scores

It produces a detailed report and, if requested, automatically cleans
the dataset.

## 18.2 How the Audit Script Works (audit_dataset.py)

The script performs a series of structured audits, each targeting a
different dimension of dataset quality.

**1. Load the QA dataset and supporting files**

The script loads:

- all QA pairs

- the FAISS index

- the embedding vectors

- the metadata for each embedding

This gives the auditor full access to the semantic space used during
retrieval and answer generation.

**2. Structural validity check**

Each QA pair is inspected to ensure:

- it contains both a "question" and an "answer" field

- both fields are strings

Pairs missing fields or containing invalid types are flagged.

**3. Duplicate detection**

The script checks for:

- repeated questions

- repeated answers

- repeated (question, answer) pairs

Any duplicates are recorded, and their indices are marked for removal if
cleaning is enabled.

**4. Noise detection**

The script flags answers that contain:

- non‑Latin characters

- Chinese text

- internal instruction patterns

- other contamination markers

It also flags answers that are too short (fewer than 5 words).

**5. Length statistics**

The script computes:

- average answer length

- median length

- standard deviation

- distribution percentiles (p10, p25, p50, p75, p90)

- histogram of answer lengths

These metrics help identify outliers and dataset imbalance.

**6. Semantic fidelity scoring**

This is the most advanced part of the audit.

For each QA pair:

- the question is embedded

- the FAISS index retrieves the top‑3 relevant chunks

- the retrieved chunks are combined into a context

- the answer is embedded

- the script computes the cosine similarity between the answer and the
  retrieved context

A low similarity score indicates that the answer is not grounded in the
documentation.

The script also computes:

- random baseline similarity

- cross‑lingual baseline similarity

- normalized fidelity score

- dynamic threshold (p10 percentile)

Any answer below the threshold is marked as low‑fidelity.

**7. Calibration and baselines**

To avoid false positives, the script compares real semantic scores
against:

- random chunk similarities

- cross‑lingual similarities

This helps calibrate what “low fidelity” truly means.

**8. Automatic cleaning (optional)**

If the script is run with --fix, it removes:

- duplicates

- noisy answers

- extremely short answers

- low‑fidelity answers

It produces two files:

- qa_pairs.cleaned.jsonl — the cleaned dataset

- qa_pairs.low_fidelity.jsonl — removed low‑fidelity pairs for manual
  review

**9. Final audit report**

The script writes a comprehensive JSON report containing:

- before/after statistics

- contamination counts

- semantic fidelity metrics

- distribution histograms

- thresholds and baselines

- paths to cleaned files

This report becomes the authoritative record of dataset quality.

## 18.3 Why This Stage Matters

This stage ensures that the dataset used for LoRA training is:

- structurally correct

- free of duplicates

- free of noise

- semantically grounded

- statistically consistent

- traceable and auditable

A LoRA model trained on unfiltered data would learn hallucinations,
inconsistencies, and noise. A model trained on this audited dataset
learns clean, grounded, domain‑accurate behavior.

## 18.4 Cleaning Previous Outputs (purge_audit_dataset.py)

This companion script resets the outputs of the audit stage.

**What it removes**

- audit_report.json

- audit_dataset.log

- qa_pairs.cleaned.jsonl

- qa_pairs.low_fidelity.jsonl

**Why it’s useful**

It allows you to re‑run the audit from scratch after:

- regenerating QA pairs

- adjusting contamination rules

- modifying semantic thresholds

- updating the corpus or embeddings

This keeps the audit reproducible and clean.

## 18.5 Inputs and Outputs of This Stage

**Inputs**

- qa_pairs.jsonl — the full QA dataset

- FAISS index and embeddings

- metadata for each embedding

- Azure OpenAI embedding model

**Outputs**

- audit_report.json — full audit summary

- qa_pairs.cleaned.jsonl — cleaned dataset (if --fix is used)

- qa_pairs.low_fidelity.jsonl — removed low‑fidelity pairs

- audit_dataset.log — detailed log of the process

## 18.6 Role of This Stage in the Pipeline

This stage is the final quality gate before converting the dataset into
instruction format and training the LoRA model. It ensures that only
high‑quality, semantically aligned QA pairs move forward, protecting the
integrity of the final model.

---
[← Back to Home](../README.md)
