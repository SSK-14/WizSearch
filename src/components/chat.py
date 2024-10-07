import streamlit as st
import PyPDF2, base64, secrets
from langchain_text_splitters import RecursiveCharacterTextSplitter, MarkdownHeaderTextSplitter
from streamlit_feedback import streamlit_feedback
from src.modules.tools.vectorstore import create_collection_and_insert, all_collections
from src.modules.tools.search import jina_reader
from src.utils import clear_chat_history


def display_chat_messages(messages):
    icons = {"assistant": "✨", "user": "👤"}
    for message in messages:
        with st.chat_message(message["role"], avatar=icons[message["role"]]):
            st.markdown(message["content"])

def display_search_result(search_results):
    if st.session_state.vectorstore:
        with st.expander("Document Result", expanded=False):
            st.json(search_results, expanded=False)
    else:
        if search_results["results"]:
            st.json(search_results["results"], expanded=False)

def feedback():
    trace = st.session_state.trace
    if trace:
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
    if st.session_state.vectorstore:
        questions = [
            "Provide a TL;DR summary of the document. 📄",
            "Highlight the key points of the document. 🔑",
        ]
    else:
        questions = [
            "What happened in T20 world cup 2024 final ?",
            "Write a short poem on a tool 'Wiz search'.",
        ]
    if col1.button(questions[0], use_container_width=True):
        st.session_state.messages.append({"role": "user", "content": questions[0], "summary": st.session_state.vectorstore})
        st.rerun()
    if col2.button(questions[1], use_container_width=True):
        st.session_state.messages.append({"role": "user", "content": questions[1], "summary": st.session_state.vectorstore})
        st.rerun()


@st.dialog("📚 Add Knowledge")
def add_knowledge():
    temp_storage = st.toggle("Temporary Storage", value=st.session_state.knowledge_in_memory)

    if temp_storage:
        new_collection = secrets.token_hex(16)
        st.session_state.knowledge_in_memory = True
    else:
        st.session_state.knowledge_in_memory = False
        collections = all_collections()
        col1, col2 = st.columns(2)
        collection_name = col1.selectbox("Select a Knowledge", collections, index=None)
        if collection_name:
            st.session_state.collection_name = collection_name
            st.session_state.vectorstore = True
            st.rerun()
        new_collection = col2.text_input("Add a new knowledge", placeholder="Enter new knowledge name")
        if new_collection in collections:
            st.error("Knowledge already exists. Please choose a different name.")
            st.stop()

    if new_collection.strip() != "":
        tab1, tab2 = st.tabs(["Upload Document", "Add Website"])
        with tab1:
            uploaded_files = st.file_uploader(
                "Upload PDF files", 
                accept_multiple_files=True, 
                type="pdf"
            )

            if uploaded_files:
                with st.expander("Chunk Settings", expanded=False):
                    col1, col2 = st.columns(2)
                    col1.slider("Chunk Size", min_value=100, max_value=2000, value=500, key="chunk_size")
                    col2.slider("Chunk Overlap", min_value=0, max_value=500, value=100, key="chunk_overlap")

                _, col, _ = st.columns([1, 2, 1])
                if col.button("Submit", use_container_width=True, type="primary"):
                    text = []
                    metadatas = []
                    st.session_state.collection_name = new_collection
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
                    _, col, _ = st.columns([1, 4, 1])
                    with col:
                        with st.spinner("Please wait, ingesting documents ⌛..."):
                            create_collection_and_insert(st.session_state.collection_name, chunks, st.session_state.knowledge_in_memory)
                    st.session_state.vectorstore = True
                    st.rerun()
        with tab2:
            website_url = st.text_input("Website URL", placeholder="Enter website URL")
            if website_url:
                markdown_document = jina_reader(website_url)
                headers_to_split_on = [
                    ("#", "Header 1"),
                    ("##", "Header 2"),
                    ("###", "Header 3"),
                ]
                markdown_splitter = MarkdownHeaderTextSplitter(headers_to_split_on=headers_to_split_on)
                md_header_splits = markdown_splitter.split_text(markdown_document)
                _, col, _ = st.columns([1, 4, 1])
                with col:
                    if st.button("Submit", use_container_width=True, type="primary"):
                        st.session_state.collection_name = new_collection
                        with st.spinner("Please wait, ingesting documents ⌛..."):
                            create_collection_and_insert(new_collection, md_header_splits, st.session_state.knowledge_in_memory)
                        st.session_state.vectorstore = True
                        st.rerun()



@st.dialog("Add Image to Chat")
def upload_image():
    uploaded_images = st.file_uploader("Upload Image", type=['png', 'jpg'], accept_multiple_files=True)
    if uploaded_images:
        for uploaded_image in uploaded_images:
            bytes_data = uploaded_image.getvalue()
            base64_image = base64.b64encode(bytes_data).decode('utf-8')
            image_format = uploaded_image.type.split('/')[-1]
            image_data = f"data:image/{image_format};base64,{base64_image}"
            st.session_state.image_data.append(image_data)
        st.rerun()

def add_image():
    if "VISION_MODELS" in st.secrets:
        if st.session_state.model_name in st.secrets['VISION_MODELS']:
            if len(st.session_state.image_data):
                if st.button("🔄 Change image", use_container_width=True):
                    st.session_state.image_data = []
                    st.rerun()
            else:
                if st.button("🖼️ Add image", use_container_width=True):
                    upload_image()
        else:
            st.session_state.image_data = []

def display_image():
    if "VISION_MODELS" in st.secrets:
        if len(st.session_state.image_data):
            cols = st.columns(4)
            for i, image in enumerate(st.session_state.image_data):
                cols[i].image(image, use_column_width=True)

def document():
    if not st.session_state.vectorstore:
        if st.button("📚 Add Knowledge", use_container_width=True):
            add_knowledge()
    else:
        if st.button(f"🗑️ {st.session_state.collection_name[:16]}...", use_container_width=True):
            st.session_state.vectorstore = False
            st.session_state.collection_name = None
            clear_chat_history()
            st.rerun()