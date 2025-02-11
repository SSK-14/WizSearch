import asyncio
from typing import Tuple, List, Optional
import streamlit as st
from src.modules.model import model
from src.components.chat import display_search_result
from src.modules.tools.vectorstore import vector_store
from src.modules.prompt import intent_prompt, search_rag_prompt, standalone_query_prompt
from src.utils import abort_chat
from src.modules.tools.search import initialise_tavily
from src.modules.tools.langfuse import end_trace
from src.modules.prompt import base_prompt, query_formatting_prompt, generate_prompt, followup_query_prompt, key_points_prompt, summary_prompt

async def process_query() -> Tuple[str, str]:
    """Process the user query and determine intent.
    
    Returns:
        Tuple[str, str]: Processed query and intent
    """
    try:
        query = st.session_state.messages[-1]["content"]
        
        # Handle conversation history
        if len(st.session_state.messages) > 3:
            history = st.session_state.messages[:-1]
            query = await model.generate(standalone_query_prompt(query, history), "Standalone Query")
            st.write(f"❓ Standalone query: {query}")
            
        st.write("🔄 Processing your query...")
        
        # Get intent in parallel with query processing
        intent_task = asyncio.create_task(model.generate(intent_prompt(query), "Intent"))
        intent = await intent_task
        intent = intent.strip().lower()
        
        st.write(f"🔍 Intent validated...")
        return query, intent
        
    except Exception as e:
        abort_chat(f"Error processing query: {str(e)}")
        raise

async def search_vectorstore(query: str) -> Optional[List]:
    """Search vector store for relevant documents.
    
    Args:
        query: Search query
        
    Returns:
        Optional[List]: Search results prompt if found
    """
    try:
        trace = st.session_state.trace
        st.write("📚 Searching the document...")
        
        if trace:
            retrieval = trace.span(name="Retrieval", metadata={"search": "document"}, input=query)
            
        search_results = vector_store.search(
            st.session_state.collection_name,
            query,
            st.session_state.top_k,
            st.session_state.knowledge_in_memory
        )
        st.session_state.search_results = search_results
        
        if trace:
            retrieval.end(output=search_results)
            
        if search_results:
            return search_rag_prompt(search_results, st.session_state.messages)
            
    except Exception as e:
        if trace:
            end_trace(f"Vector store search error: {str(e)}", "ERROR")
        abort_chat(f"Error searching vector store: {str(e)}")
        raise

async def search_tavily(query: str) -> Optional[List]:
    """Search web using Tavily API.
    
    Args:
        query: Search query
        
    Returns:
        Optional[List]: Search results prompt if found
    """
    try:
        tavily = initialise_tavily()
        trace = st.session_state.trace
        st.write("🌐 Searching the web...")
        
        if trace:
            retrieval = trace.span(name="Retrieval", metadata={"search": "tavily"}, input=query)
            
        search_results = tavily.search(
            query,
            search_depth="advanced",
            include_images=st.session_state.image_search,
            max_results=st.session_state.top_k
        )
        st.session_state.search_results = search_results
        
        if trace:
            retrieval.end(output=search_results)
            
        if search_results["results"]:
            search_context = [
                {"url": obj["url"], "content": obj["content"]}
                for obj in search_results["results"]
            ]
            image_urls = []
            if model.supports_vision(st.session_state.model_name):
                image_urls = search_results["images"]
            return search_rag_prompt(search_context, st.session_state.messages, image_urls)
            
        if trace:
            end_trace("No search results found", "WARNING")
        abort_chat("I'm sorry, There was an error in search. Please try again.")
        
    except Exception as e:
        if trace:
            end_trace(f"Tavily search error: {str(e)}", "ERROR")
        abort_chat(f"Error searching web: {str(e)}")
        raise

async def generate_answer_prompt() -> Tuple[List, asyncio.Task]:
    """Generate answer prompt based on query intent.
    
    Returns:
        Tuple[List, asyncio.Task]: Generated prompt and followup query task
    """
    try:
        with st.status("🚀 AI at work...", expanded=True) as status:
            # Process query and get followup in parallel
            query_task = asyncio.create_task(process_query())
            followup_query_task = asyncio.create_task(
                model.generate(followup_query_prompt(st.session_state.messages), "Follow-up Query")
            )
            
            query, intent = await query_task
            
            # Handle different intents
            if len(st.session_state.image_data):
                prompt = generate_prompt(query, st.session_state.messages, st.session_state.image_data)
                
            elif "search" in intent:
                # Format query and search in parallel
                query = await model.generate(query_formatting_prompt(query), "Query Formatting")
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
            
            return prompt, followup_query_task
            
    except Exception as e:
        abort_chat(f"Error generating answer: {str(e)}")
        raise

async def generate_summary_prompt() -> str:
    """Generate summary prompt from all documents.
    
    Returns:
        str: Generated summary prompt
    """
    try:
        with st.status("📝 Reading through the document...", expanded=False) as status:
            st.toast("Process may take a while, please wait...", icon="⏳")
            
            query = st.session_state.messages[-1]["content"]
            all_texts = vector_store.get_all_documents(
                st.session_state.collection_name,
                st.session_state.knowledge_in_memory
            )
            
            # Process key points in parallel
            key_point_tasks = [
                model.generate(key_points_prompt(text), "Key Points")
                for text in all_texts
            ]
            key_points = await asyncio.gather(*key_point_tasks)
            
            status.update(label="Task completed!", state="complete", expanded=False)
            
            key_points = "\n".join([f"{point}" for point in key_points])
            return summary_prompt(query, key_points)
            
    except Exception as e:
        abort_chat(f"Error generating summary: {str(e)}")
        raise
