from app.memory.vector_store import VectorStore


_STORE = VectorStore()


def retrieve_documents(query: str, limit: int = 3) -> list[dict]:
    return _STORE.search(query=query, limit=limit)


def vector_store_backend() -> str:
    return _STORE.backend_name
