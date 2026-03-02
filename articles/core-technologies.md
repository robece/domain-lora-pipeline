[← Back to Home](../README.md)

## Table of Contents

- [3.1 Azure OpenAI for Embeddings and Reasoning](#31-azure-openai-for-embeddings-and-reasoning)
- [3.2 FAISS for Vector Indexing and Similarity Search](#32-faiss-for-vector-indexing-and-similarity-search)
- [3.3 Hugging Face Ecosystem for LoRA Fine‑Tuning](#33-hugging-face-ecosystem-for-lora-finetuning)
- [3.4 FastAPI and Uvicorn for Model Deployment](#34-fastapi-and-uvicorn-for-model-deployment)

# 3. Core Technologies Underpinning the Pipeline

The provisioning layer is built around a small set of foundational
technologies that enable the pipeline to operate efficiently across
preprocessing, semantic indexing, retrieval‑augmented reasoning, and
LoRA fine‑tuning. Rather than relying on a large or fragmented
dependency stack, the system focuses on a few strategically chosen
components that provide robustness, scalability, and clarity of purpose.
Each technology plays a distinct role in the architecture and directly
supports one or more stages of the pipeline.

## 3.1 Azure OpenAI for Embeddings and Reasoning

Azure OpenAI serves as the computational backbone for all embedding and
reasoning tasks. It provides two essential capabilities:

- High‑dimensional embeddings used to construct the semantic index.

- Generative reasoning used in RAG queries, question generation, and
  answer generation.

By delegating these tasks to cloud‑grade models, the pipeline avoids the
need to host large embedding or generative models locally. This reduces
hardware requirements, improves consistency across runs, and ensures
that embedding quality remains stable over time.

## 3.2 FAISS for Vector Indexing and Similarity Search

FAISS is responsible for building and querying the semantic index. It
enables:

- Fast similarity search across thousands of document chunks.

- Deterministic indexing behavior suitable for reproducible experiments.

- CPU‑friendly performance that integrates cleanly with containerized
  environments.

FAISS is installed directly inside the main Python environment rather
than through a specialized image, keeping the system lightweight and
easy to maintain.

## 3.3 Hugging Face Ecosystem for LoRA Fine‑Tuning

The training stage relies on a set of tightly integrated components from
the Hugging Face ecosystem:

- **Transformers** for model loading and tokenization.

- **TRL** for supervised fine‑tuning workflows.

- **PEFT** for efficient LoRA adapters.

- **Accelerate** for optimized training on AMD GPUs.

- **Hugging Face Hub** for storing the final LoRA adapter privately.

These tools collectively enable parameter‑efficient training without
requiring full‑model fine‑tuning, making the process accessible even on
consumer‑grade hardware.

## 3.4 FastAPI and Uvicorn for Model Deployment

Once the LoRA adapter is trained, it is deployed through a lightweight
Python‑based container running FastAPI and Uvicorn. This service:

- Loads the base model and LoRA weights at startup.

- Exposes a clean HTTP interface for inference.

- Operates independently from the training and preprocessing
  environments.

This separation ensures that the deployment layer remains minimal,
stable, and easy to scale or replicate.

---
[← Back to Home](../README.md)
