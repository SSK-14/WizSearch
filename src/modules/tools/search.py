import streamlit as st
import requests
import os
from tavily import TavilyClient
from dotenv import load_dotenv

load_dotenv()

def initialise_tavily():
    tavily_api_key = os.environ.get("TAVILY_API_KEY")
    if tavily_api_key:
        return TavilyClient(api_key=tavily_api_key)
    elif "tavily_api_key" in st.session_state:
        tavily_api_key = st.session_state.tavily_api_key
    else:
        st.warning('Please provide Tavily API key in the sidebar.', icon="⚠️")
        st.stop()

    return TavilyClient(api_key=tavily_api_key)

def jina_reader(url):
    response = requests.get("https://r.jina.ai/"+url)
    return response.text
