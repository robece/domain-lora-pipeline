# Domain LoRA Pipeline

Created by Roberto — Powered by AI

## Introduction

Developing an end‑to‑end system that transforms raw documentation into a
fine‑tuned LoRA model requires more than a collection of scripts. It
depends on a carefully engineered provisioning layer that guarantees
reproducibility, isolation, and operational stability across
heterogeneous workloads. This project explores that full lifecycle—from
preprocessing and semantic indexing to model training and
inference—through a modular, containerized pipeline designed for
clarity, transparency, and repeatability.

As a Product Manager specializing in messaging and event‑driven
platforms, my work revolves around technologies such as Azure Event Grid
and distributed communication systems. Although I am not a machine
learning expert, I am deeply interested in understanding how modern ML
techniques can complement event‑driven architectures and enhance
developer and operator experiences. This project represents a personal
learning initiative: a hands‑on exploration of data preparation,
embedding generation, retrieval‑augmented generation, and LoRA
fine‑tuning, all applied to a domain I work with professionally.

My goal is not only to build a functional model, but also to internalize
the underlying concepts—dataset curation, contamination filtering,
vector search, container orchestration, and training workflows—so that I
can better evaluate, design, and communicate ML‑driven capabilities
within messaging ecosystems. By approaching the problem from a product
perspective, this work aims to bridge practical engineering concerns
with foundational machine learning principles, resulting in a
reproducible pipeline that is both technically sound and accessible to
non‑experts.

This learning journey also aligns with a broader industry shift toward
autonomous agents and Model Context Protocol (MCP) ecosystems. As cloud
platforms evolve, agents capable of reasoning, orchestrating workflows,
and interacting with distributed systems are becoming integral to modern
architectures. Understanding how models are trained, how context is
retrieved, and how knowledge is structured is essential for designing
agent‑driven experiences that operate reliably within event‑based
environments. By grounding this project in real messaging technologies,
I aim to build the foundational knowledge required to participate in the
emerging era of intelligent agents, where ML models, event systems, and
MCP‑enabled components collaborate seamlessly to automate complex
operational and product workflows.

## Articles

| Article |
|---------|
| [1. Design Principles for the Execution Environment](articles/design-principles.md) |
| [2. Containerization as the Execution Backbone](articles/containerization.md) |
| [3. Core Technologies Underpinning the Pipeline](articles/core-technologies.md) |
| [4. Hybrid Hardware Strategy](articles/hybrid-hardware-strategy.md) |
| [5. Directory Structure and Artifact Governance](articles/directory-structure.md) |
| [6. Environment and Container Orchestration](articles/environment-container.md) |
| [7. Pipeline Overview](articles/pipeline-overview.md) |
| [8. Markdown Ingestion and Structural Parsing (parse_toc.py + purge_parse_toc.py)](articles/markdown-ingestion.md) |
| [9. Markdown Cleaning and Normalization (clean_markdown.py + purge_clean_markdown.py)](articles/markdown-cleaning.md) |
| [10. Corpus Construction and Chunk Filtering (build_clean_corpus.py + purge_build_clean_corpus.py)](articles/corpus-construction-chunk.md) |
| [11. Embedding Generation and FAISS Index Construction (generate_embeddings.py + purge_generate_embeddings.py)](articles/embedding-generation.md) |
| [12. FAISS Index Validation and Semantic Readiness (check_faiss.py)](articles/faiss-index-validation.md) |
| [13. Semantic Retrieval (retriever.py + purge_retriever.py)](articles/semantic-retrieval.md) |
| [14. RAG‑Style Reasoning and Contextual Answer Generation (rag_query.py + purge_rag_query.py)](articles/style-reasoning.md) |
| [15. Technical Question Generation (generate_questions.py + purge_generate_questions.py)](articles/technical-question.md) |
| [16. Grounded Answer Generation (generate_answers.py + purge_generate_answers.py)](articles/grounded-answer.md) |
| [17. Question Validation and Context Alignment (validate_questions.py + purge_validate_questions.py)](articles/question-validation.md) |
| [18. Dataset Auditing and Quality Assurance (audit_dataset.py + purge_audit_dataset.py)](articles/dataset-auditing-quality.md) |
| [19. Instruction Formatting for LoRA Training (convert_to_instruct.py + purge_convert_to_instruct.py)](articles/instruction-formatting.md) |
| [20. LoRA Training on Qwen2.5‑3B‑Instruct (train_lora.py + purge_train_lora.py)](articles/lora-training-qwen.md) |
| [21. Using the Trained LoRA Model Inside the Real RAG Server (server.py)](articles/using-trained-lora-model.md) |
| [22. Deployment of the RAG + LoRA Server in Production (Docker‑based)](articles/lora-deployment-docker.md) |
| [23. Pipeline Maintenance and Regeneration](articles/pipeline-maintenance.md) |
| [24. Model Usage Across the Pipeline](articles/model-usage-across.md) |
| [25. Terminology and Acronyms](articles/terminology-acronyms.md) |
