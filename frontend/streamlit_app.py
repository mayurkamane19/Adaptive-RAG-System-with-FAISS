import requests
import streamlit as st


API_URL = "http://127.0.0.1:8000/ask"


st.set_page_config(page_title="Adaptive RAG System", page_icon="AI", layout="wide")

st.title("Adaptive RAG System")
st.caption("LangGraph + FastAPI + Streamlit proof of concept")

question = st.text_area(
    "Ask a question",
    value="Explain adaptive RAG architecture with FastAPI and Streamlit.",
    height=120,
)

if st.button("Generate Answer", type="primary"):
    if not question.strip():
        st.warning("Please enter a question.")
    else:
        with st.spinner("Running adaptive RAG workflow..."):
            try:
                response = requests.post(API_URL, json={"question": question}, timeout=30)
                response.raise_for_status()
                data = response.json()

                col1, col2 = st.columns([1, 3])
                with col1:
                    st.metric("Route", data["route"].title())
                    st.metric("Self-Correction", data["self_correction_attempts"])
                    st.write("Vector Backend")
                    st.code(data["vector_backend"])
                    if data["rewritten_question"] != data["question"]:
                        st.write("Rewritten Query")
                        st.code(data["rewritten_question"])
                    st.write("Sources")
                    for source in data["sources"]:
                        st.code(source)

                with col2:
                    st.subheader("Answer")
                    st.write(data["answer"])
            except requests.RequestException as exc:
                st.error(f"FastAPI backend is not running or returned an error: {exc}")

st.divider()
st.write("Run backend:")
st.code("uvicorn app.main:app --reload", language="bash")
st.write("Run frontend:")
st.code("streamlit run frontend/streamlit_app.py", language="bash")
