[← Back to Home](../README.md)

## Table of Contents

- [6.1 Processing and Training Environment (/scripts/docker-compose.yml)](#61-processing-and-training-environment-scriptsdocker-composeyml)
- [6.2 API Deployment Environment (/api/docker-compose.yml)](#62-api-deployment-environment-apidocker-composeyml)
- [6.3 Separation of Responsibilities](#63-separation-of-responsibilities)
- [6.4 Pre‑Execution Validation](#64-preexecution-validation)

# 6. Environment and Container Orchestration

The project uses two independent Docker Compose configurations, each
serving a distinct role in the workflow. This separation reflects the
real development and deployment process: one environment is dedicated to
data processing and model training, while the other is dedicated to
serving the trained model through an API. All environment variables are
defined explicitly inside each Compose file, and both environments have
direct access to the AMD GPU through ROCm.

## 6.1 Processing and Training Environment (/scripts/docker-compose.yml)

The Compose file located in the scripts/ directory provides the
execution environment for all pipeline operations and for LoRA
fine‑tuning. It defines two GPU‑enabled services:

**Ollama Service**

Used for local experimentation with ROCm‑accelerated models.

- Image: ollama/ollama:rocm

- GPU access via /dev/kfd and /dev/dri

- Exposes port 11434

- Stores model data in the ollama_data volume

**PyTorch ROCm Service**

This is the main workhorse of the pipeline. It runs:

- Markdown parsing

- Cleaning and normalization

- Chunking

- Embedding generation

- FAISS index construction

- Question and answer generation

- Dataset validation

- LoRA training

The service mounts the entire project directory into /workspace,
allowing all scripts to run inside the container.

It also defines all required environment variables directly in the
Compose file:

- AZURE_OPENAI_KEY

- AZURE_OPENAI_ENDPOINT

- AZURE_OPENAI_API_VERSION

- HF_TOKEN

No external configuration files or .env loaders are used.

This environment is used interactively during development and training.

## 6.2 API Deployment Environment (/api/docker-compose.yml)

The Compose file located in the api/ directory is dedicated exclusively
to serving the trained model through a FastAPI application. It defines a
single GPU‑enabled service:

**EventGrid API Service**

- Image: robece/eventgrid-api:1.0

- Built from the project’s API Dockerfile

- Exposes port 8000

- Mounts the API logs directory

- Has GPU access through /dev/kfd and /dev/dri

- Loads the base model and LoRA adapter at startup

The service includes the same Azure OpenAI and Hugging Face credentials,
defined explicitly in its environment: block.

This environment is used strictly for inference and external
consumption.

## 6.3 Separation of Responsibilities

The two Compose environments are intentionally independent:

- The **scripts Compose** handles preprocessing, embeddings, FAISS, QA
  generation, validation, and LoRA training.

- The **API Compose** handles model serving and inference.

There is no shared network, no cross‑Compose orchestration, and no
centralized configuration layer.

Both environments rely on explicit volume mounts and explicit
environment variables.

This design keeps the system simple, transparent, and easy to reproduce
on any machine with Docker and ROCm.

## 6.4 Pre‑Execution Validation

Before running the pipeline, a set of practical validation checks
ensures that the environment is correctly configured:  
  
**Directory validation**

The scripts verify or create:

- data/raw_docs/

- data/markdown_sections/

- data/clean_docs/

- data/clean_chunks/

- models/

- logs/

**Environment variable validation**

The pipeline checks that all required Azure OpenAI variables are present
in the container environment.

If any are missing, execution stops immediately.  
  
**Azure OpenAI connectivity**

A lightweight request confirms:

- the API key is valid

- the endpoint is reachable

- the selected models exist

**GPU availability (training and API)**

Both the training container and the API container verify:

- ROCm is available

- /dev/kfd and /dev/dri are accessible

- PyTorch ROCm can allocate GPU memory

**Embedding and FAISS consistency**

Before retrieval or QA generation:

- embeddings.npy must exist

- embeddings_metadata.jsonl must match in length

- faiss.index must be readable

These checks prevent runtime failures without adding unnecessary
complexity.

---
[← Back to Home](../README.md)
