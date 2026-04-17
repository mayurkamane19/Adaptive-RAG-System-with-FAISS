from pydantic import BaseModel, Field
from fastapi import APIRouter

from app.graph.langgraph_flow import run_adaptive_rag


router = APIRouter(tags=["Adaptive RAG"])


class QueryRequest(BaseModel):
    question: str = Field(..., min_length=2, examples=["What is adaptive RAG?"])


class QueryResponse(BaseModel):
    question: str
    route: str
    answer: str
    sources: list[str]
    rewritten_question: str
    self_correction_attempts: int
    vector_backend: str


@router.post("/ask", response_model=QueryResponse)
def ask_question(payload: QueryRequest):
    result = run_adaptive_rag(payload.question)
    return QueryResponse(**result)
