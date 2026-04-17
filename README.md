# Adaptive RAG System

AI POC architecture using Adaptive RAG, LangGraph, FastAPI, and Streamlit.

Now includes:

- FAISS vector search integration with local fallback
- SentenceTransformer embeddings for real semantic retrieval
- PDF/TXT/MD/CSV document loading and chunking
- Full LangGraph workflow with router, retriever, grader, rewriter, and generator
- Self-correction loop when retrieved context is weak

## Project Structure

```text
adaptive-rag-system/
|
|-- app/
|   |-- main.py                  # FastAPI app
|
|   |-- graph/
|   |   |-- langgraph_flow.py    # Full LangGraph workflow
|
|   |-- rag/
|   |   |-- retriever.py         # Vector search
|   |   |-- generator.py         # LLM response
|   |   |-- adaptive_router.py   # Simple vs Complex logic
|
|   |-- memory/
|   |   |-- vector_store.py      # FAISS vector store with fallback
|
|   |-- api/
|   |   |-- routes.py            # API endpoints
|
|   |-- core/
|   |   |-- config.py
|   |   |-- llm.py
|
|-- frontend/
|   |-- streamlit_app.py         # UI
|
|-- data/
|   |-- documents/               # PDFs / data
|
|-- tests/
|   |-- test_rag.py
|
|-- requirements.txt
|-- README.md
```

## Setup

```bash
cd adaptive-rag-system
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

## Run FastAPI Backend

```bash
uvicorn app.main:app --reload
```

Open API docs:

```text
http://127.0.0.1:8000/docs
```

## Run Streamlit Frontend

Open a second terminal:

```bash
streamlit run frontend/streamlit_app.py
```

## API Example

```bash
curl -X POST "http://127.0.0.1:8000/ask" ^
  -H "Content-Type: application/json" ^
  -d "{\"question\":\"Explain adaptive RAG architecture\"}"
```

## Optional OpenAI Setup

Without an API key, the project uses a local fallback response.

To use OpenAI:

```bash
set OPENAI_API_KEY=your_api_key_here
set OPENAI_MODEL=gpt-4o-mini
```

## Test

```bash
pytest
```

## Full LangGraph Flow

```text
User Question
    |
    v
Router
    |
    v
Retriever
    |
    v
Document Grader
    |
    |-- weak context --> Query Rewriter --> Retriever
    |
    v
Generator
    |
    v
Final Answer
```

## FAISS Integration

The vector store tries to use `faiss-cpu` automatically. If FAISS is not installed, the project still runs using local cosine similarity.

For real RAG, keep documents inside:

```text
data/documents/
```

Supported files:

```text
.txt, .md, .csv, .pdf
```

The project chunks documents, embeds them with SentenceTransformers, indexes them in FAISS, and retrieves top matching chunks for generation.

```python
from app.memory.vector_store import VectorStore

store = VectorStore()
docs = store.search("Explain adaptive RAG", limit=3)
print(store.backend_name)
print(docs)
```

To enable real semantic embeddings:

```bash
set ENABLE_SEMANTIC_EMBEDDINGS=true
set EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
```

If semantic embeddings are disabled, the app still runs with FAISS plus local hash embeddings for offline demos.

## Project Summary

This project demonstrates an adaptive RAG pipeline:

- User query enters through FastAPI or Streamlit
- Adaptive router classifies the query as simple or complex
- FAISS retriever fetches relevant context from the local knowledge base
- Document grader checks whether the retrieved context is strong enough
- Query rewriter performs one self-correction pass when retrieval is weak
- Generator creates the final answer
- LangGraph workflow orchestrates the complete process
