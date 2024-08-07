import secrets
import streamlit as st
import PyPDF2
import base64
from langchain_text_splitters import RecursiveCharacterTextSplitter
from streamlit_feedback import streamlit_feedback
from src.modules.vectorstore import create_collection_and_insert
from src.utils import clear_chat_history
from src.modules.model import model_options, vision_models

def display_chat_messages(messages):
    icons = {"assistant": "./src/assets/logo.png", "user": "👤"}
    for message in messages:
        with st.chat_message(message["role"], avatar=icons[message["role"]]):
            st.markdown(message["content"])

def display_search_result(search_results):
    if st.session_state.vectorstore:
        with st.expander("Document Result", expanded=False):
            st.json(search_results, expanded=False)
    else:
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

def followup_questions():
    if st.session_state.followup_query and len(st.session_state.followup_query) > 0:
        selected_followup_query = st.radio("Follow-up Questions:", st.session_state.followup_query, index=None)
        if selected_followup_query is not None:
            if st.button("Ask Wiz", type="primary"):
                st.session_state.messages.append({"role": "user", "content": selected_followup_query})
                st.selected_followup_query = None
                st.session_state.followup_query = []
                st.rerun()

def example_questions():
    col1, col2 = st.columns(2)
    questions = [
        "What happened in T20 world cup 2024 final ?",
        "Write a short poem on a tool 'Wiz search'.",
    ]
    if col1.button(questions[0]):
        st.session_state.messages.append({"role": "user", "content": questions[0]})
        st.rerun()
    if col2.button(questions[1]):
        st.session_state.messages.append({"role": "user", "content": questions[1]})
        st.rerun()


@st.experimental_dialog("Upload your documents")
def upload_document():
    uploaded_files = st.file_uploader(
        "Upload PDF files", 
        accept_multiple_files=True, 
        type="pdf"
    )

    if uploaded_files:
        with st.expander("Advanced Options"):
            col1, col2 = st.columns(2)
            col1.slider("Chunk Size", min_value=100, max_value=2000, value=500, key="chunk_size")
            col2.slider("Chunk Overlap", min_value=0, max_value=500, value=100, key="chunk_overlap")
        _col1, col, _col2 = st.columns([1, 2, 1])
        if col.button("Submit", use_container_width=True, type="primary"):
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

@st.experimental_dialog("Add Image to Chat")
def upload_image():
    uploaded_image = st.file_uploader("Upload Image", type=['png', 'jpg'])
    if uploaded_image:
        bytes_data = uploaded_image.getvalue()
        base64_image = base64.b64encode(bytes_data).decode('utf-8')
        image_format = uploaded_image.type.split('/')[-1]
        image_data = f"data:image/{image_format};base64,{base64_image}"
        st.session_state.image_data = image_data
        st.rerun()

def add_image():
    if model_options[st.session_state.model_name] in vision_models:
        if st.session_state.image_data:
            if st.button("🔄 Change image", use_container_width=True):
                st.session_state.image_data = None
                st.rerun()
        else:
            if st.button("🖼️ Add image", use_container_width=True):
                upload_image()
    else:
        st.session_state.image_data = None

def document():
    if not st.session_state.vectorstore:
        if st.button("📚 Add documents", use_container_width=True):
            upload_document()
    else:
        if st.button("🗑️ Remove documents", use_container_width=True):
            st.session_state.vectorstore = False
            st.session_state.collection_name = None
            clear_chat_history()
            st.rerun()