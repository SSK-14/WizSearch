import os, asyncio, json 
import streamlit as st
from langfuse import Langfuse
from src.components.sidebar import side_info
from src.modules.model import llm_generate, llm_stream, initialise_model
from src.modules.prompt import base_prompt, query_formatting_prompt, generate_prompt, followup_query_prompt
from src.components.ui import display_search_result, display_chat_messages, feedback, document, followup_questions, example_questions
from src.utils import initialise_session_state, clear_chat_history, abort_chat
from src.modules.chain import process_query, search_tavily , search_vectorstore

os.environ["LANGFUSE_SECRET_KEY"] = st.secrets["LANGFUSE_SECRET_KEY"]
os.environ["LANGFUSE_PUBLIC_KEY"] = st.secrets["LANGFUSE_PUBLIC_KEY"]
os.environ["LANGFUSE_HOST"] = "https://cloud.langfuse.com" 

langfuse = Langfuse()

async def main():
    st.title("🔍 :orange[AI] Playground")
    side_info()
    initialise_session_state()
    initialise_model()

    if len(st.session_state.messages) == 1:
        document()

    height = 700 if len(st.session_state.messages) > 1 else 640
    with st.container(height=height, border=False):
        display_chat_messages(st.session_state.messages)
            
        if len(st.session_state.messages) == 1:
            example_questions()
        st.session_state.search_results = None
        if st.session_state.messages[-1]["role"] != "assistant":
            query = st.session_state.messages[-1]["content"]
            trace = langfuse.trace(name="AI Search", input=query)
            st.session_state.trace = trace

            try:
                with st.status("🚀 AI at work...", expanded=True) as status:
                    query, intent = await process_query()
                    followup_query_asyncio = asyncio.create_task(llm_generate(followup_query_prompt(query), trace, "Follow-up Query"))
                        
                    if "search" in intent:
                        query = await llm_generate(query_formatting_prompt(query), trace, "Query Formatting")
                        st.write(f"📝 Search query: {query}")
                        if st.session_state.vectorstore:
                            prompt = await search_vectorstore(query)
                        else:
                            prompt = await search_tavily(query)
                    elif "generate" in intent:
                        st.write("🔮 Generating response...")
                        prompt = generate_prompt(st.session_state.messages)
                    else:
                        prompt = base_prompt(intent, query)
                    status.update(label="Done and dusted!", state="complete", expanded=False)
            except Exception as e:
                trace.update(output=str(e), level="ERROR")
                abort_chat(f"An error occurred: {e}")

            if st.session_state.search_results:
                display_search_result(st.session_state.search_results)

            if followup_query_asyncio:
                followup_query = await followup_query_asyncio
                if followup_query:
                    try:
                        st.session_state.followup_query = json.loads(followup_query)
                    except json.JSONDecodeError:
                        st.session_state.followup_query = []

            with st.chat_message("assistant", avatar="./src/assets/logo.png"):
                st.write_stream(llm_stream(prompt, trace, "Final Answer"))
            trace.update(output=st.session_state.messages[-1]["content"])

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
    asyncio.run(main())
