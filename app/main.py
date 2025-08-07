from fastapi import FastAPI
from app.api import router

app = FastAPI(
    title="LLM-Powered Query System",
    description="Query policy documents using LLM and semantic search",
    version="1.0"
)

app.include_router(router, prefix="/api/v1")
