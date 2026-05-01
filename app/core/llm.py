from app.core.config import settings


def _generate_with_openai(prompt: str) -> str | None:
    if not settings.OPENAI_API_KEY or settings.LLM_PROVIDER not in {"auto", "openai"}:
        return None

    try:
        from openai import OpenAI

        client = OpenAI(api_key=settings.OPENAI_API_KEY)
        response = client.chat.completions.create(
            model=settings.OPENAI_MODEL,
            messages=[
                {"role": "system", "content": "You answer using retrieved context only."},
                {"role": "user", "content": prompt},
            ],
            temperature=0.2,
        )
        return response.choices[0].message.content
    except Exception as exc:
        print(f"OpenAI LLM error: {exc}")
        return None


def _generate_with_ollama(prompt: str) -> str | None:
    if settings.LLM_PROVIDER not in {"auto", "ollama"}:
        return None

    try:
        import requests

        response = requests.post(
            f"{settings.OLLAMA_BASE_URL}/api/generate",
            json={
                "model": settings.OLLAMA_MODEL,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.2,
                    "num_predict": 500,
                },
            },
            timeout=60,
        )
        response.raise_for_status()
        payload = response.json()
        return payload.get("response", "").strip() or None
    except Exception as exc:
        print(f"Ollama LLM error: {exc}")
        return None


def generate_with_llm(prompt: str) -> str | None:
    return _generate_with_openai(prompt) or _generate_with_ollama(prompt)


def llm_backend_name() -> str:
    if settings.LLM_PROVIDER == "auto" and settings.OPENAI_API_KEY:
        return f"Auto(OpenAI:{settings.OPENAI_MODEL} -> Ollama:{settings.OLLAMA_MODEL} -> OfflineExtractive)"

    if settings.LLM_PROVIDER == "auto":
        return f"Auto(Ollama:{settings.OLLAMA_MODEL} -> OfflineExtractive)"

    if settings.LLM_PROVIDER == "openai" and settings.OPENAI_API_KEY:
        return f"OpenAI:{settings.OPENAI_MODEL}"

    if settings.LLM_PROVIDER == "ollama":
        return f"Ollama:{settings.OLLAMA_MODEL}"

    return "OfflineExtractive"
