import os
from dataclasses import dataclass
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parents[2]


@dataclass(frozen=True)
class Settings:
    PROJECT_NAME: str = "Adaptive RAG System"
    DATA_DIR: str = str(BASE_DIR / "data")
    DOCUMENTS_DIR: str = str(BASE_DIR / "data" / "documents")
    API_HOST: str = os.getenv("API_HOST", "127.0.0.1")
    API_PORT: int = int(os.getenv("API_PORT", "8000"))
    CORS_ORIGINS: tuple[str, ...] = tuple(
        origin.strip()
        for origin in os.getenv(
            "CORS_ORIGINS",
            "http://localhost:5173,http://127.0.0.1:5173",
        ).split(",")
        if origin.strip()
    )
    LLM_PROVIDER: str = os.getenv("LLM_PROVIDER", "auto").lower()
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    OPENAI_MODEL: str = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    OLLAMA_BASE_URL: str = os.getenv("OLLAMA_BASE_URL", "http://127.0.0.1:11434")
    OLLAMA_MODEL: str = os.getenv("OLLAMA_MODEL", "llama3.2:3b")
    ENABLE_SEMANTIC_EMBEDDINGS: bool = (
        os.getenv("ENABLE_SEMANTIC_EMBEDDINGS", "false").lower() == "true"
    )
    EMBEDDING_MODEL: str = os.getenv(
        "EMBEDDING_MODEL",
        "sentence-transformers/all-MiniLM-L6-v2",
    )


settings = Settings()
