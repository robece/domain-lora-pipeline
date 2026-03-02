[← Back to Home](../README.md)

## Table of Contents

- [8.1 Understanding the TOC Parsing Process (parse_toc.py)](#81-understanding-the-toc-parsing-process-parsetocpy)
- [8.2 Cleaning Previous Outputs (purge_parse_toc.py)](#82-cleaning-previous-outputs-purgeparsetocpy)
- [8.3 Inputs and Outputs of This Stage](#83-inputs-and-outputs-of-this-stage)
- [8.4 Role of This Stage in the Pipeline](#84-role-of-this-stage-in-the-pipeline)

# 8. Markdown Ingestion and Structural Parsing (parse_toc.py + purge_parse_toc.py)

This stage is the entry point of the entire pipeline. Its purpose is to
identify which documentation files actually exist in the local Azure
Event Grid repository and prepare a clean, reliable list of markdown
files that the rest of the system will process. It does this by reading
the official Azure Event Grid table of contents (TOC), flattening its
hierarchy, resolving real file paths, and filtering out missing or
invalid entries. The result is a curated list of valid markdown sources
that becomes the foundation for all subsequent steps.

## 8.1 Understanding the TOC Parsing Process (parse_toc.py)

The TOC provided by Microsoft is a hierarchical YAML file that describes
the structure of the documentation: sections, subsections, and the
markdown files associated with each one. This script reads that TOC and
transforms it into a practical, usable list.

**What the script does**

- Loads the toc.yml file that defines the documentation structure.

- Walks through the hierarchy and converts it into a flat list of
  entries, each containing:

  - the title of the section,

  - the relative path to the markdown file,

  - the full hierarchical path showing where the file sits in the
    documentation.

- Resolves each href into an actual file path inside the locally cloned
  Azure Docs repository.

- Checks whether each referenced markdown file actually exists.

- Keeps only the entries that point to real files.

- Saves the final list of valid files to eventgrid_files.json.

- Records a detailed log of everything that happened, including missing
  files, in parse_toc.log.

**Why this matters**

This step ensures that the pipeline only works with documentation that
truly exists. It prevents downstream errors, avoids processing broken
references, and guarantees that the dataset is built from a clean,
verified set of markdown sources. It also preserves the original
documentation hierarchy, which is useful for later stages that rely on
contextual structure.

## 8.2 Cleaning Previous Outputs (purge_parse_toc.py)

This companion script exists to reset the environment for this stage. It
removes any previous outputs so the TOC parsing can run again from a
clean state.

**What the script does**

- Deletes the previously generated eventgrid_files.json.

- Deletes the log file parse_toc.log.

- Prints a simple summary of what was removed.

**Why this matters**

It ensures that the TOC parsing step always starts fresh, without
leftover files that could cause confusion or hide issues. This is
especially useful when updating the documentation source or re-running
the pipeline after changes.

## 8.3 Inputs and Outputs of This Stage

**Inputs**

- data/toc.yml — the official Azure Event Grid TOC.

- Local clone of Azure Docs (azure-docs/articles/event-grid).

**Outputs**

- data/eventgrid_files.json — the validated list of markdown files to
  process.

- logs/parse_toc.log — a detailed log of the parsing process.

## 8.4 Role of This Stage in the Pipeline

This stage establishes the foundation for the entire corpus-processing
workflow. By validating the documentation structure and producing a
clean list of markdown files, it ensures that every subsequent
step—cleaning, chunking, embeddings, FAISS indexing, QA generation, and
LoRA training—operates on a consistent and trustworthy set of inputs.

---
[← Back to Home](../README.md)
