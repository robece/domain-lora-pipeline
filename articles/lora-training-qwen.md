[← Back to Home](../README.md)

## Table of Contents

- [20.1 Purpose of This Stage](#201-purpose-of-this-stage)
- [20.2 How the Training Script Works (train_lora.py)](#202-how-the-training-script-works-trainlorapy)
- [20.3 Why This Stage Matters](#203-why-this-stage-matters)
- [20.4 Cleaning Training Outputs (purge_train_lora.py)](#204-cleaning-training-outputs-purgetrainlorapy)
- [20.5 Inputs and Outputs of This Stage](#205-inputs-and-outputs-of-this-stage)
- [20.6 Role of This Stage in the Pipeline](#206-role-of-this-stage-in-the-pipeline)

# 20. LoRA Training on Qwen2.5‑3B‑Instruct (train_lora.py + purge_train_lora.py)

This stage is the culmination of the entire pipeline. After cleaning,
validating, and formatting the dataset, the system finally trains a LoRA
adapter on top of the Qwen2.5‑3B‑Instruct model. The goal is to produce
a lightweight, domain‑specialized model that understands Azure Event
Grid deeply and responds with grounded, technical accuracy. This stage
also supports optional private publishing to Hugging Face.

## 20.1 Purpose of This Stage

The training step takes the instruct‑formatted dataset and fine‑tunes a
base model using LoRA (Low‑Rank Adaptation). LoRA modifies only a small
set of trainable parameters, making training:

- efficient

- hardware‑friendly

- fast

- easy to store and deploy

The result is a compact adapter that can be merged with the base model
or loaded dynamically at inference time.

## 20.2 How the Training Script Works (train_lora.py)

The script orchestrates dataset loading, model preparation, LoRA
configuration, training, saving, and optional publishing.

**1. Load arguments and configuration**

The script accepts a single optional flag:

- --push_to_hub — uploads the trained LoRA to a private Hugging Face
  repo.

It defines:

- dataset paths

- model paths

- LoRA hyperparameters

- training hyperparameters

- Hugging Face repo ID

It also checks for the HF_TOKEN environment variable if pushing is
enabled.

**2. Load the instruct dataset**

The script loads qa_pairs.instruct.jsonl using the Hugging Face datasets
library. Each entry contains:

- "instruction"

- "input" (empty)

- "output"

This dataset is then transformed into a single "text" field using a
prompt template:

Code

Instruction: \<instruction\>  
Answer: \<output\>  
  
This ensures the model learns the expected conversational pattern.

**3. Load the base model and tokenizer**

The script loads:

- **Qwen2.5‑3B‑Instruct** as the base model

- its tokenizer, ensuring a valid pad token

The model is loaded in **BF16** when GPU is available, which is ideal
for ROCm and modern NVIDIA cards.

**4. Apply the LoRA configuration**

The script configures LoRA with:

- rank = 16

- alpha = 32

- dropout = 0.05

These values balance training stability and parameter efficiency.

The model is wrapped with get_peft_model, enabling LoRA layers.

**5. Compute dynamic warmup steps**

Warmup is calculated based on:

- dataset size

- batch size

- gradient accumulation

- number of epochs

This ensures smoother training and avoids early instability.

**6. Define training arguments**

The script configures:

- batch size

- gradient accumulation

- learning rate

- cosine scheduler

- warmup steps

- weight decay

- logging and saving frequency

- hub integration (if enabled)

These settings are optimized for small‑GPU training.

**7. Train using TRL’s SFTTrainer**

The SFTTrainer handles:

- tokenization

- batching

- loss computation

- gradient updates

It is fully compatible with LoRA and Qwen models.

**8. Save the trained adapter**

After training, the script saves:

- the LoRA adapter

- the tokenizer

These files are stored in:

Code

models/qwen2.5-3b-lora-eventgrid/  
  
**9. Optional: Push to Hugging Face**

If --push_to_hub is enabled:

- the script creates or verifies a private repo

- uploads the LoRA adapter

- uploads the tokenizer

- ensures the repo remains private

This allows secure sharing or deployment.

## 20.3 Why This Stage Matters

This stage transforms the entire pipeline from a data‑processing system
into a model‑building system. The LoRA adapter produced here:

- captures the structure of Azure Event Grid

- learns from validated, high‑fidelity QA pairs

- responds with grounded, technical accuracy

- is lightweight and easy to deploy

- can be merged with the base model or loaded on demand

This is the final product of the pipeline: a domain‑specialized model
ready for real‑world use.

## 20.4 Cleaning Training Outputs (purge_train_lora.py)

This companion script resets the training environment by deleting:

- the LoRA model directory

- the training log

- any checkpoint directories

This is useful when:

- retraining from scratch

- adjusting hyperparameters

- updating the dataset

- switching base models

It ensures a clean slate for the next training run.

## 20.5 Inputs and Outputs of This Stage

**Inputs**

- qa_pairs.instruct.jsonl — the instruct‑formatted dataset

- Qwen2.5‑3B‑Instruct base model

- LoRA configuration

**Outputs**

- trained LoRA adapter

- tokenizer

- optional private Hugging Face repo

- train_lora.log — detailed training log

## 20.6 Role of This Stage in the Pipeline

This is the final transformation step. Everything before this stage
prepares the data; everything after this stage uses the trained model.
It represents the culmination of the entire pipeline: a clean,
validated, domain‑specific LoRA model ready for deployment.

---
[← Back to Home](../README.md)
