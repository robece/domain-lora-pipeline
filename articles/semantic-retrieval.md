[← Back to Home](../README.md)

## Table of Contents

- [13.1 Purpose of This Stage](#131-purpose-of-this-stage)
- [13.2 How the Retriever Works (retriever.py)](#132-how-the-retriever-works-retrieverpy)
- [13.3 Why This Stage Matters](#133-why-this-stage-matters)
- [13.4 Cleaning Previous Outputs (purge_retriever.py)](#134-cleaning-previous-outputs-purgeretrieverpy)
- [13.5 Inputs and Outputs of This Stage](#135-inputs-and-outputs-of-this-stage)
- [13.6 Role of This Stage in the Pipeline](#136-role-of-this-stage-in-the-pipeline)

# 13. Semantic Retrieval (retriever.py + purge_retriever.py)

This stage gives the pipeline the ability to *search by meaning*.
Instead of looking for keywords, the system uses the FAISS index and
Azure OpenAI embeddings to find the most relevant chunks of
documentation for any question. This is the first moment where the
pipeline behaves like a real retrieval‑augmented system: you ask a
question, and it returns the most semantically related pieces of the
Azure Event Grid documentation.

## 13.1 Purpose of This Stage

The goal of this stage is to take a user query, convert it into an
embedding, and use the FAISS index to retrieve the top‑k most relevant
chunks from the corpus. These retrieved chunks become the foundation
for:

- RAG‑style reasoning

- question generation

- answer generation

- dataset creation

- LoRA training

If retrieval is inaccurate, everything downstream becomes weaker. This
stage ensures that the system can reliably surface the right
information.

## 13.2 How the Retriever Works (retriever.py)

The script loads everything it needs—FAISS index, metadata, and
corpus—and exposes two core functions: one to embed a query, and one to
search for relevant chunks.

**1. Load the FAISS index**

The script checks that the index exists and loads it into memory. It
logs:

- the vector dimension

- the total number of vectors stored

This confirms that the index is ready for semantic search.

**2. Load metadata and corpus**

Two files are loaded:

- embeddings_metadata.jsonl — contains the metadata for each embedding

- corpus_clean.jsonl — contains the actual text chunks

Both lists are aligned: the nth metadata entry corresponds to the nth
corpus entry.

**3. Convert a query into an embedding**

When a user provides a question, the script:

- sends the text to Azure OpenAI using the same embedding model used for
  the corpus

- receives a 3072‑dimensional vector

- normalizes it so it works correctly with FAISS

This ensures that the query lives in the same vector space as the
corpus.

**4. Search the FAISS index**

The script performs a semantic search using:

- the normalized query embedding

- the FAISS index

- a configurable number of results (default: top‑5)

FAISS returns:

- the IDs of the most similar chunks

- the similarity scores

**5. Build the final results**

For each retrieved ID, the script gathers:

- the similarity score

- the chunk ID

- the source article

- the TOC path

- the chunk text

The result is a list of the most relevant documentation snippets for the
query.

**6. Optional CLI usage**

If run from the command line, the script prints the retrieved chunks in
a readable format.

## 13.3 Why This Stage Matters

This stage is the backbone of the entire pipeline. It enables:

- grounded question generation

- grounded answer generation

- multi‑turn reasoning

- dataset creation

- LoRA training with real documentation context

Without accurate retrieval, the system would hallucinate or rely on
irrelevant information. With retrieval, every step becomes grounded in
the actual Azure Event Grid documentation.

## 13.4 Cleaning Previous Outputs (purge_retriever.py)

This companion script resets the retriever’s logs.

**What it removes**

- the retriever log file

**Why it’s useful**

It keeps the retriever’s logs clean and makes debugging easier when
running multiple retrieval tests.

## 13.5 Inputs and Outputs of This Stage

**Inputs**

- faiss.index — the semantic search index

- embeddings_metadata.jsonl — metadata aligned with embeddings

- corpus_clean.jsonl — the full cleaned corpus

- Azure OpenAI embedding model

**Outputs**

- a list of the top‑k most relevant chunks for any query

- retriever.log — detailed log of retrieval operations

## 13.6 Role of This Stage in the Pipeline

This stage transforms the pipeline from a static dataset into an
intelligent retrieval system. It allows the model to access the right
information at the right time, enabling all downstream tasks to be
grounded, accurate, and semantically aligned with the documentation.

---
[← Back to Home](../README.md)
