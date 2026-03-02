[← Back to Home](../README.md)

## Table of Contents

- [17.1 Purpose of This Stage](#171-purpose-of-this-stage)
- [17.2 How the Validation Script Works (validate_questions.py)](#172-how-the-validation-script-works-validatequestionspy)
- [17.3 Why This Stage Matters](#173-why-this-stage-matters)
- [17.4 Cleaning Previous Outputs (purge_validate_questions.py)](#174-cleaning-previous-outputs-purgevalidatequestionspy)
- [17.5 Inputs and Outputs of This Stage](#175-inputs-and-outputs-of-this-stage)
- [17.6 Role of This Stage in the Pipeline](#176-role-of-this-stage-in-the-pipeline)

# 17. Question Validation and Context Alignment (validate_questions.py + purge_validate_questions.py)

This stage evaluates every generated question and determines whether it
can truly be answered using the documentation. It acts as a quality gate
between question generation and answer generation. Instead of trusting
that all questions are valid, the system checks each one against the
FAISS index and uses Azure OpenAI to decide whether the retrieved
context contains enough information to answer it. The result is a clean
split between **valid questions** (safe to answer) and **invalid
questions** (should be discarded).

## 17.1 Purpose of This Stage

The goal is to ensure that every question in the dataset is grounded in
the documentation. A question is considered valid only if the retrieved
context contains enough information to answer it. This prevents:

- hallucinated questions

- overly broad or vague questions

- questions that require external knowledge

- questions that cannot be answered from the documentation

This step protects the quality of the QA dataset and ensures that answer
generation remains grounded and reliable.

## 17.2 How the Validation Script Works (validate_questions.py)

The script performs a structured process to evaluate each question.

**1. Load FAISS index, embeddings, and metadata**

The script loads:

- the FAISS index

- the embedding vectors

- the metadata aligned with each embedding

This gives the validator the ability to retrieve the most relevant
chunks for any question.

**2. Load all generated questions**

It reads every question from generated_questions.jsonl and prepares them
for validation.

**3. Embed the question**

For each question:

- the script generates an embedding using Azure OpenAI

- the embedding is normalized and used to search the FAISS index

This ensures that the validation process uses the same semantic space as
the rest of the pipeline.

**4. Retrieve the top‑5 context chunks**

The script retrieves the five most relevant chunks from the FAISS index.
Instead of using the full text, it uses the metadata entries for each
chunk. These metadata entries contain enough information for the
validator to judge whether the question is answerable.

**5. Build a strict validation prompt**

The prompt instructs the model to:

- read the question

- read the retrieved context

- decide whether the context contains enough information to answer the
  question

- respond only with **VALID** or **INVALID**

- provide no explanation

This keeps the validation consistent and machine‑readable.

**6. Call Azure OpenAI to classify the question**

The script sends the prompt to the model gpt‑4o. The model returns
either:

- **VALID**

- **INVALID**

If the model returns anything else, the script logs the issue and skips
the question.

**7. Save the question to the appropriate file**

Depending on the verdict:

- valid questions go to validated_questions.jsonl

- invalid questions go to invalid_questions.jsonl

This creates a clean separation between usable and unusable questions.

**8. Log a complete summary**

At the end, the script prints and logs:

- number of valid questions

- number of invalid questions

- paths to the output files

This gives full visibility into the quality of the generated questions.

## 17.3 Why This Stage Matters

This stage ensures that the QA dataset is:

- **grounded** — every question is answerable from the documentation

- **reliable** — no hallucinated or unsupported questions

- **clean** — invalid questions are filtered out early

- **efficient** — answer generation only processes valid questions

Without this stage, the system might generate answers to questions that
cannot be answered from the documentation, leading to hallucinations and
degraded LoRA training.

## 17.4 Cleaning Previous Outputs (purge_validate_questions.py)

This companion script resets the outputs of the validation stage.

**What it removes**

- validated_questions.jsonl

- invalid_questions.jsonl

- validate_questions.log

**Why it’s useful**

It allows you to re‑run the validation step from scratch, especially
after:

- updating the corpus

- improving retrieval

- adjusting the validation prompt

- regenerating questions

This keeps the dataset consistent and reproducible.

## 17.5 Inputs and Outputs of This Stage

### **Inputs**

- generated_questions.jsonl — all generated questions

- FAISS index and embeddings

- metadata for each embedding

- Azure OpenAI model (gpt‑4o)

### **Outputs**

- validated_questions.jsonl — questions that can be answered from the
  documentation

- invalid_questions.jsonl — questions that cannot be answered

- validate_questions.log — detailed log of the process

## 17.6 Role of This Stage in the Pipeline

This stage is the quality filter that ensures the dataset remains
grounded and trustworthy. It prevents invalid questions from
contaminating the QA dataset and ensures that the next stage—dataset
auditing—works with clean, validated inputs.

---
[← Back to Home](../README.md)
