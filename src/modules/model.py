import streamlit as st
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from openai import OpenAI

MODEL_PROVIDER = "openai"

model_options = {
    "GPT-4o": "gpt-4o",
    "GPT-3.5 Turbo-16k": "gpt-3.5-turbo-16k",
    "GPT-4 Turbo": "gpt-4-1106-preview",
    "GPT-4": "gpt-4",
}

def initialise_model():
    if "llm" not in st.session_state:
        st.session_state.llm = None
    if "MODEL_API_TOKEN" in st.secrets:
        model_api_token = st.secrets['MODEL_API_TOKEN']
        st.session_state.model_api_key = model_api_token
    if "model_api_key" not in st.session_state or not st.session_state.model_api_key:
        st.warning('Please provide openai API key in the sidebar.', icon="⚠️")
        st.stop()
    st.session_state.llm = ChatOpenAI(
        model=model_options[st.session_state.model_name] or "gpt-4o",
        temperature=st.session_state.temperature or 0.1,
        max_tokens=st.session_state.max_tokens or 2500,
        api_key=st.session_state.model_api_key
    )
    st.session_state.embeddings = OpenAIEmbeddings(api_key=st.session_state.model_api_key, model="text-embedding-3-small")
    st.session_state.openai_client = OpenAI(api_key=st.session_state.model_api_key)


async def llm_generate(prompt, trace, name="llm-generate"):
    generation = trace.generation(
        name=name,
        model=MODEL_PROVIDER,
        input=prompt,
    )
    result = st.session_state.llm.invoke(prompt).content
    generation.end(output=result)
    return result

def llm_stream(prompt, trace, name="llm-stream"):
    generation = trace.generation(
        name=name,
        model=MODEL_PROVIDER,
        input=prompt,
    )
    st.session_state.messages.append({"role": "assistant", "content": ""})
    for chunk in st.session_state.llm.stream(prompt):
        st.session_state.messages[-1]["content"] += str(chunk.content)
        yield str(chunk.content)
    generation.end(output=st.session_state.messages[-1]["content"])

