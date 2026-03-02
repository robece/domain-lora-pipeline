# Azure Docs Clone Requirement

This project requires a local copy of the official Azure Documentation repository. The processing pipeline depends on the original Markdown structure, folder hierarchy, and article metadata contained in the azure-docs repository.

## Clone the Azure Docs Repository

Before running any scripts, clone the Azure Docs repository into the root of your workspace:

```bash
git clone https://github.com/MicrosoftDocs/azure-docs.git
```

Expected folder structure:

/workspace
/azure-docs
/scripts
/output
/data

## Why This Is Required

The pipeline reads and processes Markdown files directly from the Azure Docs source. Cloning the repository ensures:

    Access to the latest documentation content

    Correct folder paths for article discovery

    Compatibility with the table of contents (TOC) structure

    Reproducible processing across environments

Keeping the Repository Updated

To pull the latest changes at any time:

```bash
cd azure-docs
git pull
```