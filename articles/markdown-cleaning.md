[← Back to Home](../README.md)

## Table of Contents

- [9.1 What This Stage Does](#91-what-this-stage-does)
- [9.2 How the Cleaning Process Works (clean_markdown.py)](#92-how-the-cleaning-process-works-cleanmarkdownpy)
- [9.3 Why This Stage Matters](#93-why-this-stage-matters)
- [9.4 Cleaning Previous Outputs (purge_clean_markdown.py)](#94-cleaning-previous-outputs-purgecleanmarkdownpy)
- [9.5 Inputs and Outputs of This Stage](#95-inputs-and-outputs-of-this-stage)
- [9.6 Role of This Stage in the Pipeline](#96-role-of-this-stage-in-the-pipeline)

# 9. Markdown Cleaning and Normalization (clean_markdown.py + purge_clean_markdown.py)

This stage transforms the raw Azure documentation into clean, readable
text that is ready for semantic processing. The goal is simple: remove
everything that adds noise and keep only the meaningful content. The
script takes each markdown file discovered in the previous stage, cleans
it, converts it into plain text, and then breaks it into manageable
chunks. These cleaned documents and chunks become the foundation for
embeddings, FAISS indexing, and all downstream reasoning steps.

## 9.1 What This Stage Does

This stage takes the raw markdown files and prepares them for semantic
work. It removes formatting, code blocks, images, and other elements
that don’t contribute to the meaning of the text. It then organizes the
cleaned content into smaller, coherent pieces so the model can
understand and index them effectively.

## 9.2 How the Cleaning Process Works (clean_markdown.py)

The script follows a clear sequence of steps to transform each markdown
file into clean text.

**1. Load the markdown file**

It reads the original markdown exactly as it appears in the Azure
documentation.

**2. Remove front matter**

Some markdown files begin with metadata enclosed in ---. This metadata
is not useful for semantic understanding, so it is removed.

**3. Convert markdown to HTML**

The script uses a markdown parser to convert the markdown into HTML.
This makes it easier to remove unwanted elements in the next step.

**4. Convert HTML to plain text**

Using an HTML parser, the script extracts only the meaningful text and
removes:

- code blocks

- images

- scripts and styles

- admonitions (NOTE, WARNING, etc.)

- embedded components

- formatting tags

The result is clean, readable text without distractions.

**5. Normalize the text**

The script cleans up the text by:

- removing extra blank lines

- collapsing multiple spaces

- trimming unnecessary whitespace

This ensures consistency across all documents.

**6. Save the cleaned document**

Each cleaned document is saved as a JSON file in clean_docs/,
containing:

- the title

- the original path

- the TOC hierarchy

- the cleaned text

This preserves context while keeping the content clean.

**7. Split the text into chunks**

The cleaned text is divided into smaller sections that:

- do not exceed a reasonable size

- avoid cutting sentences abruptly

- preserve paragraph boundaries

Each chunk is saved as a separate JSON file in clean_chunks/.

These chunks are what the embedding model will process later.

## 9.3 Why This Stage Matters

Clean, consistent text is essential for:

- generating high‑quality embeddings

- building a reliable FAISS index

- producing accurate retrieval results

- generating grounded questions and answers

- training a LoRA model that understands the domain

If the text contains noise, formatting artifacts, or irrelevant
elements, the entire pipeline suffers. This stage ensures that only
meaningful, well‑structured content moves forward.

## 9.4 Cleaning Previous Outputs (purge_clean_markdown.py)

This companion script resets the outputs of the cleaning stage.

**What it removes**

- all cleaned documents in clean_docs/

- all generated chunks in clean_chunks/

- the cleaning log file

**Why it’s useful**

It allows you to rerun the cleaning process from scratch without
leftover files that could cause inconsistencies or confusion.

## 9.5 Inputs and Outputs of This Stage

**Inputs**

- eventgrid_files.json — the list of valid markdown files from the
  previous stage

- raw markdown files from the Azure documentation

**Outputs**

- clean_docs/\*.json — cleaned, normalized documents

- clean_chunks/\*.json — chunked text ready for embeddings

- clean_markdown.log — detailed log of the cleaning process

## 9.6 Role of This Stage in the Pipeline

This stage ensures that the pipeline works with clean, consistent, and
semantically meaningful text. It removes noise, preserves structure, and
prepares the content for embedding generation. Without this step, the
model would learn from messy, inconsistent data, leading to poor
retrieval and weak LoRA training.

---
[← Back to Home](../README.md)
