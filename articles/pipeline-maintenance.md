[← Back to Home](../README.md)

## Table of Contents

- [23.1 When regeneration is required](#231-when-regeneration-is-required)
- [23.2 Order of regeneration](#232-order-of-regeneration)
- [23.3 Artifacts produced by each stage](#233-artifacts-produced-by-each-stage)
- [23.4 Partial vs. full regeneration](#234-partial-vs-full-regeneration)
- [23.5 Versioning and traceability](#235-versioning-and-traceability)
- [23.6 Deployment after regeneration](#236-deployment-after-regeneration)

# 23. Pipeline Maintenance and Regeneration

The pipeline supporting the RAG server is designed to be fully
reproducible. All artifacts—cleaned corpus, embeddings, FAISS index, and
the LoRA adapter—can be regenerated when documentation changes, when new
content is added, or when improved training data becomes available. This
section describes the exact maintenance workflow and the conditions
under which each component should be rebuilt.

## 23.1 When regeneration is required

Regeneration is necessary under the following conditions:

- New documentation is added to the source corpus.

- Existing documentation is updated or corrected.

- The cleaning rules or preprocessing logic change.

- Embedding model parameters or chunking strategy are modified.

- The FAISS index becomes outdated relative to the corpus.

- A new LoRA training run is desired based on improved datasets.

Each of these changes affects different stages of the pipeline and
determines which artifacts must be rebuilt.

## 23.2 Order of regeneration

The pipeline must be executed in a strict order to ensure consistency:

1.  **Corpus cleaning**

    1.  Raw documents are normalized, cleaned, and split into chunks.

    2.  Output: corpus_clean.jsonl.

2.  **Embedding generation**

    1.  Each chunk is embedded using Azure OpenAI.

    2.  Output: embeddings.npy and embeddings_metadata.jsonl.

3.  **FAISS index construction**

    1.  Embeddings are indexed using FAISS.

    2.  Output: faiss.index.

4.  **Dataset preparation for LoRA training**

    1.  Chunks are transformed into question–answer pairs.

    2.  Output: training dataset in JSONL format.

5.  **LoRA training**

    1.  The adapter is trained on the curated dataset.

    2.  Output: qwen2.5-3b-lora-eventgrid.

6.  **Deployment packaging**

    1.  The FAISS index, metadata, corpus, and LoRA adapter are copied
        into the Docker build context.

    2.  Output: a new inference container image.

Each stage depends on the outputs of the previous one, so skipping steps
leads to inconsistencies.

## 23.3 Artifacts produced by each stage

| **Stage**            | **Output**                                | **Purpose**                                       |
|----------------------|-------------------------------------------|---------------------------------------------------|
| Corpus cleaning      | corpus_clean.jsonl                        | Source text for retrieval and dataset generation. |
| Embedding generation | embeddings.npy, embeddings_metadata.jsonl | Vector representations aligned with FAISS.        |
| FAISS index          | faiss.index                               | High‑speed semantic search structure.             |
| Dataset creation     | Training JSONL                            | Input for LoRA fine‑tuning.                       |
| LoRA training        | qwen2.5-3b-lora-eventgrid/                | Domain‑adapted model weights.                     |
| Deployment packaging | Docker image                              | Final RAG server ready for production.            |

This table reflects the real artifacts used by the server.

## 23.4 Partial vs. full regeneration

Not all changes require a full rebuild. The following guidelines
determine the minimal required work:

- **Corpus changes only**

  - Rebuild embeddings

  - Rebuild FAISS index

  - No LoRA retraining required unless content meaning changes
    significantly.

- **Embedding model changes**

  - Rebuild embeddings

  - Rebuild FAISS index

  - LoRA training unaffected.

- **Chunking or cleaning rule changes**

  - Rebuild corpus

  - Rebuild embeddings

  - Rebuild FAISS index

  - Regenerate training dataset

  - Retrain LoRA adapter.

- **Dataset improvements**

  - Retrain LoRA adapter only.

- **Model architecture changes**

  - Full pipeline regeneration required.

This ensures minimal compute usage while maintaining consistency.

## 23.5 Versioning and traceability

Each regeneration cycle should produce:

- A new timestamped FAISS index

- A new metadata file

- A new cleaned corpus

- A new LoRA adapter directory

- A new Docker image tag

This allows the RAG server to be rolled back or compared across
versions.

## 23.6 Deployment after regeneration

Once all artifacts are rebuilt:

1.  The new FAISS index, metadata, corpus, and LoRA adapter are placed
    into the Docker build context.

2.  A new container image is built using the same Dockerfile.

3.  The running server is replaced with the new image.

4.  Logs continue to be written to the mounted /logs directory.

This ensures a clean, reproducible deployment cycle.

---
[← Back to Home](../README.md)
