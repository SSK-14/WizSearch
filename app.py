import json, os
import streamlit as st
from src.sidebar import side_info
from src.model import init_llm
from src.prompt import intent_prompt, rag_prompt
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

    if query := st.chat_input("Enter your search query here..."):
        st.session_state.messages.append({"role": "user", "content": query})
        with st.chat_message("user"):
            st.markdown(query)

        response = None
        with st.status("Downloading data...", expanded=True) as status:
            st.write("Processing your query...")
            intent_response = llm.invoke(intent_prompt(query)).content
            intent = json.loads(intent_response)

            if intent["intent"] != 'valid_query':
                response = intent["message"]
                status.update(label="Done", state="complete", expanded=False)
            else:
                st.write("Query is valid. Searching the web...")
                search_results = tavily.search(query, search_depth="advanced", include_images=True)
                search_context = [{"url": obj["url"], "content": obj["content"]} for obj in search_results["results"]]
                prompt = rag_prompt(search_context, st.session_state.messages)
                status.update(label="Done", state="complete", expanded=False)

        if search_results:
            with st.expander("Image Results", expanded=False):
                col1, col2, col3, col4, col5 = st.columns(5)
                col1.image(search_results["images"][0], use_column_width=True)
                col2.image(search_results["images"][1], use_column_width=True)
                col3.image(search_results["images"][2], use_column_width=True)
                col4.image(search_results["images"][3], use_column_width=True)
                col5.image(search_results["images"][4], use_column_width=True)

            with st.expander("Search Results", expanded=False):
                for result in search_results["results"]:
                    st.write(f"- [{result['title']}]({result['url']})")

        if response:  
            st.session_state.messages.append({"role": "assistant", "content": response})
            with st.chat_message("assistant"):
                st.markdown(response)
        else:
            st.write_stream(stream_response(prompt))

        if len(st.session_state.messages) > 0:
            if st.button("New Chat"):
                st.session_state.messages = []


if __name__ == "__main__":
    st.set_page_config(page_title="Hello", page_icon="🔍")
    main()
