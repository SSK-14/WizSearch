import os
import streamlit as st
from langfuse import Langfuse

os.environ["LANGFUSE_HOST"] = "https://cloud.langfuse.com"
if os.environ.get("LANGFUSE_SECRET_KEY") and os.environ.get("LANGFUSE_PUBLIC_KEY"):
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
