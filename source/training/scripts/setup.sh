#!/bin/bash
set -e

echo "Starting containers..."
sudo docker compose up -d --remove-orphans

echo "Configuring Ollama container..."
sudo docker exec ollama bash -c "
    ollama pull llava:13b &&
    ollama pull llava:7b &&
    ollama pull qwen2.5:14b
"

echo "Configuring PyTorch ROCm container..."
sudo docker exec pytorch-rocm bash -c "
    source /opt/venv/bin/activate &&
    pip install --upgrade pip &&
    pip install numpy tqdm python-dotenv markdown beautifulsoup4 lxml openai faiss-cpu transformers datasets huggingface_hub tokenizers accelerate peft trl
"

echo "All containers configured successfully."

clear
sudo docker exec -it pytorch-rocm bash