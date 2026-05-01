from typing import TypedDict

from app.rag.adaptive_router import classify_query
from app.rag.generator_v2 import generate_answer, generator_backend
from app.rag.retriever import retrieve_documents, vector_store_backend


class RAGState(TypedDict):
    question: str
    rewritten_question: str
    route: str
    documents: list[dict]
    answer: str
    sources: list[str]
    needs_rewrite: bool
    attempts: int
    vector_backend: str
    llm_backend: str


def route_question(state: RAGState) -> RAGState:
    state["route"] = classify_query(state["question"])
    state["rewritten_question"] = state["question"]
    state["attempts"] = 0
    state["needs_rewrite"] = False
    state["vector_backend"] = vector_store_backend()
    state["llm_backend"] = generator_backend()
    return state


def retrieve_context(state: RAGState) -> RAGState:
    limit = 5 if state["route"] == "complex" else 3
    query = state.get("rewritten_question") or state["question"]
    state["documents"] = retrieve_documents(query, limit=limit)
    state["sources"] = [doc["source"] for doc in state["documents"]]
    return state


def grade_documents(state: RAGState) -> RAGState:
    min_score = 0.08 if state["route"] == "complex" else 0.04
    best_score = max((doc.get("score", 0.0) for doc in state["documents"]), default=0.0)
    state["needs_rewrite"] = best_score < min_score and state["attempts"] < 1
    return state


def rewrite_question(state: RAGState) -> RAGState:
    state["attempts"] += 1
    state["rewritten_question"] = (
        f"{state['question']} adaptive RAG LangGraph FastAPI Streamlit vector search"
    )
    return state


def generate_response(state: RAGState) -> RAGState:
    state["answer"] = generate_answer(
        question=state["question"],
        documents=state["documents"],
        route=state["route"],
    )
    return state


def decide_after_grading(state: RAGState) -> str:
    if state["needs_rewrite"]:
        return "rewrite"
    return "generate"


def _run_without_langgraph(question: str) -> RAGState:
    state: RAGState = {
        "question": question,
        "rewritten_question": question,
        "route": "simple",
        "documents": [],
        "answer": "",
        "sources": [],
        "needs_rewrite": False,
        "attempts": 0,
        "vector_backend": vector_store_backend(),
        "llm_backend": generator_backend(),
    }
    state = route_question(state)
    state = retrieve_context(state)
    state = grade_documents(state)
    if decide_after_grading(state) == "rewrite":
        state = rewrite_question(state)
        state = retrieve_context(state)
        state = grade_documents(state)
    state = generate_response(state)
    return state


def _build_langgraph_app():
    try:
        from langgraph.graph import END, StateGraph
    except Exception:
        return None

    workflow = StateGraph(RAGState)
    workflow.add_node("router", route_question)
    workflow.add_node("retriever", retrieve_context)
    workflow.add_node("grader", grade_documents)
    workflow.add_node("rewriter", rewrite_question)
    workflow.add_node("generator", generate_response)

    workflow.set_entry_point("router")
    workflow.add_edge("router", "retriever")
    workflow.add_edge("retriever", "grader")
    workflow.add_conditional_edges(
        "grader",
        decide_after_grading,
        {
            "rewrite": "rewriter",
            "generate": "generator",
        },
    )
    workflow.add_edge("rewriter", "retriever")
    workflow.add_edge("generator", END)
    return workflow.compile()


_GRAPH_APP = _build_langgraph_app()


def run_adaptive_rag(question: str) -> dict:
    if _GRAPH_APP is None:
        state = _run_without_langgraph(question)
    else:
        state = _GRAPH_APP.invoke(
            {
                "question": question,
                "rewritten_question": question,
                "route": "simple",
                "documents": [],
                "answer": "",
                "sources": [],
                "needs_rewrite": False,
                "attempts": 0,
                "vector_backend": vector_store_backend(),
                "llm_backend": generator_backend(),
            }
        )

    return {
        "question": state["question"],
        "route": state["route"],
        "answer": state["answer"],
        "sources": state["sources"],
        "rewritten_question": state["rewritten_question"],
        "self_correction_attempts": state["attempts"],
        "vector_backend": state.get("vector_backend", vector_store_backend()),
        "llm_backend": state.get("llm_backend", generator_backend()),
    }
