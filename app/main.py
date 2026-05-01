from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from app.api.routes import router
from app.core.config import settings
from app.services.saas_store import initialize_saas_db

# 👉 RAG import (adjust if needed)
try:
    from app.rag.pipeline import query_rag
except:
    query_rag = None


app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Adaptive RAG system with Chat/Ask AI feature",
    version="1.1.0",
)

# ✅ CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=list(settings.CORS_ORIGINS) or ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✅ Existing routes
app.include_router(router)


# ✅ Startup
@app.on_event("startup")
def startup_event():
    initialize_saas_db()


# ✅ Request Model
class QueryRequest(BaseModel):
    question: str


# 🚀 NEW: Ask AI Endpoint
@app.post("/ask")
async def ask_question(request: QueryRequest):
    try:
        if query_rag:
            answer = query_rag(request.question)
        else:
            answer = f"AI (fallback): {request.question}"

        return {
            "status": "success",
            "question": request.question,
            "answer": answer,
        }

    except Exception as e:
        return {
            "status": "error",
            "message": str(e),
        }


# ✅ Root
@app.get("/")
def root():
    return {
        "message": "Adaptive RAG System is running 🚀",
        "docs": "/docs",
        "ask_endpoint": "/ask",
    }


# ✅ Health check
@app.get("/health")
def health():
    return {"status": "ok"}