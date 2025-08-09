import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
    PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
    PINECONE_INDEX_NAME = os.getenv("PINECONE_INDEX_NAME", "policy-index")
    # Hugging Face model used for embeddings via Inference API
    HF_EMBEDDING_MODEL = os.getenv("HF_EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2")
    HF_API_KEY = os.getenv("HF_API_KEY")
    LLM_MODEL = os.getenv("LLM_MODEL", "deepseek/deepseek-chat-v3-0324:free")
    OPENROUTER_BASE_URL = os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1")
    SITE_URL = os.getenv("SITE_URL", "https://your-app-name.onrender.com")  # set on Render env
    SITE_NAME = os.getenv("SITE_NAME", "LLM Query Retrieval")
