import streamlit as st
import requests
from tavily import TavilyClient

def initialise_tavily():
    if "TAVILY_API_KEY" in st.secrets:
        tavily_api_key = st.secrets["TAVILY_API_KEY"]
    elif "tavily_api_key" in st.session_state:
        tavily_api_key = st.session_state.tavily_api_key
    else:
        st.warning('Please provide Tavily API key in the sidebar.', icon="⚠️")
        st.stop()

    return TavilyClient(api_key=tavily_api_key)

def jina_reader(url):
    response = requests.get("https://r.jina.ai/"+url)
    return response.text
