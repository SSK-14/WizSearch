import streamlit as st
from langchain_openai import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI

def initialise_model():
    if "llm" not in st.session_state:
        st.session_state.llm = None
    if "MODEL_API_TOKEN" in st.secrets and "MODEL_PROVIDER" in st.secrets:
        model_api_token = st.secrets['MODEL_API_TOKEN']
        model_provider = st.secrets['MODEL_PROVIDER']
        st.session_state.model_api_key = model_api_token
        st.session_state.model_provider = model_provider
    if "model_api_key" not in st.session_state or "model_provider" not in st.session_state:
        st.warning('Please provide model API key in the sidebar.', icon="⚠️")
        st.stop()
    
    if st.session_state.model_provider == "openai":
        st.session_state.llm = ChatOpenAI(model="gpt-4o", api_key=st.session_state.model_api_key)
    elif st.session_state.model_provider == "gemini":
        st.session_state.llm = ChatGoogleGenerativeAI(model="gemini-1.5-pro-latest", google_api_key=st.session_state.model_api_key)
    else:
        st.error("Invalid model provider")
        st.stop()

async def llm_generate(prompt, trace, name="llm-generate"):
    model_provider = st.session_state.model_provider or st.secrets['MODEL_PROVIDER']
    generation = trace.generation(
        name=name,
        model=model_provider,
        input=prompt,
    )
    result = st.session_state.llm.invoke(prompt).content
    generation.end(output=result)
    return result

def llm_stream(prompt, trace, name="llm-stream"):
    model_provider = st.session_state.model_provider or st.secrets['MODEL_PROVIDER']
    generation = trace.generation(
        name=name,
        model=model_provider,
        input=prompt,
    )
    st.session_state.messages.append({"role": "assistant", "content": ""})
    for chunk in st.session_state.llm.stream(prompt):
        st.session_state.messages[-1]["content"] += str(chunk.content)
        yield str(chunk.content)
    generation.end(output=st.session_state.messages[-1]["content"])

