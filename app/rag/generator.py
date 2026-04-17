from app.core.llm import generate_with_llm


def _format_context(documents: list[dict]) -> str:
    if not documents:
        return "No matching documents found."

    return "\n\n".join(
        f"Source: {doc['source']}\nContent: {doc['content']}"
        for doc in documents
    )


def _fallback_answer(question: str, documents: list[dict], route: str) -> str:
    context = _format_context(documents)
    style = "short and direct" if route == "simple" else "detailed and structured"
    return (
        f"Route selected: {route}.\n\n"
        f"Question: {question}\n\n"
        f"Generated a {style} answer using retrieved context:\n\n"
        f"{context}"
    )


def generate_answer(question: str, documents: list[dict], route: str) -> str:
    context = _format_context(documents)
    prompt = f"""
You are an adaptive RAG assistant.
Answer the user question using only the context.

Route: {route}
Question: {question}

Context:
{context}
"""

    llm_answer = generate_with_llm(prompt)
    if llm_answer:
        return llm_answer

    return _fallback_answer(question, documents, route)
