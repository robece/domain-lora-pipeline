FROM rocm/pytorch:rocm7.2_ubuntu24.04_py3.12_pytorch_release_2.9.1

# Instalar dependencias necesarias
RUN pip install --upgrade pip && \
    pip install fastapi uvicorn transformers peft accelerate huggingface_hub faiss-cpu openai numpy

# Crear directorio de trabajo
WORKDIR /workspace

# Copiar el servidor
COPY server.py /workspace/server.py

# Crear carpeta data dentro de la imagen 
RUN mkdir -p /workspace/data
RUN mkdir -p /workspace/models

# Copiar SOLO los archivos necesarios 
COPY temp/corpus_clean.jsonl /workspace/data/corpus_clean.jsonl
COPY temp/embeddings_metadata.jsonl /workspace/data/embeddings_metadata.jsonl
COPY temp/faiss.index /workspace/data/faiss.index
COPY temp/models/ /workspace/models/

# Exponer puerto
EXPOSE 8000

# Comando por defecto
CMD ["uvicorn", "server:app", "--host", "0.0.0.0", "--port", "8000"]
