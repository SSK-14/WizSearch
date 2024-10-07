import asyncio
import streamlit as st
from src.modules.model import llm_generate
from src.components.chat import display_search_result
from src.modules.tools.vectorstore import search_collection, all_points
from src.modules.prompt import intent_prompt, search_rag_prompt, standalone_query_prompt
from src.utils import abort_chat
from src.modules.tools.search import initialise_tavily
from src.modules.tools.langfuse import end_trace
from src.modules.prompt import base_prompt, query_formatting_prompt, generate_prompt, followup_query_prompt, key_points_prompt, summary_prompt

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
    search_results = search_collection(st.session_state.collection_name, query, st.session_state.top_k, st.session_state.knowledge_in_memory)
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
    search_results = tavily.search(query, search_depth="advanced", include_images=st.session_state.image_search, max_results=st.session_state.top_k)
    st.session_state.search_results = search_results
    if trace:
        retrieval.end(output=search_results)                
    if search_results["results"]:
        search_context = [{"url": obj["url"], "content": obj["content"]} for obj in search_results["results"]]
        image_urls = []
        if "VISION_MODELS" in st.secrets:
            if st.session_state.model_name in st.secrets['VISION_MODELS']:
                image_urls = search_results["images"]
        return search_rag_prompt(search_context, st.session_state.messages, image_urls)
    else:
        if trace:
            end_trace("No search results found", "WARNING")
        abort_chat("I'm sorry, There was an error in search. Please try again.")

async def generate_answer_prompt():
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
            
        if st.session_state.search_results:
            display_search_result(st.session_state.search_results)      
        status.update(label="Task completed!", state="complete", expanded=False)
    return prompt, followup_query_asyncio

async def generate_summary_prompt():
    with st.status("📝 Reading through the document...", expanded=False) as status:
        st.toast("Process may take a while, please wait...", icon="⏳")
        query = st.session_state.messages[-1]["content"]
        all_texts = all_points(st.session_state.collection_name, st.session_state.knowledge_in_memory)
        tasks = [llm_generate(key_points_prompt(text), "Key Points") for text in all_texts]
        key_points = await asyncio.gather(*tasks)
        status.update(label="Task completed!", state="complete", expanded=False)
    key_points = "\n".join([f"{point}" for point in key_points])
    return summary_prompt(query, key_points)
