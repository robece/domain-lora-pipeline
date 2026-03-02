#!/bin/bash
set -e

rm -rf /home/robece/Documents/eventgrid-expert/api/temp
mkdir /home/robece/Documents/eventgrid-expert/api/temp
mkdir /home/robece/Documents/eventgrid-expert/api/temp/models

cp /home/robece/Documents/eventgrid-expert/data/faiss.index \
   /home/robece/Documents/eventgrid-expert/api/temp/faiss.index

cp /home/robece/Documents/eventgrid-expert/data/embeddings_metadata.jsonl \
   /home/robece/Documents/eventgrid-expert/api/temp/embeddings_metadata.jsonl

cp /home/robece/Documents/eventgrid-expert/data/corpus_clean.jsonl \
   /home/robece/Documents/eventgrid-expert/api/temp/corpus_clean.jsonl

cp -r /home/robece/Documents/eventgrid-expert/models/qwen2.5-3b-lora-eventgrid \
      /home/robece/Documents/eventgrid-expert/api/temp/models

echo "Building eventgrid-api image"
sudo docker compose build eventgrid-api

sudo docker compose up -d

sudo docker exec -it eventgrid-api bash