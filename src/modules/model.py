import streamlit as st
from langchain_openai import ChatOpenAI
from openai import OpenAI

MODEL = "openai"

def initialise_model():
    if "llm" not in st.session_state:
        st.session_state.llm = None
    if "MODEL_API_TOKEN" in st.secrets:
        model_api_token = st.secrets['MODEL_API_TOKEN']
        st.session_state.model_api_key = model_api_token
    if "model_api_key" not in st.session_state:
        st.warning('Please provide openai API key in the sidebar.', icon="⚠️")
        st.stop()
    st.session_state.llm = ChatOpenAI(model="gpt-4o", api_key=st.session_state.model_api_key)
    st.session_state.openai_client = OpenAI(api_key=st.session_state.model_api_key)


async def llm_generate(prompt, trace, name="llm-generate"):
    generation = trace.generation(
        name=name,
        model=MODEL,
        input=prompt,
    )
    result = st.session_state.llm.invoke(prompt).content
    generation.end(output=result)
    return result

def llm_stream(prompt, trace, name="llm-stream"):
    generation = trace.generation(
        name=name,
        model=MODEL,
        input=prompt,
    )
    st.session_state.messages.append({"role": "assistant", "content": ""})
    for chunk in st.session_state.llm.stream(prompt):
        st.session_state.messages[-1]["content"] += str(chunk.content)
        yield str(chunk.content)
    generation.end(output=st.session_state.messages[-1]["content"])

