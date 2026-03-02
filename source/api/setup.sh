#!/bin/bash
set -e

rm -rf temp/
mkdir temp/
mkdir temp/models
cp ../training/data/faiss.index temp/faiss.index
cp ../training/data/embeddings_metadata.jsonl temp/embeddings_metadata.jsonl
cp ../training/data/corpus_clean.jsonl temp/corpus_clean.jsonl
cp -r ../training/models/qwen2.5-3b-lora-eventgrid temp/models

echo "Building eventgrid-api image"
sudo docker compose build eventgrid-api

sudo docker compose up -d

sudo docker exec -it eventgrid-api bash