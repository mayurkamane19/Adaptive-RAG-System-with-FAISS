COMPLEX_KEYWORDS = {
    "compare",
    "explain",
    "architecture",
    "workflow",
    "difference",
    "advantages",
    "disadvantages",
    "step by step",
    "detailed",
    "complex",
    "why",
    "how",
}


def classify_query(question: str) -> str:
    text = question.lower().strip()
    word_count = len(text.split())

    if word_count > 12:
        return "complex"

    if any(keyword in text for keyword in COMPLEX_KEYWORDS):
        return "complex"

    return "simple"
