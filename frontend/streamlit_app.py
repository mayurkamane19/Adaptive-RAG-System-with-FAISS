from pathlib import Path

import requests
import streamlit as st


API_URL = "http://127.0.0.1:8000/ask"
PROJECT_ROOT = Path(__file__).resolve().parents[1]
DOCUMENTS_DIR = PROJECT_ROOT / "data" / "documents"


st.set_page_config(page_title="RAG Chatbot", page_icon="RAG", layout="wide")


def inject_styles() -> None:
    st.markdown(
        """
        <style>
        :root {
            --app-bg: #0d111a;
            --sidebar-bg: #232631;
            --field-bg: #272a35;
            --border: #333846;
            --text: #f3f3f6;
            --muted: #b4b7c1;
        }

        .stApp {
            background: var(--app-bg);
            color: var(--text);
        }

        [data-testid="stSidebar"] {
            background: var(--sidebar-bg);
            border-right: 1px solid var(--border);
        }

        [data-testid="stSidebar"] * {
            color: var(--text);
        }

        [data-testid="stSidebar"] .stRadio > label {
            color: var(--muted);
            font-size: 20px;
            padding-top: 140px;
        }

        [data-testid="stSidebar"] [role="radiogroup"] label {
            border-radius: 5px;
            padding: 8px 12px;
            margin: 4px 0;
        }

        [data-testid="stSidebar"] [role="radiogroup"] label:has(input:checked) {
            background: #3a3b46;
        }

        h1 {
            font-size: 58px !important;
            line-height: 1.05 !important;
            letter-spacing: 0 !important;
            margin-bottom: 22px !important;
        }

        h2, h3, p, label, span, div {
            letter-spacing: 0 !important;
        }

        .main .block-container {
            max-width: 1120px;
            padding-top: 78px;
        }

        .subtitle {
            color: var(--text);
            font-size: 24px;
            margin-bottom: 30px;
        }

        [data-testid="stVerticalBlockBorderWrapper"] {
            border-color: var(--border) !important;
            border-radius: 8px !important;
            background: rgba(16, 20, 31, 0.78);
        }

        .section-title {
            font-size: 20px;
            font-weight: 700;
            margin-bottom: 12px;
        }

        [data-testid="stFileUploader"] section {
            min-height: 124px;
            background: var(--field-bg);
            border: 0;
            border-radius: 8px;
            padding: 16px;
        }

        [data-testid="stFileUploader"] button,
        .stButton button {
            border: 1px solid #424754;
            border-radius: 8px;
            background: #111721;
            color: var(--text);
            min-height: 50px;
            font-size: 22px;
        }

        .stButton button:hover {
            border-color: #626a7a;
            color: var(--text);
        }

        [data-testid="stTextInput"] input,
        [data-testid="stNumberInput"] input,
        [data-testid="stTextArea"] textarea,
        [data-baseweb="select"] > div {
            background: var(--field-bg);
            color: var(--text);
            border: 1px solid transparent;
            border-radius: 8px;
            min-height: 60px;
            font-size: 22px;
        }

        [data-testid="stNumberInput"] button {
            background: var(--field-bg);
            color: var(--text);
            border: 0;
        }

        .stAlert {
            background: #1b2433;
            border: 1px solid #34445f;
            color: var(--text);
        }

        code {
            white-space: pre-wrap;
        }

        .deploy-text {
            position: fixed;
            right: 76px;
            top: 28px;
            color: var(--text);
            font-size: 20px;
            font-weight: 600;
            z-index: 99;
        }
        </style>
        <div class="deploy-text">Deploy &vellip;</div>
        """,
        unsafe_allow_html=True,
    )


def save_uploaded_documents(uploaded_files: list, vector_store_name: str) -> list[Path]:
    target_dir = DOCUMENTS_DIR / vector_store_name if vector_store_name else DOCUMENTS_DIR
    target_dir.mkdir(parents=True, exist_ok=True)

    saved_paths = []
    for uploaded_file in uploaded_files:
        safe_name = Path(uploaded_file.name).name
        destination = target_dir / safe_name
        destination.write_bytes(uploaded_file.getbuffer())
        saved_paths.append(destination)

    return saved_paths


def document_embedding_page() -> None:
    st.markdown("<h1>Document embedding</h1>", unsafe_allow_html=True)
    st.markdown(
        '<p class="subtitle">This page is used to upload the documents as the custom knowledge for the chatbot.</p>',
        unsafe_allow_html=True,
    )

    with st.container(border=True):
        st.markdown('<div class="section-title">Knowledge Documents</div>', unsafe_allow_html=True)
        uploaded_files = st.file_uploader(
            "Drag and drop file here",
            type=["pdf", "txt", "md", "csv"],
            accept_multiple_files=True,
            label_visibility="collapsed",
            help="Limit 200MB per file · PDF, TXT, MD, CSV",
        )

        col1, col2, col3 = st.columns([2.1, 1, 1])
        with col1:
            embedding_model = st.text_input(
                "Model name of the Instruct Embeddings",
                value="hkunlp/instructor-xl",
            )
        with col2:
            chunk_size = st.number_input("Chunk Size", min_value=50, max_value=4000, value=200, step=50)
        with col3:
            chunk_overlap = st.number_input("Chunk Overlap", min_value=0, max_value=1000, value=10, step=5)

        col4, col5 = st.columns(2)
        with col4:
            merge_target = st.selectbox(
                "Vector Store to Merge the Knowledge",
                options=["<new>", "default"],
                index=0,
            )
        with col5:
            vector_store_name = st.text_input("New Vector Store Name", value="new_vector_store_name")

        if st.button("Save vector store"):
            if not uploaded_files:
                st.warning("Please upload at least one PDF, TXT, MD, or CSV file.")
                return

            store_name = vector_store_name.strip() if merge_target == "<new>" else merge_target
            saved_paths = save_uploaded_documents(uploaded_files, store_name)
            st.success(f"Saved {len(saved_paths)} document(s) to data/documents/{store_name}")
            st.info(
                "Restart FastAPI backend after saving documents so the FAISS index reloads with the new knowledge."
            )
            st.session_state["embedding_config"] = {
                "embedding_model": embedding_model,
                "chunk_size": chunk_size,
                "chunk_overlap": chunk_overlap,
                "vector_store_name": store_name,
            }


def chatbot_page() -> None:
    st.markdown("<h1>rag chatbot</h1>", unsafe_allow_html=True)
    st.markdown(
        '<p class="subtitle">Ask questions from your uploaded knowledge base.</p>',
        unsafe_allow_html=True,
    )

    question = st.text_area(
        "Ask a question",
        value="Explain adaptive RAG architecture with FastAPI and Streamlit.",
        height=140,
    )

    if st.button("Generate Answer", type="primary"):
        if not question.strip():
            st.warning("Please enter a question.")
            return

        with st.spinner("Running adaptive RAG workflow..."):
            try:
                response = requests.post(API_URL, json={"question": question}, timeout=30)
                response.raise_for_status()
                data = response.json()
            except requests.RequestException as exc:
                st.error(f"FastAPI backend is not running or returned an error: {exc}")
                return

        col1, col2 = st.columns([1, 3])
        with col1:
            st.metric("Route", data["route"].title())
            st.metric("Self-Correction", data["self_correction_attempts"])
            st.write("Vector Backend")
            st.code(data["vector_backend"])
            st.write("LLM Backend")
            st.code(data.get("llm_backend", "OfflineExtractive"))
            if data["rewritten_question"] != data["question"]:
                st.write("Rewritten Query")
                st.code(data["rewritten_question"])
            st.write("Sources")
            for source in data["sources"]:
                st.code(source)

        with col2:
            st.subheader("Answer")
            st.write(data["answer"])


inject_styles()

with st.sidebar:
    page = st.radio(
        "rag chatbot",
        ["document embedding", "chatbot"],
        index=0,
        label_visibility="visible",
    )

if page == "document embedding":
    document_embedding_page()
else:
    chatbot_page()
