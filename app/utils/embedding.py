import os
import faiss
import numpy as np
from dotenv import load_dotenv
from openai import OpenAI

# Load API key from .env
load_dotenv()
api_key = os.getenv("OPENROUTER_API_KEY")

# Initialize OpenRouter client
client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=api_key,
)

# Choose the model you want to use
# Check the exact name of supported embedding models from https://openrouter.ai/docs#models
EMBEDDING_MODEL = "openai/text-embedding-ada-002"  # or another compatible one
EMBEDDING_DIM = 1536

# Global vector index
index = faiss.IndexFlatL2(EMBEDDING_DIM)
doc_chunks = []
doc_embeddings = []

def get_embedding(text):
    try:
        response = client.embeddings.create(
            model=EMBEDDING_MODEL,
            input=text
        )
        return response.data[0].embedding
    except Exception as e:
        print("Embedding failed:", e)
        return [0.0] * EMBEDDING_DIM

def chunk_text(text, max_tokens=500):
    sentences = text.split('. ')
    chunks, current = [], ""
    for sentence in sentences:
        if len(current + sentence) < max_tokens:
            current += sentence + ". "
        else:
            chunks.append(current.strip())
            current = sentence + ". "
    if current:
        chunks.append(current.strip())
    return chunks

def embed_document(text):
    global doc_chunks, doc_embeddings
    chunks = chunk_text(text)
    embeddings = [get_embedding(chunk) for chunk in chunks]
    index.add(np.array(embeddings).astype("float32"))
    doc_chunks = chunks
    doc_embeddings = embeddings
