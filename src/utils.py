import streamlit as st
import base64
import requests
from io import BytesIO
from PIL import Image
from typing import List, Dict, Any, Optional
from dataclasses import dataclass

@dataclass
class Message:
    """Represents a chat message."""
    role: str
    content: str
    summary: bool = False

class SessionState:
    """Manages Streamlit session state with proper initialization and typing."""
    
    @staticmethod
    def initialize() -> None:
        """Initialize all session state variables with default values."""
        defaults = {
            "chat_aborted": False,
            "messages": [{"role": "assistant", "content": "Hi. I'm WizSearch your super-smart AI assistant. Ask me anything you are looking for 🪄."}],
            "vectorstore": False,
            "temperature": 0.1,
            "max_tokens": 2500,
            "image_search": True,
            "top_k": 4,
            "search_results": None,
            "followup_query": [],
            "image_data": [],
            "knowledge_in_memory": False,
            "model_api_key": None
        }
        
        for key, default_value in defaults.items():
            if key not in st.session_state:
                st.session_state[key] = default_value

    @staticmethod
    def clear_chat_history() -> None:
        """Reset chat history to initial state."""
        st.session_state.messages = [{"role": "assistant", "content": "Hi. I'm WizSearch your super-smart AI assistant. Ask me anything you are looking for 🪄."}]
        st.session_state.chat_aborted = False

    @staticmethod
    def get_messages() -> List[Dict[str, Any]]:
        """Get current chat messages."""
        return st.session_state.messages

    @staticmethod
    def add_message(role: str, content: str, summary: bool = False) -> None:
        """Add a new message to the chat history."""
        message = {"role": role, "content": content}
        if summary:
            message["summary"] = True
        st.session_state.messages.append(message)

    @staticmethod
    def update_last_message(content: str) -> None:
        """Update the content of the last message."""
        if st.session_state.messages:
            st.session_state.messages[-1]["content"] = content

    @staticmethod
    def set_chat_aborted(value: bool) -> None:
        """Set the chat aborted state."""
        st.session_state.chat_aborted = value

class Utils:
    """Utility functions for the application."""
    
    @staticmethod
    def abort_chat(error_message: str) -> None:
        """Abort the chat with an error message."""
        assert error_message, "Error message must be provided."
        error_message = f":red[{error_message}]"
        
        messages = SessionState.get_messages()
        if messages[-1]["role"] != "assistant":
            SessionState.add_message("assistant", error_message)
        else:
            SessionState.update_last_message(error_message)
            
        SessionState.set_chat_aborted(True)
        st.rerun()

    @staticmethod
    def process_image(url: str) -> Optional[str]:
        """Process an image URL and return base64 encoded data."""
        try:
            pil_image = Image.open(requests.get(url, stream=True).raw)
            buffered = BytesIO()
            pil_image.save(buffered, format="JPEG")
            base64_image = base64.b64encode(buffered.getvalue()).decode("utf-8")
            return f"data:image/jpeg;base64,{base64_image}"
        except Exception:
            return None

# For backward compatibility
def clear_chat_history():
    SessionState.clear_chat_history()

def abort_chat(error_message: str):
    Utils.abort_chat(error_message)

def image_data(url: str) -> Optional[str]:
    return Utils.process_image(url)

def initialise_session_state():
    SessionState.initialize()
