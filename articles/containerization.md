[← Back to Home](../README.md)

## Table of Contents

- [2.1 Base Images and Their Roles](#21-base-images-and-their-roles)
- [2.2 Multi‑Container Orchestration with Docker Compose](#22-multicontainer-orchestration-with-docker-compose)

# 2. Containerization as the Execution Backbone

Docker and Docker Compose provide the foundation for reproducibility and
portability. Every stage of the pipeline—from markdown parsing to LoRA
training—runs inside containers with pinned versions of runtimes and
dependencies.

## 2.1 Base Images and Their Roles

The pipeline relies on a small set of Python‑based container images,
each tailored to a specific stage of the workflow. Instead of using
specialized or pre‑built images, the environment is constructed from
lightweight Python bases, with the required components installed
directly inside each container. This approach keeps the system portable,
transparent, and easy to reproduce.

- **Python 3.10 Slim** Serves as the foundation for preprocessing,
  corpus cleaning, embedding generation, FAISS indexing, and all
  CPU‑bound tasks. FAISS, markdown parsers, and supporting utilities are
  installed directly into this environment.

- **ROCm‑enabled PyTorch image (AMD GPU)** Used exclusively for LoRA
  training on local AMD hardware. This image provides PyTorch compiled
  for ROCm, enabling efficient fine‑tuning on the RX 7900 XTX without
  relying on NVIDIA CUDA.

- **Python‑based FastAPI container** A lightweight Python image extended
  with FastAPI and Uvicorn to deploy the trained LoRA adapter as an
  inference API. This container loads the base model and LoRA weights at
  runtime and exposes a clean HTTP interface for downstream
  applications.

These images form the execution backbone of the system, ensuring that
each stage of the pipeline runs in a controlled, isolated, and
reproducible environment.

## 2.2 Multi‑Container Orchestration with Docker Compose

The provisioning layer uses Docker Compose to coordinate the different
execution environments required throughout the pipeline. Instead of
relying on a single monolithic container, the system is organized into
multiple lightweight services, each responsible for a specific stage of
the workflow. This separation improves maintainability, enables clean
dependency boundaries, and ensures that GPU‑enabled tasks remain
isolated from CPU‑only processes.

Docker Compose provides a unified interface to start, stop, and manage
all components of the system, ensuring consistent behavior across
machines and collaborators.

**Core Services Defined in the Orchestration Layer**

- **Pipeline Service (CPU)** Runs all preprocessing, cleaning, corpus
  construction, embedding generation, FAISS indexing, retrieval,
  question generation, answer generation, validation, and dataset
  conversion. This service is based on a Python 3.10 Slim image with the
  required libraries installed directly into the environment.

- **Training Service (GPU‑enabled)** Dedicated to LoRA fine‑tuning using
  an ROCm‑enabled PyTorch image. This service has direct access to the
  host’s AMD GPU through device passthrough and is isolated from the
  CPU‑only pipeline environment to avoid dependency conflicts.

- **API Service (CPU)** A lightweight Python container extended with
  FastAPI and Uvicorn. It loads the base model and LoRA adapter at
  runtime and exposes an HTTP endpoint for inference. This service is
  intentionally kept minimal to ensure fast startup and low resource
  usage.

**Shared Volumes and Persistent Storage**

All services share a set of mounted volumes that store the artifacts
produced at each stage:

- Raw and cleaned corpus

- Embeddings and FAISS index

- Generated datasets

- Final LoRA adapters

This ensures that data persists across container rebuilds and that each
stage of the pipeline has access to the outputs of the previous one.

**Benefits of the Multi‑Container Approach**

- **Isolation of concerns** — preprocessing, training, and deployment
  each run in their own environment.

- **Reproducibility** — every collaborator runs the exact same
  containers with pinned versions.

- **Portability** — the system can be executed on local hardware, cloud
  VMs, or CI/CD pipelines without modification.

- **Scalability** — training can be moved to more powerful hardware
  without affecting the rest of the pipeline.

- **Operational clarity** — logs, dependencies, and runtime behavior are
  separated by function.

---
[← Back to Home](../README.md)
