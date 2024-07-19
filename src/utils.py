import streamlit as st

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

def initialise_session_state():
    if "chat_aborted" not in st.session_state:
        st.session_state.chat_aborted = False

    if "messages" not in st.session_state:
        clear_chat_history()

    if "vectorstore" not in st.session_state:
        st.session_state.vectorstore = False

    if "search_results" not in st.session_state:
        st.session_state.search_results = None

    if "followup_query" not in st.session_state:
        st.session_state.followup_query = []

    if "image_data" not in st.session_state:
        st.session_state.image_data = None
  