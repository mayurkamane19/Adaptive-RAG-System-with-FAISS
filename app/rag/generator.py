from app.core.llm import generate_with_llm


def _format_context(documents: list[dict]) -> str:
    """Convert retrieved docs into clean context string"""
    if not documents:
        return "No relevant documents found."

    formatted_chunks = []
    for doc in documents:
        source = doc.get("source", "unknown")
        content = doc.get("content", "").strip()

        if content:
            formatted_chunks.append(f"[{source}]\n{content}")

    return "\n\n".join(formatted_chunks)


def _fallback_answer(question: str, documents: list[dict], route: str) -> str:
    """Fallback if LLM fails"""
    context = _format_context(documents)

    return (
        "⚠️ LLM not available. Showing retrieved context.\n\n"
        f"Question: {question}\n\n"
        f"{context}"
    )


def generate_answer(question: str, documents: list[dict], route: str) -> str:
    """Main answer generator using LLM"""

    # 🚫 no docs case
    if not documents:
        return "No relevant information found in the document."

    context = _format_context(documents)

    question_lower = question.lower()

    # 🔥 smart instruction selection
    if any(word in question_lower for word in ["summarize", "summary", "key points"]):
        instruction = "Summarize the context into 5-7 clear bullet points."
    elif route == "complex":
        instruction = "Provide a detailed, well-structured answer."
    else:
        instruction = "Provide a short and clear answer."

    # 🔥 improved prompt (VERY IMPORTANT)
    prompt = f"""
You are a smart AI assistant using RAG.

Rules:
- Use ONLY the given context
- Do NOT copy full text
- Extract important information only
- Keep answer clean and structured
- If not found, say: Not enough information

{instruction}

Question:
{question}

Context:
{context}

Answer:
"""

    try:
        llm_answer = generate_with_llm(prompt)

        # ✅ strict validation
        if (
            llm_answer
            and isinstance(llm_answer, str)
            and len(llm_answer.strip()) > 20
        ):
            return llm_answer.strip()

    except Exception as e:
        print("LLM Error:", e)

    # 🔁 fallback
    return _fallback_answer(question, documents, route)