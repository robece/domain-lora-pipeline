import os
import json
from pathlib import Path
import logging
import argparse

import torch
from datasets import load_dataset
from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    TrainingArguments,
    DataCollatorForLanguageModeling,
)
from peft import LoraConfig, get_peft_model
from trl import SFTTrainer
from huggingface_hub import HfApi

# ---------------------------------------------------------
# Argumentos de ejecución
# ---------------------------------------------------------

parser = argparse.ArgumentParser()
parser.add_argument("--push_to_hub", action="store_true", help="Upload LoRA adapter to Hugging Face if enabled.")
args = parser.parse_args()

# ---------------------------------------------------------
# Configuración general del entrenamiento
# ---------------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent.parent

INSTRUCT_PATH = BASE_DIR / "data" / "qa_pairs.instruct.jsonl"
LOG_PATH = BASE_DIR / "logs" / "train_lora.log"
OUTPUT_DIR = BASE_DIR / "models" / "qwen2.5-3b-lora-eventgrid"

MODEL_NAME = "Qwen/Qwen2.5-3B-Instruct"
HF_REPO_ID = "robece/qwen2.5-3b-lora-eventgrid"

MICRO_BATCH_SIZE = 2
GRAD_ACCUM = 8
EPOCHS = 3
LEARNING_RATE = 2e-4
MAX_SEQ_LENGTH = 1024

LORA_R = 16
LORA_ALPHA = 32
LORA_DROPOUT = 0.05

HF_TOKEN = os.environ.get("HF_TOKEN")
if args.push_to_hub and HF_TOKEN is None:
    raise ValueError("ERROR: HF_TOKEN must be exported to use --push_to_hub.")

LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    filename=str(LOG_PATH),
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)

print("=== LoRA Training: Qwen2.5-3B-Instruct ===")
logging.info("Starting LoRA training for Qwen2.5-3B-Instruct")

# ---------------------------------------------------------
# Creación del repositorio privado en Hugging Face (si aplica)
# ---------------------------------------------------------

if args.push_to_hub:
    api = HfApi()
    try:
        api.create_repo(
            repo_id=HF_REPO_ID,
            private=True,
            exist_ok=True,
            token=HF_TOKEN
        )
        print(f"Verified/created private repo: {HF_REPO_ID}")
        logging.info(f"Repo verified/created: {HF_REPO_ID}")
    except Exception as e:
        logging.error(f"Error creating repo: {e}")
        raise

# ---------------------------------------------------------
# Carga del dataset instruct
# ---------------------------------------------------------

if not INSTRUCT_PATH.exists():
    raise FileNotFoundError(f"Instruct dataset not found: {INSTRUCT_PATH}")

print(f"Loading instruct dataset from: {INSTRUCT_PATH}")
logging.info(f"Loading instruct dataset from: {INSTRUCT_PATH}")

dataset = load_dataset(
    "json",
    data_files=str(INSTRUCT_PATH),
    split="train",
)

print(f"Total examples: {len(dataset)}")
logging.info(f"Total examples: {len(dataset)}")

# ---------------------------------------------------------
# Formato del prompt
# ---------------------------------------------------------

def format_example(example):
    instruction = example.get("instruction", "").strip()
    input_text = example.get("input", "").strip()
    output = example.get("output", "").strip()

    if input_text:
        prompt = f"Instruction: {instruction}\nInput: {input_text}\nAnswer:"
    else:
        prompt = f"Instruction: {instruction}\nAnswer:"

    return {"text": prompt + " " + output}

dataset = dataset.map(format_example, remove_columns=dataset.column_names)

# ---------------------------------------------------------
# Carga del modelo y tokenizer
# ---------------------------------------------------------

device = "cuda" if torch.cuda.is_available() else "cpu"
print(f"Using device: {device}")
logging.info(f"Using device: {device}")

tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME, use_fast=False)
if tokenizer.pad_token is None:
    tokenizer.pad_token = tokenizer.eos_token

print("Loading base model Qwen2.5-3B-Instruct in BF16...")
logging.info("Loading base model Qwen2.5-3B-Instruct in BF16")

model = AutoModelForCausalLM.from_pretrained(
    MODEL_NAME,
    dtype=torch.bfloat16 if torch.cuda.is_available() else torch.float32,
    device_map="auto",
)

lora_config = LoraConfig(
    r=LORA_R,
    lora_alpha=LORA_ALPHA,
    lora_dropout=LORA_DROPOUT,
    bias="none",
    task_type="CAUSAL_LM",
)

model = get_peft_model(model, lora_config)
model.print_trainable_parameters()

# ---------------------------------------------------------
# Cálculo dinámico de warmup_steps
# ---------------------------------------------------------

effective_batch_size = MICRO_BATCH_SIZE * GRAD_ACCUM
steps_per_epoch = len(dataset) // effective_batch_size
total_steps = steps_per_epoch * EPOCHS
warmup_steps = int(total_steps * 0.03)

print(f"Dynamic warmup: {warmup_steps} steps")
logging.info(f"Dynamic warmup_steps: {warmup_steps}")

# ---------------------------------------------------------
# Argumentos de entrenamiento
# ---------------------------------------------------------

training_args = TrainingArguments(
    output_dir=str(OUTPUT_DIR),
    per_device_train_batch_size=MICRO_BATCH_SIZE,
    gradient_accumulation_steps=GRAD_ACCUM,
    num_train_epochs=EPOCHS,
    learning_rate=LEARNING_RATE,
    logging_steps=10,
    save_steps=500,
    bf16=torch.cuda.is_available(),
    fp16=False,
    optim="adamw_torch",
    weight_decay=0.01,
    lr_scheduler_type="cosine",
    warmup_steps=warmup_steps,
    report_to="none",

    push_to_hub=args.push_to_hub,
    hub_model_id=HF_REPO_ID if args.push_to_hub else None,
    hub_private_repo=True if args.push_to_hub else None,
    hub_token=HF_TOKEN if args.push_to_hub else None,
)

data_collator = DataCollatorForLanguageModeling(
    tokenizer=tokenizer,
    mlm=False,
)

# ---------------------------------------------------------
# Entrenador (compatible con TRL 0.28.0)
# ---------------------------------------------------------

trainer = SFTTrainer(
    model=model,
    train_dataset=dataset,
    args=training_args,
)

print("Starting LoRA training...")
logging.info("Starting LoRA training...")

trainer.train()

print("Training complete. Saving LoRA adapter...")
logging.info("Training completed. Saving LoRA adapter...")

model.save_pretrained(str(OUTPUT_DIR))
tokenizer.save_pretrained(str(OUTPUT_DIR))

# ---------------------------------------------------------
# Push a Hugging Face (si aplica)
# ---------------------------------------------------------

if args.push_to_hub:
    print("Uploading LoRA adapter to Hugging Face (private)...")
    logging.info("Pushing LoRA to Hugging Face...")
    trainer.push_to_hub()
else:
    print("Push to Hugging Face disabled. Model saved locally.")
    logging.info("Push disabled. Local save only.")

print("\n=== DONE ===")
print(f"LoRA saved to: {OUTPUT_DIR}")
print(f"Log saved to: {LOG_PATH}")
logging.info("Training finished.")
