[← Back to Home](../README.md)

## Table of Contents

- [22.1 Base image and GPU environment](#221-base-image-and-gpu-environment)
- [22.2 Installed dependencies](#222-installed-dependencies)
- [22.3 Filesystem layout inside the container](#223-filesystem-layout-inside-the-container)
- [22.4 Copying pipeline outputs into the image](#224-copying-pipeline-outputs-into-the-image)
- [22.5 Working directory and startup command](#225-working-directory-and-startup-command)
- [22.6 Startup sequence inside the container](#226-startup-sequence-inside-the-container)
- [22.7 Runtime behavior](#227-runtime-behavior)
- [22.8 Logging](#228-logging)
- [22.9 Networking](#229-networking)
- [22.10 Deployment summary](#2210-deployment-summary)

# 22. Deployment of the RAG + LoRA Server in Production (Docker‑based)

The production deployment is a GPU‑accelerated FastAPI server packaged
inside a Docker container built on a ROCm‑compatible PyTorch base image.
The container includes the LoRA adapter, the FAISS index, the cleaned
corpus, and the server code, forming a self‑contained inference
environment that mirrors the outputs of the full pipeline.

## 22.1 Base image and GPU environment

The deployment uses the following ROCm‑enabled PyTorch image:

Code

rocm/pytorch:rocm7.2_ubuntu24.04_py3.12_pytorch_release_2.9.1

This base image provides ROCm 7.2 GPU support, PyTorch compiled for AMD
GPUs, Python 3.12, and BF16 compute capability. These features allow the
Qwen2.5‑3B‑Instruct model and its LoRA adapter to run efficiently on AMD
hardware.

## 22.2 Installed dependencies

The Dockerfile installs only the libraries required for inference:

Code

pip install fastapi uvicorn transformers peft accelerate huggingface_hub
faiss-cpu openai numpy

These packages support API serving, model loading, LoRA application,
vector search, embedding generation, and numerical operations. No
training dependencies are included, keeping the image lightweight and
focused on inference.

## 22.3 Filesystem layout inside the container

The container organizes all runtime assets under /workspace. The
following table summarizes the structure and purpose of each directory
and file:

| **Path**                                     | **Type**                  | **Description**                                                         |
|----------------------------------------------|---------------------------|-------------------------------------------------------------------------|
| /workspace/server.py                         | File                      | FastAPI application implementing the RAG server.                        |
| /workspace/data/                             | Directory                 | Root folder for retrieval artifacts used by FAISS and the RAG pipeline. |
| /workspace/data/faiss.index                  | File                      | FAISS index containing vector embeddings for semantic search.           |
| /workspace/data/embeddings_metadata.jsonl    | File                      | Metadata aligned with FAISS index entries.                              |
| /workspace/data/corpus_clean.jsonl           | File                      | Cleaned text chunks used as retrieval context.                          |
| /workspace/models/                           | Directory                 | Storage location for model artifacts.                                   |
| /workspace/models/qwen2.5-3b-lora-eventgrid/ | Directory                 | LoRA adapter produced by the training pipeline.                         |
| /logs/requests.log                           | File (created at runtime) | Log file storing all incoming requests and generated responses.         |

This structure is static and defined at build time, ensuring that the
server can locate all required components without environment‑dependent
paths.

## 22.4 Copying pipeline outputs into the image

The Dockerfile copies the required artifacts from the build context:

Code

COPY api/temp/\* /workspace/data/  
COPY api/temp/models/ /workspace/models/

This embeds the FAISS index, metadata, cleaned corpus, and LoRA adapter
directly into the container image. No external downloads occur at
runtime except for the base model pulled from Hugging Face.

## 22.5 Working directory and startup command

The container sets:

Code

WORKDIR /workspace  
  
and launches the server with:

Code

CMD \["uvicorn", "server:app", "--host", "0.0.0.0", "--port", "8000"\]

This starts the FastAPI application defined in server.py and exposes it
on port 8000.

## 22.6 Startup sequence inside the container

When the container starts, the server performs the following steps:

1.  Loads the tokenizer from the base Qwen2.5‑3B‑Instruct model.

2.  Loads the base model in BF16 on the ROCm GPU.

3.  Loads the LoRA adapter from
    /workspace/models/qwen2.5-3b-lora-eventgrid.

4.  Initializes the Azure OpenAI client using environment variables:

    1.  AZURE_OPENAI_KEY

    2.  AZURE_OPENAI_ENDPOINT

5.  Loads the FAISS index from /workspace/data/faiss.index.

6.  Loads metadata from /workspace/data/embeddings_metadata.jsonl.

7.  Loads the cleaned corpus from /workspace/data/corpus_clean.jsonl.

8.  Initializes request logging to /logs/requests.log.

9.  Exposes the /generate and /health endpoints.

If any required file or environment variable is missing, the server
fails during startup.

## 22.7 Runtime behavior

Each request to /generate triggers the following sequence:

1.  Embedding generation using Azure OpenAI.

2.  FAISS search over the index stored in /workspace/data.

3.  Construction of an English grounding prompt.

4.  Answer generation using Qwen2.5‑3B‑Instruct with the LoRA adapter.

5.  Extraction of the final answer.

6.  Logging of the request and response.

7.  JSON response returned to the client.

This forms a deterministic retrieval‑augmented generation pipeline.

## 22.8 Logging

The server writes logs to:

Code

/logs/requests.log

Each entry includes timestamp, client IP, question, answer, top_k value,
and the full_response flag. If /logs is mounted as a volume, logs
persist across container restarts.

## 22.9 Networking

The container exposes:

Code

EXPOSE 8000

and binds to:

Code

0.0.0.0:8000

This allows integration with reverse proxies, Kubernetes services, or
VM‑level firewalls.

## 22.10 Deployment summary

The production deployment consists of a ROCm‑enabled Docker image
containing:

- a FastAPI server running inside /workspace/server.py

- a baked‑in FAISS index, metadata, corpus, and LoRA adapter

- Azure OpenAI embeddings for retrieval

- GPU‑accelerated inference using Qwen2.5‑3B‑Instruct with LoRA

- request logging to /logs/requests.log

- a single public API on port 8000

---
[← Back to Home](../README.md)
