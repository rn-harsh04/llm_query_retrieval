from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.utils.document_parser import parse_document
from app.utils.embedding import embed_document
from app.utils.search import search_top_k
from app.utils.llm import query_llm
from app.utils.json_formatter import format_to_json

router = APIRouter()

class QueryRequest(BaseModel):
    documents: str
    questions: list[str]

@router.post("/hackrx/run")
def handle_query(data: QueryRequest):
    try:
        raw_text = parse_document(data.documents)
        embed_document(raw_text)

        answers = []
        for q in data.questions:
            context = "\n".join(search_top_k(q, k=3))
            response = query_llm(q, context)
            answers.append(response)

        return {"answers": answers}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
