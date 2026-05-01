from app.rag.adaptive_router import classify_query
from app.graph.langgraph_flow import run_adaptive_rag


def test_simple_query_route():
    assert classify_query("What is RAG?") == "simple"


def test_complex_query_route():
    assert classify_query("Explain adaptive RAG architecture step by step") == "complex"


def test_rag_response_shape():
    result = run_adaptive_rag("What is FastAPI used for?")

    assert result["question"]
    assert result["route"] in {"simple", "complex"}
    assert result["answer"]
    assert isinstance(result["sources"], list)
    assert "rewritten_question" in result
    assert "self_correction_attempts" in result
    assert "vector_backend" in result
    assert "llm_backend" in result
