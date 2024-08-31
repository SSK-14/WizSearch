import asyncio, json 
import streamlit as st
from src.components.sidebar import side_info
from src.modules.model import llm_generate, llm_stream, initialise_model
from src.modules.prompt import base_prompt, query_formatting_prompt, generate_prompt, followup_query_prompt
from src.components.ui import display_search_result, display_chat_messages, feedback, document, followup_questions, example_questions, add_image
from src.utils import initialise_session_state, clear_chat_history, abort_chat
from src.modules.chain import process_query, search_tavily , search_vectorstore
from src.modules.tools.langfuse import start_trace, end_trace

@st.fragment
async def main():
    if len(st.session_state.messages) == 1:
        col1, col2, col = st.columns([5, 4, 7])
        with col1:
            document()
        with col2:
            add_image()

    display_chat_messages(st.session_state.messages)
    if len(st.session_state.messages) == 1:
        example_questions()
            
    st.session_state.search_results = None
    if st.session_state.messages[-1]["role"] != "assistant":
        query = st.session_state.messages[-1]["content"]
        start_trace(query)

        try:
            with st.status("🚀 AI at work...", expanded=True) as status:
                query, intent = await process_query()
                followup_query_asyncio = asyncio.create_task(llm_generate(followup_query_prompt(st.session_state.messages), "Follow-up Query"))
                    
                if len(st.session_state.image_data):
                    prompt = generate_prompt(query, st.session_state.messages, st.session_state.image_data)
                elif "search" in intent:
                    query = await llm_generate(query_formatting_prompt(query), "Query Formatting")
                    st.write(f"📝 Search query: {query}")
                    if st.session_state.vectorstore:
                        prompt = await search_vectorstore(query)
                    else:
                        prompt = await search_tavily(query)
                elif "generate" in intent:
                    st.write("🔮 Generating response...")
                    prompt = generate_prompt(query, st.session_state.messages)
                else:
                    prompt = base_prompt(intent, query)
                status.update(label="Done and dusted!", state="complete", expanded=False)
        except Exception as e:
            end_trace(str(e), "ERROR")
            abort_chat(f"An error occurred: {e}")

        if st.session_state.search_results:
            display_search_result(st.session_state.search_results)

        if followup_query_asyncio:
            followup_query = await followup_query_asyncio
            if followup_query:
                followup_query = "[" + followup_query.split("[")[1].split("]")[0] + "]"
                try:
                    st.session_state.followup_query = json.loads(followup_query)
                except json.JSONDecodeError:
                    st.session_state.followup_query = []

        with st.chat_message("assistant", avatar="./src/assets/logo.png"):
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
    st.set_page_config(page_title="Wiz AI", page_icon="🌟")
    st.title("🔍 :orange[AI] Playground")
    side_info()
    initialise_session_state()
    initialise_model()
    asyncio.run(main())