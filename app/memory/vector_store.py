import hashlib
import math
import re
from pathlib import Path

from app.core.config import settings
from app.rag.document_loader import chunk_text, load_document_text


DEFAULT_DOCUMENTS = [
    {
        "source": "adaptive-rag-overview",
        "content": "Adaptive RAG routes simple questions to lightweight retrieval and complex questions to deeper multi-document retrieval before generation.",
    },
    {
        "source": "langgraph-workflow",
        "content": "LangGraph orchestrates the workflow with router, retriever, and generator nodes. The graph can support self-correction and feedback loops.",
    },
    {
        "source": "fastapi-layer",
        "content": "FastAPI exposes the RAG workflow through API endpoints. A user sends a question and receives route, answer, and source documents.",
    },
    {
        "source": "streamlit-ui",
        "content": "Streamlit provides a simple user interface for asking questions and displaying generated responses from the FastAPI backend.",
    },
    {
        "source": "vector-search",
        "content": "Vector search retrieves relevant knowledge base chunks. This project uses a lightweight local similarity store for easy demo execution.",
    },
]


def tokenize(text: str) -> list[str]:
    return re.findall(r"[a-zA-Z0-9]+", text.lower())


class VectorStore:
    def __init__(self, embedding_dim: int = 384):
        self.embedding_dim = embedding_dim
        self.embedding_model = None
        self.embedding_backend = "HashEmbeddings"
        self.documents = self._load_documents()
        self.faiss_index = None
        self._use_faiss = False
        self._load_embedding_model()
        self._build_faiss_index()

    def _load_documents(self) -> list[dict]:
        docs_path = Path(settings.DOCUMENTS_DIR)
        docs_path.mkdir(parents=True, exist_ok=True)

        loaded = []
        supported_files = [
            path
            for path in docs_path.rglob("*")
            if path.is_file() and path.suffix.lower() in {".txt", ".md", ".csv", ".pdf"}
        ]

        for path in supported_files:
            content = load_document_text(path)
            for chunk_index, chunk in enumerate(chunk_text(content), start=1):
                loaded.append(
                    {
                        "source": f"{path.name}#chunk-{chunk_index}",
                        "content": chunk,
                    }
                )

        return loaded or DEFAULT_DOCUMENTS

    def _score(self, query: str, content: str) -> float:
        query_tokens = tokenize(query)
        content_tokens = tokenize(content)

        if not query_tokens or not content_tokens:
            return 0.0

        query_freq = {token: query_tokens.count(token) for token in set(query_tokens)}
        content_freq = {token: content_tokens.count(token) for token in set(content_tokens)}
        common_tokens = set(query_freq) & set(content_freq)

        dot = sum(query_freq[token] * content_freq[token] for token in common_tokens)
        query_norm = math.sqrt(sum(value * value for value in query_freq.values()))
        content_norm = math.sqrt(sum(value * value for value in content_freq.values()))

        if query_norm == 0 or content_norm == 0:
            return 0.0

        return dot / (query_norm * content_norm)

    def _load_embedding_model(self) -> None:
        if not settings.ENABLE_SEMANTIC_EMBEDDINGS:
            self.embedding_model = None
            self.embedding_backend = "HashEmbeddings"
            return

        try:
            from sentence_transformers import SentenceTransformer
        except Exception:
            self.embedding_model = None
            self.embedding_backend = "HashEmbeddings"
            return

        try:
            self.embedding_model = SentenceTransformer(settings.EMBEDDING_MODEL)
            model_dim = self.embedding_model.get_sentence_embedding_dimension()
            if model_dim:
                self.embedding_dim = int(model_dim)
            self.embedding_backend = f"SentenceTransformers:{settings.EMBEDDING_MODEL}"
        except Exception:
            self.embedding_model = None
            self.embedding_backend = "HashEmbeddings"

    def _embed_with_sentence_transformers(self, text: str) -> list[float] | None:
        if self.embedding_model is None:
            return None

        vector = self.embedding_model.encode(
            text,
            normalize_embeddings=True,
            show_progress_bar=False,
        )
        return vector.tolist()

    def _embed_with_hashing(self, text: str) -> list[float]:
        vector = [0.0] * self.embedding_dim
        tokens = tokenize(text)

        if not tokens:
            return vector

        for token in tokens:
            digest = hashlib.md5(token.encode("utf-8")).hexdigest()
            index = int(digest[:8], 16) % self.embedding_dim
            sign = 1.0 if int(digest[8:10], 16) % 2 == 0 else -1.0
            vector[index] += sign

        norm = math.sqrt(sum(value * value for value in vector))
        if norm == 0:
            return vector

        return [value / norm for value in vector]

    def _embed(self, text: str) -> list[float]:
        semantic_vector = self._embed_with_sentence_transformers(text)
        if semantic_vector is not None:
            return semantic_vector

        return self._embed_with_hashing(text)

    def _build_faiss_index(self) -> None:
        try:
            import faiss
            import numpy as np
        except Exception:
            self._use_faiss = False
            return

        embeddings = [self._embed(document["content"]) for document in self.documents]
        if not embeddings:
            self._use_faiss = False
            return

        matrix = np.array(embeddings, dtype="float32")
        index = faiss.IndexFlatIP(self.embedding_dim)
        index.add(matrix)

        self.faiss_index = index
        self._use_faiss = True

    def _search_with_faiss(self, query: str, limit: int) -> list[dict]:
        import numpy as np

        query_vector = np.array([self._embed(query)], dtype="float32")
        scores, indexes = self.faiss_index.search(query_vector, limit)

        results = []
        for score, index in zip(scores[0], indexes[0]):
            if index < 0:
                continue
            results.append({**self.documents[int(index)], "score": round(float(score), 4)})

        return results

    def _search_with_local_similarity(self, query: str, limit: int) -> list[dict]:
        ranked = []
        for document in self.documents:
            score = self._score(query, document["content"])
            ranked.append({**document, "score": round(score, 4)})

        ranked.sort(key=lambda item: item["score"], reverse=True)
        return ranked[:limit]

    def search(self, query: str, limit: int = 3) -> list[dict]:
        if self._use_faiss and self.faiss_index is not None:
            return self._search_with_faiss(query, limit)

        return self._search_with_local_similarity(query, limit)

    @property
    def backend_name(self) -> str:
        vector_backend = "FAISS" if self._use_faiss else "LocalSimilarity"
        return f"{vector_backend} + {self.embedding_backend}"
