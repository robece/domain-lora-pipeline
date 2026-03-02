[← Back to Home](../README.md)

## Table of Contents

- [21.1 Model loading and initialization](#211-model-loading-and-initialization)
- [21.2 Embedding generation using Azure OpenAI](#212-embedding-generation-using-azure-openai)
- [21.3 Loading FAISS, metadata, and corpus](#213-loading-faiss-metadata-and-corpus)
- [21.4 Retrieving context from FAISS](#214-retrieving-context-from-faiss)
- [21.5 Prompt construction](#215-prompt-construction)
- [21.6 Answer generation with the LoRA model](#216-answer-generation-with-the-lora-model)
- [21.7 Main API endpoint: /generate](#217-main-api-endpoint-generate)
- [21. 8 Health check endpoint](#21-8-health-check-endpoint)
- [21.9 Request logging](#219-request-logging)
- [21.10 Real‑world behavior and constraints](#2110-realworld-behavior-and-constraints)

# 21. Using the Trained LoRA Model Inside the Real RAG Server (server.py)

The FastAPI server is the final stage of the pipeline: it loads the
Qwen2.5‑3B‑Instruct base model, applies the LoRA adapter, connects to
Azure OpenAI embeddings, loads the FAISS index, and exposes a single RAG
endpoint that performs retrieval and grounded answer generation. This
section documents how the server works exactly as implemented in the
script.

## 21.1 Model loading and initialization

The server loads:

- the tokenizer from the base Qwen model

- the base model in BF16 on GPU (ROCm-compatible)

- the LoRA adapter stored in /workspace/models/qwen2.5-3b-lora-eventgrid

python

tokenizer = AutoTokenizer.from_pretrained(BASE_MODEL, use_fast=False)  
base_model = AutoModelForCausalLM.from_pretrained(BASE_MODEL,
dtype=torch.bfloat16, device_map="auto")  
model = PeftModel.from_pretrained(base_model, LORA_MODEL,
dtype=torch.bfloat16, device_map="auto")  
model.eval()  
  
This produces a fully functional model that incorporates the
domain‑specific training.

## 21.2 Embedding generation using Azure OpenAI

The server uses Azure OpenAI’s text-embedding-3-large model to embed
user questions. This is required because the FAISS index was built using
the same embedding model.

python

response = client.embeddings.create(  
model=AZURE_EMBEDDING_MODEL,  
input=t,  
)  
vec = np.array(response.data\[0\].embedding, dtype="float32")  
vec = vec / np.linalg.norm(vec)

The embeddings are normalized to match the FAISS index’s inner‑product
search.

## 21.3 Loading FAISS, metadata, and corpus

The server loads:

- faiss.index

- embeddings_metadata.jsonl

- corpus_clean.jsonl

exactly as produced by the pipeline.

python

index = faiss.read_index(FAISS_INDEX_PATH)  
metadata = \[json.loads(line) for line in open(METADATA_PATH)\]  
corpus = \[json.loads(line)\["text"\] for line in open(CORPUS_PATH)\]

The corpus is stored as a list of raw text chunks, aligned with FAISS
vector order.

## 21.4 Retrieving context from FAISS

The server embeds the question and retrieves the top‑k most relevant
chunks:

python

q_emb = embed_texts(\[question\])  
distances, indices = index.search(q_emb, top_k)  
return \[corpus\[idx\] for idx in indices\[0\]\]

This is a direct semantic search using the trained embeddings and index.

## 21.5 Prompt construction

The server builds a fixed prompt template that instructs the model to
answer **only** using the retrieved context:

Code

Instruction: Answer using only the provided context. Do not use external
knowledge.

Input:  
Context:  
\<contexts\>  
  
Question:  
\<question\>  
  
Answer:

This is the exact prompt used in the script.

## 21.6 Answer generation with the LoRA model

The server tokenizes the prompt and generates an answer using
deterministic decoding:

python

outputs = model.generate(  
\*\*inputs,  
max_new_tokens=500,  
temperature=0.2,  
top_p=0.9,  
repetition_penalty=1.1,  
do_sample=False,  
)

The output is decoded and trimmed so that only the text after "Answer:"
is returned (unless full_response=true).

## 21.7 Main API endpoint: /generate

The endpoint accepts:

json

{  
"question": "How does Event Grid handle custom topics?",  
"top_k": 5  
}

The server:

1.  Embeds the question

2.  Retrieves top‑k chunks

3.  Builds the prompt

4.  Generates the answer

5.  Logs the request

6.  Returns the final answer

The default response is:

json

{  
"question": "...",  
"answer": "..."  
}

If full_response=true, the server also returns:

- the retrieved contexts

- the full generated text

- the number of tokens allowed

This behavior is exactly as implemented.

## 21. 8 Health check endpoint

The /health endpoint simply returns:

json

{"status": "ok"}

This is used for monitoring and readiness checks.

## 21.9 Request logging

Every request is logged to /logs/requests.log with:

- timestamp

- client IP

- question

- answer

- top_k

- whether full_response was used

This provides traceability for debugging and auditing.

## 21.10 Real‑world behavior and constraints

The server behaves exactly as follows:

- It always performs retrieval before answering.

- It always uses Azure OpenAI embeddings.

- It always uses the FAISS index for context selection.

- It always uses the LoRA model for generation.

- It does not support streaming.

- It does not support authentication.

- It does not merge LoRA weights; it loads them dynamically.

- It does not expose additional endpoints beyond /generate and /health.

---
[← Back to Home](../README.md)
