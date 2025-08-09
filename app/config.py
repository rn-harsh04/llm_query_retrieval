import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
    PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
    PINECONE_INDEX_NAME = "policy-index"
    EMBEDDING_MODEL = "all-MiniLM-L6-v2"
    LLM_MODEL = "deepseek/deepseek-chat-v3-0324:free"
    OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"
    SITE_URL = "http://localhost:8000"
    SITE_NAME = "LLM Query Retrieval"
