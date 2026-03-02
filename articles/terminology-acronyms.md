[← Back to Home](../README.md)

# 25. Terminology and Acronyms

This dictionary consolidates all technical terms, acronyms, and
domain‑specific expressions used throughout the project. It serves as a
reference for readers who need clarity on the models, algorithms,
infrastructure components, and machine‑learning techniques involved in
the system.

**Comprehensive Terminology Table**

| **Term / Acronym**         | **Meaning**                     | **Description in the System**                                                             |
|----------------------------|---------------------------------|-------------------------------------------------------------------------------------------|
| **RAG**                    | Retrieval‑Augmented Generation  | Architecture combining semantic retrieval (FAISS) with generative modeling (Qwen + LoRA). |
| **LoRA**                   | Low‑Rank Adaptation             | Parameter‑efficient fine‑tuning technique applied to the Qwen base model.                 |
| **Qwen2.5‑3B‑Instruct**    | Base model                      | Foundation model used for LoRA training and inference.                                    |
| **LoRA Adapter**           | Fine‑tuned weight module        | Domain‑specific weights applied on top of the base model during inference.                |
| **Azure OpenAI**           | Cloud AI service                | Provider of the embedding model used for retrieval.                                       |
| **text‑embedding‑3‑large** | Embedding model                 | Azure OpenAI model used to convert text into normalized semantic vectors.                 |
| **Embedding**              | Semantic vector                 | Numerical representation of text used for similarity search.                              |
| **FAISS**                  | Facebook AI Similarity Search   | Library used to build and query the vector index.                                         |
| **FAISS Index**            | Vector index                    | Structure storing embeddings for fast nearest‑neighbor search.                            |
| **Chunk**                  | Text fragment                   | Unit of text used for embedding and retrieval.                                            |
| **Clean corpus**           | corpus_clean.jsonl              | Normalized and chunked documentation used for retrieval and dataset creation.             |
| **Metadata**               | embeddings_metadata.jsonl       | Information aligned with each embedding (chunk ID, source, offsets).                      |
| **BF16**                   | Bfloat16                        | Numerical format used to load the model efficiently on ROCm GPUs.                         |
| **ROCm**                   | Radeon Open Compute             | AMD’s GPU compute platform used for model inference.                                      |
| **PEFT**                   | Parameter‑Efficient Fine‑Tuning | Framework enabling LoRA training without modifying full model weights.                    |
| **Transformers**           | Model library                   | Framework used for tokenization, model loading, and generation.                           |
| **FastAPI**                | Web framework                   | Technology used to expose the RAG server as an HTTP API.                                  |
| **Uvicorn**                | ASGI server                     | Runtime engine executing the FastAPI application.                                         |
| **Docker**                 | Container platform              | Used to package and deploy the RAG server.                                                |
| **Docker Image**           | Container image                 | Self‑contained environment including server code, FAISS index, corpus, and LoRA adapter.  |
| **ROCm PyTorch Image**     | Base image                      | GPU‑enabled PyTorch environment used as the foundation for the server container.          |
| **Inference**              | Model execution                 | Process of generating answers using the LoRA‑enhanced Qwen model.                         |
| **Prompt**                 | Structured input                | Template combining retrieved context and the user question.                               |
| **Grounding**              | Context‑restricted generation   | Technique ensuring the model answers only using retrieved context.                        |
| **Context Retrieval**      | Semantic search                 | Process of selecting the most relevant chunks using FAISS.                                |
| **Top‑k**                  | Retrieval parameter             | Number of chunks returned by FAISS for prompt construction.                               |
| **JSONL**                  | JSON Lines                      | File format where each line contains a standalone JSON object.                            |
| **Training dataset**       | Q&A dataset                     | Collection of question–answer pairs used for LoRA fine‑tuning.                            |
| **Normalization**          | Text cleaning                   | Process of preparing raw documentation for chunking and embedding.                        |
| **Semantic Search**        | Meaning‑based retrieval         | Retrieval based on vector similarity rather than keyword matching.                        |
| **Device Map**             | Model placement                 | Automatic distribution of model layers across GPU devices.                                |
| **Repetition Penalty**     | Generation parameter            | Reduces repeated phrases during inference.                                                |
| **Temperature**            | Sampling parameter              | Controls randomness in model output.                                                      |
| **Top‑p**                  | Nucleus sampling                | Limits token selection to a probability mass threshold.                                   |
| **Max New Tokens**         | Generation limit                | Maximum number of tokens produced by the model.                                           |
| **Health Endpoint**        | /health                         | Endpoint used to verify server availability.                                              |
| **Request Logging**        | Runtime logging                 | System that records questions, answers, and metadata in /logs/requests.log.               |
| **Inference Container**    | Production container            | Docker image running the RAG server in production.                                        |
| **Semantic Fidelity**      | Context adherence               | Degree to which the model output matches the retrieved evidence.                          |
| **Dynamic Thresholding**   | Adaptive filtering              | Technique used in earlier pipeline stages to filter low‑quality data.                     |
| **Traceability**           | Output auditability             | Ability to trace each answer back to its context and retrieval path.                      |

---
[← Back to Home](../README.md)
