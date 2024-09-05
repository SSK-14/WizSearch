import streamlit as st
import base64, requests
from io import BytesIO
from PIL import Image

def clear_chat_history():
    st.session_state.messages = [{"role": "assistant", "content": "Hi. I'm WizSearch your super-smart AI assistant. Ask me anything you are looking for 🪄."}]
    st.session_state.chat_aborted = False

def abort_chat(error_message: str):
    assert error_message, "Error message must be provided."
    error_message = f":red[{error_message}]"
    if st.session_state.messages[-1]["role"] != "assistant":
        st.session_state.messages.append({"role": "assistant", "content": error_message})
    else:
        st.session_state.messages[-1]["content"] = error_message
    st.session_state.chat_aborted = True
    st.rerun()

def image_data(url):
    try:
        pil_image = Image.open(requests.get(url, stream=True).raw)
        buffered = BytesIO()
        pil_image.save(buffered, format="JPEG")
        base64_image = base64.b64encode(buffered.getvalue()).decode("utf-8")
        return f"data:image/jpeg;base64,{base64_image}"
    except Exception as e:
        return None

def initialise_session_state():
    if "chat_aborted" not in st.session_state:
        st.session_state.chat_aborted = False

    if "messages" not in st.session_state:
        clear_chat_history()

    if "vectorstore" not in st.session_state:
        st.session_state.vectorstore = False

    if "temperature" not in st.session_state:
        st.session_state.temperature = 0.1

    if "max_tokens" not in st.session_state:
        st.session_state.max_tokens = 2500

    if "image_search" not in st.session_state:
        st.session_state.image_search = True
        
    if "top_k" not in st.session_state:
        st.session_state.top_k = 4

    if "search_results" not in st.session_state:
        st.session_state.search_results = None

    if "followup_query" not in st.session_state:
        st.session_state.followup_query = []

    if "image_data" not in st.session_state:
        st.session_state.image_data = []

    if "knowledge_in_memory" not in st.session_state:
        st.session_state.knowledge_in_memory = False

    if "model_api_key" not in st.session_state:
        st.session_state.model_api_key = None
  