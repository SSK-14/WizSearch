import os
import streamlit as st
from src.sidebar import side_info
from src.model import llm_generate, llm_stream
from src.prompt import intent_prompt, search_rag_prompt, base_prompt
from src.ui import display_search_result, display_chat_messages
from tavily import TavilyClient

os.environ['REPLICATE_API_TOKEN'] = st.secrets['REPLICATE_API_TOKEN']
tavily = TavilyClient(api_key=st.secrets['TAVILY_API_KEY'])

def clear_chat_history():
    st.session_state.messages = [{"role": "assistant", "content": "Hi. I'm SearchWiz your super-smart AI assistant using [Snowflake Arctic](https://www.snowflake.com/blog/arctic-open-and-efficient-foundation-language-models-snowflake). Ask me anything you are looking for 🪄."}]
    st.session_state.chat_aborted = False

if "messages" not in st.session_state:
    clear_chat_history()

def main():
    st.title("🔍 :orange[AI] Playground")
    side_info()
    display_chat_messages(st.session_state.messages)

    if st.session_state.messages[-1]["role"] != "assistant":
        query = st.session_state.messages[-1]["content"]
        search_results = None
        with st.status("🚀 AI at work...", expanded=True) as status:
            st.write("🔄 Processing your query...")
            intent = llm_generate(intent_prompt(query))
            intent = intent.strip().lower()
            st.write(f"🔍 Intent validated...")

            if "valid_query" in intent:
                st.write("🌐 Searching the web...")
                search_results = tavily.search(query, search_depth="advanced", include_images=True)
                search_context = [{"url": obj["url"], "content": obj["content"]} for obj in search_results["results"]]
                st.json(search_results, expanded=False)
                prompt = search_rag_prompt(search_context, st.session_state.messages)
                status.update(label="Done and dusted!", state="complete", expanded=False)
            else:
                prompt = base_prompt(intent, query)
                status.update(label="Done and dusted!", state="complete", expanded=False)

        if search_results:
            display_search_result(search_results)
        
        with st.chat_message("assistant", avatar="./src/assets/logo.svg"):
            st.write_stream(llm_stream(prompt))

    if st.session_state.chat_aborted:
        st.button('Reset chat', on_click=clear_chat_history, key="clear_chat_history")
        st.chat_input(disabled=True)
    elif query := st.chat_input("Enter your search query here..."):
        st.session_state.messages.append({"role": "user", "content": query})
        st.rerun()

    if len(st.session_state.messages) > 1:
        st.button('New Chat', on_click=clear_chat_history)


if __name__ == "__main__":
    st.set_page_config(page_title="Wiz AI", page_icon="🔍")
    main()
