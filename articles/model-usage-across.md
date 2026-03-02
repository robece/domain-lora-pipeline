[← Back to Home](../README.md)

## Table of Contents

- [24.1 Models involved in the pipeline](#241-models-involved-in-the-pipeline)
- [24.2 Where each model is used](#242-where-each-model-is-used)
- [24.3 Detailed model roles](#243-detailed-model-roles)
- [24.4 How models interact during inference](#244-how-models-interact-during-inference)
- [24.5 Why this model architecture works](#245-why-this-model-architecture-works)

# 24. Model Usage Across the Pipeline

The system relies on multiple models at different stages of the
pipeline. Each model serves a distinct purpose: document understanding,
embedding generation, semantic retrieval, dataset creation, and final
answer generation. This section documents exactly which models are used,
where they are used, and how they interact within the full architecture.

## 24.1 Models involved in the pipeline

The pipeline uses three model families:

- **Azure OpenAI embedding model**

- **Qwen2.5‑3B‑Instruct (base model)**

- **Qwen2.5‑3B‑LoRA adapter (fine‑tuned model)**

Each model plays a different role and appears in a different stage of
the system.

## 24.2 Where each model is used

The following table summarizes the usage of all models across the
pipeline:

| **Stage**                | **Model Used**                                  | **Purpose**                                             | **Location in System**                            |
|--------------------------|-------------------------------------------------|---------------------------------------------------------|---------------------------------------------------|
| Corpus cleaning          | No model                                        | Text normalization and chunking only.                   | Pipeline preprocessing scripts.                   |
| Embedding generation     | text-embedding-3-large (Azure OpenAI)           | Converts each chunk into a normalized vector for FAISS. | Pipeline embedding scripts and runtime retrieval. |
| FAISS index construction | No model                                        | Builds index from embeddings.                           | Pipeline FAISS scripts.                           |
| Dataset creation         | No model                                        | Converts cleaned corpus into Q&A pairs.                 | Pipeline dataset builder.                         |
| LoRA training            | Qwen2.5‑3B‑Instruct (base) + LoRA adapter       | Fine‑tunes the base model on domain‑specific Q&A pairs. | Pipeline training scripts.                        |
| Inference (RAG server)   | Qwen2.5‑3B‑Instruct + qwen2.5‑3b-lora-eventgrid | Generates grounded answers using retrieved context.     | /workspace/server.py inside the Docker container. |
| Retrieval (RAG server)   | text-embedding-3-large (Azure OpenAI)           | Embeds incoming questions for FAISS search.             | /workspace/server.py inside the Docker container. |

This table reflects the exact model usage in the current implementation.

## 24.3 Detailed model roles

**Azure OpenAI embedding model**

- Model: text-embedding-3-large

- Used in two places:

  - During pipeline execution to embed all documentation chunks.

  - During inference to embed incoming user questions.

- Produces normalized vectors compatible with FAISS inner‑product
  search.

- Determines retrieval quality and semantic alignment.

**Qwen2.5‑3B‑Instruct (base model)**

- Serves as the foundation for LoRA fine‑tuning.

- Loaded in BF16 on ROCm GPUs during:

  - LoRA training.

  - Inference inside the Docker container.

- Provides general reasoning and language capabilities.

**Qwen2.5‑3B LoRA adapter**

- Directory: /workspace/models/qwen2.5-3b-lora-eventgrid

- Contains the domain‑specific weights learned from the curated dataset.

- Applied on top of the base model at inference time.

- Injects Event Grid–specific knowledge into the generation process.

- Loaded dynamically using PEFT.

## 24.4 How models interact during inference

The inference pipeline uses two models in sequence:

1.  **Embedding model (Azure OpenAI)**

    1.  Converts the question into a vector.

    2.  FAISS retrieves the most relevant chunks.

2.  **Qwen2.5‑3B‑Instruct + LoRA adapter**

    1.  Receives the English grounding prompt containing the retrieved
        chunks.

    2.  Generates the final answer using only the provided context.

This separation ensures that retrieval and generation remain independent
and modular.

## 24.5 Why this model architecture works

- The embedding model specializes in semantic similarity, not
  generation.

- The Qwen base model specializes in reasoning and language.

- The LoRA adapter injects domain‑specific knowledge without retraining
  the full model.

- FAISS provides fast retrieval over large corpora.

- The RAG server orchestrates all components into a single deterministic
  pipeline.

This architecture balances performance, accuracy, and maintainability.

---
[← Back to Home](../README.md)
