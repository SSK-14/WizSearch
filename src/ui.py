import secrets
import streamlit as st
import PyPDF2
from langchain_text_splitters import RecursiveCharacterTextSplitter
from streamlit_feedback import streamlit_feedback
from src.vectorstore import create_collection_and_insert

def display_chat_messages(messages):
    icons = {"assistant": "./src/assets/logo.svg", "user": "👤"}
    for message in messages:
        with st.chat_message(message["role"], avatar=icons[message["role"]]):
            st.markdown(message["content"])

def display_search_result(search_results):
    if search_results["images"]:
        with st.expander("Image Results", expanded=False):
            col1, col2, col3, col4, col5 = st.columns(5)
            col1.image(search_results["images"][0], use_column_width=True)
            col2.image(search_results["images"][1], use_column_width=True)
            col3.image(search_results["images"][2], use_column_width=True)
            col4.image(search_results["images"][3], use_column_width=True)
            col5.image(search_results["images"][4], use_column_width=True)

    with st.expander("Search Results", expanded=False):
        if search_results["results"]:
            for result in search_results["results"]:
                st.write(f"- [{result['title']}]({result['url']})")

def abort_chat(error_message: str):
    assert error_message, "Error message must be provided."
    error_message = f":red[{error_message}]"
    if st.session_state.messages[-1]["role"] != "assistant":
        st.session_state.messages.append({"role": "assistant", "content": error_message})
    else:
        st.session_state.messages[-1]["content"] = error_message
    st.session_state.chat_aborted = True
    st.rerun()

def feedback():
    trace = st.session_state.trace
    scores = {"😀": 1, "🙂": 0.75, "😐": 0.5, "🙁": 0.25, "😞": 0}
    if "feedback_" + trace.id not in st.session_state: 
        streamlit_feedback(
            feedback_type="faces",
            optional_text_label="[Optional] Please provide an explanation",
            key=f"feedback_{trace.id}",
        )
    else:
        if st.session_state["feedback_" + trace.id] is not None:
            feedback = st.session_state["feedback_" + trace.id]
            trace.score(
                name="user-explicit-feedback",
                value=scores[feedback["score"]],
                comment=feedback["text"],
            )

@st.experimental_dialog("Upload your PDF files")
def upload_document():
    uploaded_files = st.file_uploader("Upload PDF files", accept_multiple_files=True, type="pdf")
    col1, col2 = st.columns(2)
    col1.slider("Chunk Size", min_value=100, max_value=2000, value=500, key="chunk_size")
    col2.slider("Chunk Overlap", min_value=0, max_value=500, value=100, key="chunk_overlap")

    if uploaded_files:
        if st.button("Submit"):
            text = []
            metadatas = []
            st.session_state.collection_name = secrets.token_urlsafe(8)
            for file in uploaded_files:
                pdf_reader = PyPDF2.PdfReader(file)
                page_number = 1
                for page in pdf_reader.pages:
                    text.append(page.extract_text())
                    metadatas.append({"page": page_number, "file": file.name})
                    page_number += 1

            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=st.session_state.get("chunk_size") or 500,
                chunk_overlap=st.session_state.get("chunk_overlap") or 80,
                separators=["\n\n", "\n", " ", ""],
            )

            chunks = text_splitter.create_documents(text, metadatas=metadatas)
            create_collection_and_insert(chunks)
            st.session_state.vectorstore = True
            st.rerun()