[← Back to Home](../README.md)

## Table of Contents

- [4.1 Local GPU Acceleration for LoRA Training](#41-local-gpu-acceleration-for-lora-training)
- [4.2 Cloud‑Based Inference for Embeddings and Reasoning](#42-cloudbased-inference-for-embeddings-and-reasoning)
- [4.3 CPU‑Optimized Retrieval and Indexing](#43-cpuoptimized-retrieval-and-indexing)
- [4.4 Benefits of the Hybrid Approach](#44-benefits-of-the-hybrid-approach)

# 4. Hybrid Hardware Strategy

The pipeline is designed around a hybrid hardware model that balances
cost efficiency, performance, and flexibility. Instead of relying
exclusively on cloud infrastructure or local compute, the system
strategically distributes workloads across different environments based
on their computational characteristics. This approach minimizes
operational costs while ensuring that each stage of the pipeline runs on
the most suitable hardware.

## 4.1 Local GPU Acceleration for LoRA Training

LoRA fine‑tuning is the only stage of the pipeline that requires GPU
acceleration. To support this, the system uses:

- An **AMD RX 7900 XTX** as the primary training device.

- A **ROCm‑enabled PyTorch environment** inside a dedicated training
  container.

- Direct GPU passthrough from the host to the container via /dev/kfd and
  /dev/dri.

This configuration enables efficient fine‑tuning without the need for
NVIDIA hardware or cloud‑based GPU instances. It also ensures that
training remains fully reproducible and independent of external
services.

## 4.2 Cloud‑Based Inference for Embeddings and Reasoning

Embedding generation and reasoning tasks are delegated to **Azure
OpenAI**, which provides:

- High‑quality embedding models with stable dimensionality.

- Consistent reasoning performance for RAG queries, question generation,
  and answer generation.

- Zero local GPU requirements for inference.

This offloading strategy avoids the need to host large embedding or
generative models locally, reducing hardware complexity and ensuring
predictable performance.

## 4.3 CPU‑Optimized Retrieval and Indexing

FAISS indexing and similarity search run entirely on CPU, which offers
several advantages:

- Full compatibility with lightweight Python containers.

- Deterministic behavior across machines.

- No dependency on GPU drivers or specialized hardware.

This makes the retrieval layer portable and easy to deploy in any
environment, including CI/CD pipelines or cloud VMs.

## 4.4 Benefits of the Hybrid Approach

The hybrid hardware strategy provides a balanced and efficient execution
model:

- **Cost efficiency** — training is performed locally, avoiding cloud
  GPU costs.

- **Scalability** — embedding and reasoning scale automatically through
  Azure OpenAI.

- **Portability** — FAISS and preprocessing remain CPU‑friendly and
  container‑friendly.

- **Flexibility** — each stage can be moved to different hardware
  without redesigning the system.

This architecture ensures that the pipeline remains accessible,
reproducible, and adaptable as the project evolves.

---
[← Back to Home](../README.md)
