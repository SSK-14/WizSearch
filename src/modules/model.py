import streamlit as st
from langchain_community.chat_models import ChatOllama

MODEL_PROVIDER = "ollama"

model_options = {
    "Llama 3": "llama3",
    "Phi-3": "phi3",
    "LLaVA (vision)": "llava"
}

vision_models = [ "llava" ]

def initialise_model():
    if "llm" not in st.session_state:
        st.session_state.llm = None
    if "OLLAMA_SERVER_URL" in st.secrets:
        ollama_server_url = st.secrets['OLLAMA_SERVER_URL']
        st.session_state.ollama_server_url = ollama_server_url
    st.session_state.llm = ChatOllama(
        model=model_options[st.session_state.model_name] or "llama3",
        temperature=st.session_state.temperature or 0.1,
        max_tokens=st.session_state.max_tokens or 2500,
        base_url=st.session_state.ollama_server_url
    )

async def llm_generate(prompt, trace, name="llm-generate"):
    generation = trace.generation(
        name=name,
        model=model_options[st.session_state.model_name],
        input=prompt,
    )
    result = st.session_state.llm.invoke(prompt).content
    generation.end(output=result)
    return result

def llm_stream(prompt, trace, name="llm-stream"):
    generation = trace.generation(
        name=name,
        model=model_options[st.session_state.model_name],
        input=prompt,
    )
    st.session_state.messages.append({"role": "assistant", "content": ""})
    for chunk in st.session_state.llm.stream(prompt):
        st.session_state.messages[-1]["content"] += str(chunk.content)
        yield str(chunk.content)
    generation.end(output=st.session_state.messages[-1]["content"])

