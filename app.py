import asyncio, json, os
import streamlit as st
from src.components.sidebar import side_info
from src.modules.model import llm_stream, initialise_model
from src.components.chat import display_chat_messages, feedback, document, followup_questions, example_questions, add_image, display_image
from src.utils import initialise_session_state, clear_chat_history, abort_chat
from src.modules.chain import generate_answer_prompt, generate_summary_prompt
from src.modules.tools.langfuse import start_trace, end_trace

os.environ["TOKENIZERS_PARALLELISM"] = "false"

@st.fragment
async def main():
    side_info()
    initialise_model()
    
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
            
    st.session_state.search_results = None
    if st.session_state.messages[-1]["role"] != "assistant":
        query = st.session_state.messages[-1]["content"]
        start_trace(query)

        try:
            if "summary" in st.session_state.messages[-1] and st.session_state.messages[-1]["summary"]:
                prompt = await generate_summary_prompt()
                followup_query_asyncio = None
            else:
                prompt, followup_query_asyncio = await generate_answer_prompt()
        except Exception as e:
            end_trace(str(e), "ERROR")
            abort_chat(f"An error occurred: {e}")

        if followup_query_asyncio:
            followup_query = await followup_query_asyncio
            if followup_query:
                followup_query = "[" + followup_query.split("[")[1].split("]")[0] + "]"
                try:
                    st.session_state.followup_query = json.loads(followup_query)
                except json.JSONDecodeError:
                    st.session_state.followup_query = []

        with st.chat_message("assistant", avatar="✨"):
            st.write_stream(llm_stream(prompt, "Final Answer"))
        end_trace(st.session_state.messages[-1]["content"])

    if len(st.session_state.messages) > 1:
        col1, col2 = st.columns([1, 4])
        col1.button('New Chat', on_click=clear_chat_history)
        with col2:
            feedback()
        followup_questions()

    if st.session_state.chat_aborted:
        st.chat_input("Enter your search query here...", disabled=True)
    elif query := st.chat_input("Enter your search query here..."):
        st.session_state.messages.append({"role": "user", "content": query})
        st.rerun()

if __name__ == "__main__":
    st.set_page_config(page_title="Wiz AI", page_icon="✨")
    st.title("🔍 :orange[AI] Playground")
    initialise_session_state()
    asyncio.run(main())