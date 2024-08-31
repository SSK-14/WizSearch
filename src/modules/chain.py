import streamlit as st
from src.modules.model import llm_generate
from src.modules.tools.vectorstore import search_collection
from src.modules.prompt import intent_prompt, search_rag_prompt, standalone_query_prompt
from src.utils import abort_chat
from src.modules.tools.search import initialise_tavily
from src.modules.tools.langfuse import end_trace

async def process_query():
    query = st.session_state.messages[-1]["content"]
    if len(st.session_state.messages) > 3:
        history = st.session_state.messages[:-1]
        query = await llm_generate(standalone_query_prompt(query, history), "Standalone Query")
        st.write(f"❓ Standalone query: {query}")
    st.write("🔄 Processing your query...")
    intent = await llm_generate(intent_prompt(query), "Intent")
    intent = intent.strip().lower()
    st.write(f"🔍 Intent validated...")
    return query, intent

async def search_vectorstore(query):
    trace = st.session_state.trace
    st.write("📚 Searching the document...")
    if trace:
        retrieval = trace.span(name="Retrieval", metadata={"search": "document"}, input=query)
    search_results = search_collection(st.session_state.collection_name, query, st.session_state.top_k)
    st.session_state.search_results = search_results
    if trace:
        retrieval.end(output=search_results)
    if search_results:
        return search_rag_prompt(search_results, st.session_state.messages)

async def search_tavily(query):
    tavily = initialise_tavily()
    trace = st.session_state.trace
    st.write("🌐 Searching the web...")
    if trace:
        retrieval = trace.span(name="Retrieval", metadata={"search": "tavily"}, input=query)
    search_results = tavily.search(query, search_depth="advanced", include_images=True)
    st.session_state.search_results = search_results
    if trace:
        retrieval.end(output=search_results)                
    if search_results["results"]:
        search_context = [{"url": obj["url"], "content": obj["content"]} for obj in search_results["results"]]
        image_urls = []
        if "VISION_MODELS" in st.secrets:
            if st.session_state.model_name in st.secrets['VISION_MODELS']:
                image_urls = search_results["images"]
        return search_rag_prompt(search_context, image_urls, st.session_state.messages)
    else:
        if trace:
            end_trace("No search results found", "WARNING")
        abort_chat("I'm sorry, There was an error in search. Please try again.")