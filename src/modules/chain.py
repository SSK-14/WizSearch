import streamlit as st
from src.modules.model import llm_generate
from src.modules.vectorstore import search_collection
from src.modules.prompt import intent_prompt, search_rag_prompt, standalone_query_prompt
from src.utils import abort_chat
from src.modules.search import initialise_tavily

async def process_query():
    trace = st.session_state.trace
    query = st.session_state.messages[-1]["content"]
    if len(st.session_state.messages) > 3:
        history = st.session_state.messages[:-1]
        query = await llm_generate(standalone_query_prompt(query, history), trace, "Standalone Query")
        st.write(f"❓ Standalone query: {query}")
    st.write("🔄 Processing your query...")
    intent = await llm_generate(intent_prompt(query), trace, "Intent")
    intent = intent.strip().lower()
    st.write(f"🔍 Intent validated...")
    return query, intent

async def search_vectorstore(query):
    trace = st.session_state.trace
    st.write("📚 Searching the document...")
    retrieval = trace.span(name="Retrieval", metadata={"search": "document"}, input=query)
    search_results = search_collection(query)
    st.session_state.search_results = search_results
    retrieval.end(output=search_results)
    if search_results:
        return search_rag_prompt(search_results, st.session_state.messages)

async def search_tavily(query):
    tavily = initialise_tavily()
    trace = st.session_state.trace
    st.write("🌐 Searching the web...")
    retrieval = trace.span(name="Retrieval", metadata={"search": "tavily"}, input=query)
    search_results = tavily.search(query, search_depth="advanced", include_images=True)
    st.session_state.search_results = search_results
    retrieval.end(output=search_results)                
    if search_results["results"]:
        search_context = [{"url": obj["url"], "content": obj["content"]} for obj in search_results["results"]]
        st.json(search_results, expanded=False)
        return search_rag_prompt(search_context, st.session_state.messages)
    else:
        trace.update(output="No search results found", level="WARNING")
        abort_chat("I'm sorry, There was an error in search. Please try again.")