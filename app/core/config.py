import os
from dataclasses import dataclass
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parents[2]


@dataclass(frozen=True)
class Settings:
    PROJECT_NAME: str = "Adaptive RAG System"
    DOCUMENTS_DIR: str = str(BASE_DIR / "data" / "documents")
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    OPENAI_MODEL: str = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    ENABLE_SEMANTIC_EMBEDDINGS: bool = (
        os.getenv("ENABLE_SEMANTIC_EMBEDDINGS", "false").lower() == "true"
    )
    EMBEDDING_MODEL: str = os.getenv(
        "EMBEDDING_MODEL",
        "sentence-transformers/all-MiniLM-L6-v2",
    )


settings = Settings()
