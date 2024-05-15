import json, os
import streamlit as st
from src.sidebar import side_info
from src.model import init_llm
from src.prompt import intent_prompt, search_rag_prompt, base_prompt
from src.ui import display_search_result, display_chat_messages
from tavily import TavilyClient
from dotenv import load_dotenv
load_dotenv()

if "messages" not in st.session_state:
    st.session_state.messages = []

llm = init_llm()
tavily = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))

def stream_response(prompt):
    chunks = ""
    for chunk in llm.stream(prompt):
        yield chunk.content
        chunks += chunk.content
    st.session_state.messages.append({"role": "assistant", "content": chunks})

def main():
    st.title("👋🔍 SearchWiz Playground")
    side_info()
    display_chat_messages(st.session_state.messages)
    if query := st.chat_input("Enter your search query here..."):
        st.session_state.messages.append({"role": "user", "content": query})
        with st.chat_message("user", avatar="👤"):
            st.markdown(query)

        search_results = None
        with st.status("🚀 AI at work...", expanded=True) as status:
            st.write("🔄 Processing your query...")
            intent = llm.invoke(intent_prompt(query)).content
            st.write(f"🔍 Intent: {intent}")
            if intent != 'valid_query':
                prompt = base_prompt(intent, query)
                status.update(label="✅ Done and dusted!", state="complete", expanded=False)
            else:
                st.write("🌐 Searching the web...")
                search_results = tavily.search(query, search_depth="advanced", include_images=True)
                search_context = [{"url": obj["url"], "content": obj["content"]} for obj in search_results["results"]]
                st.json(search_results, expanded=False)
                prompt = search_rag_prompt(search_context, st.session_state.messages)
                status.update(label="✅ Done and dusted!", state="complete", expanded=False)

        if search_results:
            display_search_result(search_results)
        
        with st.chat_message("assistant", avatar="./src/assets/logo.png"):
            st.write_stream(stream_response(prompt))

        if len(st.session_state.messages) > 0:
            if st.button("New Chat"):
                st.session_state.messages = []


if __name__ == "__main__":
    st.set_page_config(page_title="Wiz AI", page_icon="🔍")
    main()
