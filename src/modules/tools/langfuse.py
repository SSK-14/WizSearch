import os
import streamlit as st
from langfuse import Langfuse

if "LANGFUSE_SECRET_KEY" in st.secrets or "LANGFUSE_PUBLIC_KEY" in st.secrets:
    os.environ["LANGFUSE_SECRET_KEY"] = st.secrets["LANGFUSE_SECRET_KEY"]
    os.environ["LANGFUSE_PUBLIC_KEY"] = st.secrets["LANGFUSE_PUBLIC_KEY"]
    os.environ["LANGFUSE_HOST"] = "https://cloud.langfuse.com" 
    langfuse = Langfuse()
else:
    langfuse = None

def start_trace(query, name="AI Search"):
    if langfuse is None:
        st.session_state.trace = None
        return
    trace = langfuse.trace(name=name, input=query)
    st.session_state.trace = trace
    
def end_trace(output, level="DEFAULT"):
    if langfuse is None:
        return
    trace = st.session_state.trace
    trace.update(output=output, level=level)