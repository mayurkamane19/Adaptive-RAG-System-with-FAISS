from pathlib import Path


def _read_pdf(path: Path) -> str:
    try:
        from pypdf import PdfReader
    except Exception:
        return ""

    reader = PdfReader(str(path))
    pages = [page.extract_text() or "" for page in reader.pages]
    return "\n".join(pages).strip()


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="ignore").strip()


def load_document_text(path: Path) -> str:
    suffix = path.suffix.lower()

    if suffix == ".pdf":
        return _read_pdf(path)

    if suffix in {".txt", ".md", ".csv"}:
        return _read_text(path)

    return ""


def chunk_text(text: str, chunk_size: int = 900, overlap: int = 150) -> list[str]:
    clean_text = " ".join(text.split())
    if not clean_text:
        return []

    chunks = []
    start = 0
    while start < len(clean_text):
        end = start + chunk_size
        chunks.append(clean_text[start:end])
        if end >= len(clean_text):
            break
        start = end - overlap

    return chunks
