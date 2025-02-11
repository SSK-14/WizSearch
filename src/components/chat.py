import streamlit as st
import base64, secrets
from pathlib import Path
from markitdown import MarkItDown
from langchain_text_splitters import RecursiveCharacterTextSplitter, MarkdownHeaderTextSplitter
from streamlit_feedback import streamlit_feedback
from src.modules.tools.vectorstore import vector_store
from src.modules.tools.search import jina_reader
from src.utils import clear_chat_history
from src.modules.model import model

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
        collections = vector_store.all_collections()
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
                "Upload Documents", 
                accept_multiple_files=True,
            )

            if uploaded_files:
                with st.spinner("Please wait, Uploading ⌛..."):
                    temp_dir = Path(".temp")
                    temp_dir.mkdir(exist_ok=True)
                    file_paths = []
                    
                    for existing_file in temp_dir.glob("*"):
                        existing_file.unlink()
                        
                    for file in uploaded_files:
                        temp_path = temp_dir / f"{secrets.token_hex(8)}_{file.name}"
                        with open(temp_path, "wb") as f:
                            f.write(file.getvalue())
                        file_paths.append(temp_path)
                
                with st.expander("Chunk Settings", expanded=False):
                    col1, col2 = st.columns(2)
                    col1.slider("Chunk Size", min_value=100, max_value=2000, value=500, key="chunk_size")
                    col2.slider("Chunk Overlap", min_value=0, max_value=500, value=100, key="chunk_overlap")

                _, col, _ = st.columns([1, 2, 1])
                if col.button("Submit", use_container_width=True, type="primary"):
                    st.session_state.collection_name = new_collection
                    all_texts = []
                    all_metadatas = []
                    
                    for file_path in file_paths:
                        md = MarkItDown()
                        result = md.convert(str(file_path))
                        all_texts.append(result.text_content)
                        all_metadatas.append({"file": file_path.name.split('_', 1)[1]})

                    text_splitter = RecursiveCharacterTextSplitter(
                        chunk_size=st.session_state.get("chunk_size") or 500,
                        chunk_overlap=st.session_state.get("chunk_overlap") or 80,
                        separators=["\n\n", "\n", " ", ""],
                    )

                    chunks = text_splitter.create_documents(all_texts, metadatas=all_metadatas)
                    _, col, _ = st.columns([1, 4, 1])
                    with col:
                        with st.spinner("Please wait, ingesting documents ⌛..."):
                            vector_store.create_collection_and_insert(st.session_state.collection_name, chunks, st.session_state.knowledge_in_memory)
                            for file_path in file_paths:
                                file_path.unlink()
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
                            vector_store.create_collection_and_insert(new_collection, md_header_splits, st.session_state.knowledge_in_memory)
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
    if model.supports_vision(st.session_state.model_name):
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
    if model.supports_vision(st.session_state.model_name):
        if len(st.session_state.image_data):
            cols = st.columns(4)
            for i, image in enumerate(st.session_state.image_data):
                cols[i].image(image, use_container_width=True)

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