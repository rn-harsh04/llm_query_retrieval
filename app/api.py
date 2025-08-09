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

app = FastAPI()
security = HTTPBearer()

class QueryRequest(BaseModel):
    documents: str
    questions: List[str]

class QueryResponse(BaseModel):
    answers: List[str]

def verify_token(credentials: HTTPAuthorizationCredentials = Security(security)):
    expected_token = "898075d0812fb3570314b282ad2c4dbed819c0413f21a2dc54f74a3f8e061b3c"
    if credentials.credentials != expected_token:
        raise HTTPException(status_code=401, detail="Invalid token")
    return credentials.credentials

@app.post("/hackrx/run", response_model=QueryResponse)
async def run_query(request: QueryRequest, token: str = Depends(verify_token)):
    db = get_db()
    try:
        vector_search = VectorSearch()
        llm_processor = LLMProcessor()

        # Parse document
        document_text = await parse_document(request.documents)
        if not document_text:
            raise HTTPException(status_code=400, detail="Failed to parse document")

        # Split into chunks
        chunks = split_text(document_text)

        # Generate embeddings and index
        document_id = str(uuid.uuid4())
        embeddings = [vector_search.embed_text(chunk) for chunk in chunks]
        vector_search.index_document(document_id, chunks, embeddings)
        db.store_chunks(document_id, chunks, embeddings)

        # Answer each question
        answers = []
        for question in request.questions:
            query_embedding = vector_search.embed_text(question)
            context_chunks = vector_search.search(query_embedding, top_k=5)
            context = " ".join(context_chunks)
            answer = llm_processor.parse_query(question, context)
            answers.append(answer)

        return QueryResponse(answers=answers)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing request: {str(e)}")
    finally:
        db.close()
