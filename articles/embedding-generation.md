[← Back to Home](../README.md)

## Table of Contents

- [11.1 Purpose of This Stage](#111-purpose-of-this-stage)
- [11.2 How Embeddings Are Generated (generate_embeddings.py)](#112-how-embeddings-are-generated-generateembeddingspy)
- [11.3 Building the FAISS Index](#113-building-the-faiss-index)
- [11.4 Why This Stage Matters](#114-why-this-stage-matters)
- [11.5 Cleaning Previous Outputs (purge_generate_embeddings.py)](#115-cleaning-previous-outputs-purgegenerateembeddingspy)
- [11.6 Inputs and Outputs of This Stage](#116-inputs-and-outputs-of-this-stage)
- [11.7 Role of This Stage in the Pipeline](#117-role-of-this-stage-in-the-pipeline)

# 11. Embedding Generation and FAISS Index Construction (generate_embeddings.py + purge_generate_embeddings.py)

This stage transforms the cleaned corpus into numerical representations
that a model can understand. It generates embeddings for every chunk of
text, stores them efficiently, and builds a FAISS index that enables
fast semantic search. This is the moment where the pipeline becomes
“searchable”: text turns into vectors, and vectors become a searchable
index.

## 11.1 Purpose of This Stage

The goal here is to take the unified corpus and convert each chunk into
a high‑dimensional vector using Azure OpenAI’s embedding model. These
vectors capture the meaning of the text, allowing the system to compare
chunks based on semantic similarity rather than keywords. Once all
embeddings are generated, they are stored and indexed so the pipeline
can retrieve relevant information quickly and accurately.

## 11.2 How Embeddings Are Generated (generate_embeddings.py)

The script follows a clear sequence to turn text into vectors and
prepare everything for retrieval.

**1. Load the clean corpus**

It reads corpus_clean.jsonl, which contains all the validated chunks
from the previous stage. Each line represents one chunk with its text
and metadata.

**2. Prepare the output environment**

Before generating anything new, the script removes old files:

- previous embeddings

- previous metadata

- previous FAISS index

This ensures that the new run starts clean.

**3. Extract the text and metadata**

For each corpus entry:

- it takes the cleaned text

- it collects metadata such as the chunk ID, source article, and TOC
  path

Empty or invalid entries are skipped.

**4. Send the text to Azure OpenAI**

The script uses the model text-embedding-3-large, which produces
3072‑dimensional vectors.

To be efficient, it sends the text in batches (32 at a time). For each
batch:

- Azure returns a list of embeddings

- the script stores them in memory

- any errors are logged

By the end, all embeddings are combined into a single matrix.

**5. Normalize the embeddings**

The vectors are normalized so they work correctly with FAISS’s
inner‑product search. This step ensures that similarity scores behave
consistently.

**6. Save the embeddings and metadata**

Two files are created:

- embeddings.npy — a compact NumPy array with all vectors

- embeddings_metadata.jsonl — one line per chunk with its metadata

These files stay perfectly aligned: the nth embedding corresponds to the
nth metadata entry.

## 11.3 Building the FAISS Index

Once the embeddings are ready, the script builds a FAISS index to enable
fast semantic search.

**How it works**

- It reads the dimensionality of the embeddings (3072).

- It creates a FAISS index optimized for inner‑product similarity.

- It adds all embeddings to the index.

- It saves the index to faiss.index.

This index becomes the backbone of retrieval for the rest of the
pipeline.

## 11.4 Why This Stage Matters

This stage is essential because it gives the pipeline the ability to:

- understand text semantically

- compare chunks based on meaning

- retrieve relevant information quickly

- support RAG‑style reasoning

- generate grounded questions and answers

- train a LoRA model with high‑quality context

Without embeddings and FAISS, the system would have no way to “search by
meaning,” which is the core of the entire workflow.

## 11.5 Cleaning Previous Outputs (purge_generate_embeddings.py)

This companion script resets the outputs of the embedding stage.

**What it removes**

- embeddings.npy

- embeddings_metadata.jsonl

- faiss.index

- the embedding log file

**Why it’s useful**

It ensures that the embedding generation step always starts fresh,
especially when:

- the corpus changes

- contamination rules change

- the embedding model changes

- you want to regenerate the FAISS index

This keeps the pipeline consistent and reproducible.

## 11.6 Inputs and Outputs of This Stage

**Inputs**

- corpus_clean.jsonl — the unified clean corpus

- Azure OpenAI embedding model

**Outputs**

- embeddings.npy — all embeddings in order

- embeddings_metadata.jsonl — metadata aligned with embeddings

- faiss.index — the semantic search index

- generate_embeddings.log — detailed log of the process

## 11.7 Role of This Stage in the Pipeline

This stage is the bridge between text and semantic search. It transforms
the corpus into a vector space where meaning can be compared
mathematically. Everything that follows—retrieval, RAG simulation,
question generation, answer generation, and LoRA training—depends on the
quality and consistency of these embeddings.

---
[← Back to Home](../README.md)
