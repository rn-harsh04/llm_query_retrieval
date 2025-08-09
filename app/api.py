import os
from fastapi import FastAPI, HTTPException, Depends, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from typing import List
import uuid
from app.utils.document_parser import parse_document
from app.utils.text_splitter import split_text
from app.utils.search import VectorSearch
from app.utils.llm import LLMProcessor
from app.utils.db import get_db
from app.config import Config

app = FastAPI()
security = HTTPBearer()

class QueryRequest(BaseModel):
    documents: str
    questions: List[str]

class QueryResponse(BaseModel):
    answers: List[str]

def verify_token(credentials: HTTPAuthorizationCredentials = Security(security)):
    expected_token = os.getenv("HACKRX_TOKEN") or "898075d0812fb3570314b282ad2c4dbed819c0413f21a2dc54f74a3f8e061b3c"
    if credentials.credentials != expected_token:
        raise HTTPException(status_code=401, detail="Invalid token")
    return credentials.credentials

@app.on_event("startup")
async def startup_event():
    """Prepare Pinecone index and do a small warmup call to HF to ensure external API reachable."""
    try:
        app.state.vector_search = VectorSearch()
        # small HF warmup (short text) to ensure HF key works and pipeline responsive
        try:
            _ = app.state.vector_search.embed_text("warmup " * 10)
            print("✅ HF embedding warmup success")
        except Exception as e:
            print(f"⚠️ HF warmup failed: {e}")
        # preload llm client but don't call heavy model
        app.state.llm = LLMProcessor()
        print("✅ VectorSearch and LLM initialized (lightly)")
    except Exception as e:
        # log and continue; requests will fail with errors but app will be up
        print(f"Startup init warning: {e}")

@app.post("/hackrx/run", response_model=QueryResponse)
async def run_query(request: QueryRequest, token: str = Depends(verify_token)):
    # Validate input
    if not request.documents or not request.questions:
        raise HTTPException(status_code=400, detail="Missing documents or questions")

    # parse document (downloads & extracts text)
    try:
        document_text = await parse_document(request.documents)
        if not document_text:
            raise HTTPException(status_code=400, detail="Failed to parse document")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Document parsing failed: {e}")

    chunks = split_text(document_text)
    if not chunks:
        raise HTTPException(status_code=400, detail="No text extracted from document")

    # Ensure vector_search exists
    vector_search = getattr(app.state, "vector_search", None)
    if vector_search is None:
        vector_search = VectorSearch()
        app.state.vector_search = vector_search

    llm_processor = getattr(app.state, "llm", None)
    if llm_processor is None:
        llm_processor = LLMProcessor()
        app.state.llm = llm_processor

    # stream index & store to DB chunk-by-chunk (no large lists)
    db = get_db()
    document_id = str(uuid.uuid4())
    try:
        # index to Pinecone in streaming batches
        vector_search.index_document_stream(document_id, chunks, batch_size=10)

        # store embeddings per chunk by re-requesting embedding per chunk (keeps memory small)
        # NOTE: we could store embeddings returned during indexing but HF embed calls are idempotent & fast
        for i, chunk in enumerate(chunks):
            emb = vector_search.embed_text(chunk)
            db.store_chunk(f"{document_id}_{i}", chunk, emb)

        # Answer questions
        answers = []
        for question in request.questions:
            q_emb = vector_search.embed_text(question)
            context_chunks = vector_search.search(q_emb, top_k=5)
            context = " ".join(context_chunks)
            ans = llm_processor.parse_query(question, context)
            answers.append(ans)

        return QueryResponse(answers=answers)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Processing failed: {str(e)}")
    finally:
        try:
            db.close()
        except Exception:
            pass

@app.get("/health")
async def health_check():
    return {"status": "ok"}
