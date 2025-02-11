import asyncio
import json
import os
import streamlit as st
from dotenv import load_dotenv
from src.components.sidebar import side_info
from src.modules.model import model
from src.components.chat import (
    display_chat_messages,
    feedback,
    document,
    followup_questions,
    example_questions,
    add_image,
    display_image,
)
from src.utils import initialise_session_state, clear_chat_history, abort_chat
from src.modules.chain import generate_answer_prompt, generate_summary_prompt
from src.modules.tools.langfuse import start_trace, end_trace
from src.modules.context import app_context

load_dotenv()
os.environ["TOKENIZERS_PARALLELISM"] = "false"

class ChatState:
    """Manages chat-specific state to reduce global state usage."""
    
    def __init__(self):
        self.search_results = None
        self.chat_aborted = False
        self.followup_query = []
        
    def clear_search_results(self):
        """Clear search results."""
        self.search_results = None
        
    def set_chat_aborted(self, value: bool):
        """Set chat aborted state."""
        self.chat_aborted = value
        
    def set_followup_query(self, query: str):
        """Parse and set followup query."""
        try:
            if query:
                query = "[" + query.split("[")[1].split("]")[0] + "]"
                self.followup_query = json.loads(query)
        except (json.JSONDecodeError, IndexError):
            self.followup_query = []

class App:
    """Main application class with dependency injection."""
    
    def __init__(self, context):
        self.context = context
        self.chat_state = ChatState()
        
    async def handle_user_message(self, messages):
        """Handle new user message."""
        if messages[-1]["role"] != "assistant":
            query = messages[-1]["content"]
            start_trace(query)

            try:
                if "summary" in messages[-1] and messages[-1]["summary"]:
                    prompt = await generate_summary_prompt()
                    followup_query_asyncio = None
                else:
                    prompt, followup_query_asyncio = await generate_answer_prompt()
            except Exception as e:
                end_trace(str(e), "ERROR")
                abort_chat(f"An error occurred: {e}")
                return None, None

            if followup_query_asyncio:
                followup_query = await followup_query_asyncio
                self.chat_state.set_followup_query(followup_query)

            return prompt, query
        return None, None

    @st.fragment
    async def main(self):
        """Main application flow."""
        side_info()
        
        if len(st.session_state.messages) == 1:
            col1, col2, col = st.columns([4, 4, 6])
            with col1:
                document()
            with col2:
                add_image()
        display_image()
        display_chat_messages(st.session_state.messages)
        if len(st.session_state.messages) == 1:
            example_questions()
                
        self.chat_state.clear_search_results()
        prompt, query = await self.handle_user_message(st.session_state.messages)
        
        if prompt is not None:
            with st.chat_message("assistant", avatar="✨"):
                st.write_stream(model.stream(prompt, "Final Answer"))
            end_trace(st.session_state.messages[-1]["content"])

        if len(st.session_state.messages) > 1:
            col1, col2 = st.columns([1, 4])
            col1.button('New Chat', on_click=clear_chat_history)
            with col2:
                feedback()
            followup_questions()

        if self.chat_state.chat_aborted:
            st.chat_input("Enter your search query here...", disabled=True)
        elif query := st.chat_input("Enter your search query here..."):
            st.session_state.messages.append({"role": "user", "content": query})
            st.rerun()

def main():
    """Application entry point."""
    st.set_page_config(page_title="Wiz AI", page_icon="✨")
    st.title("🔍 :orange[AI] Playground")
    initialise_session_state()
    
    app = App(app_context)
    asyncio.run(app.main())

if __name__ == "__main__":
    main()
