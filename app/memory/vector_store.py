import hashlib
import math
import re
from pathlib import Path

from app.core.config import settings
from app.rag.document_loader import chunk_text, load_document_text


def tokenize(text: str) -> list[str]:
    return re.findall(r"[a-zA-Z0-9]+", text.lower())


class VectorStore:
    def __init__(self, embedding_dim: int = 384, db_name: str = "my_clean_db"):
        self.embedding_dim = embedding_dim
        self.embedding_model = None
        self.embedding_backend = "HashEmbeddings"

        # 🔥 FIX: specific DB folder load karega
        self.db_path = Path(settings.DOCUMENTS_DIR) / db_name

        self.documents = self._load_documents()
        self.faiss_index = None
        self._use_faiss = False

        self._load_embedding_model()
        self._build_faiss_index()

    def _load_documents(self) -> list[dict]:
        self.db_path.mkdir(parents=True, exist_ok=True)

        loaded = []

        supported_files = [
            path
            for path in self.db_path.rglob("*")
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

        # ❌ NO DEFAULT DATA
        return loaded

    def _score(self, query: str, content: str) -> float:
        query_tokens = tokenize(query)
        content_tokens = tokenize(content)

        if not query_tokens or not content_tokens:
            return 0.0

        query_freq = {t: query_tokens.count(t) for t in set(query_tokens)}
        content_freq = {t: content_tokens.count(t) for t in set(content_tokens)}

        common = set(query_freq) & set(content_freq)

        dot = sum(query_freq[t] * content_freq[t] for t in common)
        q_norm = math.sqrt(sum(v * v for v in query_freq.values()))
        c_norm = math.sqrt(sum(v * v for v in content_freq.values()))

        if q_norm == 0 or c_norm == 0:
            return 0.0

        return dot / (q_norm * c_norm)

    def _load_embedding_model(self) -> None:
        if not settings.ENABLE_SEMANTIC_EMBEDDINGS:
            return

        try:
            from sentence_transformers import SentenceTransformer

            self.embedding_model = SentenceTransformer(settings.EMBEDDING_MODEL)
            dim = self.embedding_model.get_sentence_embedding_dimension()
            if dim:
                self.embedding_dim = int(dim)

            self.embedding_backend = f"SentenceTransformers:{settings.EMBEDDING_MODEL}"

        except Exception:
            self.embedding_model = None
            self.embedding_backend = "HashEmbeddings"

    def _embed(self, text: str) -> list[float]:
        if self.embedding_model:
            return self.embedding_model.encode(text, normalize_embeddings=True).tolist()

        # fallback hashing
        vec = [0.0] * self.embedding_dim
        tokens = tokenize(text)

        for token in tokens:
            h = hashlib.md5(token.encode()).hexdigest()
            idx = int(h[:8], 16) % self.embedding_dim
            sign = 1 if int(h[8:10], 16) % 2 == 0 else -1
            vec[idx] += sign

        norm = math.sqrt(sum(v * v for v in vec))
        return [v / norm for v in vec] if norm else vec

    def _build_faiss_index(self):
        try:
            import faiss
            import numpy as np
        except:
            return

        if not self.documents:
            return

        embeddings = [self._embed(doc["content"]) for doc in self.documents]
        matrix = np.array(embeddings, dtype="float32")

        index = faiss.IndexFlatIP(self.embedding_dim)
        index.add(matrix)

        self.faiss_index = index
        self._use_faiss = True

    def search(self, query: str, limit: int = 3) -> list[dict]:
        if self._use_faiss:
            import numpy as np

            q = np.array([self._embed(query)], dtype="float32")
            scores, idxs = self.faiss_index.search(q, limit)

            results = []
            for s, i in zip(scores[0], idxs[0]):
                if i >= 0:
                    results.append(
                        {**self.documents[int(i)], "score": round(float(s), 4)}
                    )
            return results

        # fallback local
        ranked = []
        for doc in self.documents:
            score = self._score(query, doc["content"])
            ranked.append({**doc, "score": round(score, 4)})

        ranked.sort(key=lambda x: x["score"], reverse=True)
        return ranked[:limit]

    @property
    def backend_name(self):
        return "FAISS" if self._use_faiss else "LocalSimilarity"