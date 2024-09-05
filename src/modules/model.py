import streamlit as st
from langchain_openai import ChatOpenAI, AzureChatOpenAI

if "IS_AZURE" in st.secrets:
    is_azure = st.secrets["IS_AZURE"]
else:
    is_azure = False

def initialise_model():
    if "llm" not in st.session_state:
        st.session_state.llm = None

    if "MODEL_BASE_URL" in st.secrets:
        model_base_url = st.secrets['MODEL_BASE_URL']
    elif st.session_state.model_base_url:
        model_base_url = st.session_state.model_base_url
    else:
        st.warning('Please provide Model Base URL in sidebar.', icon="⚠️")
        st.stop()
    
    if "MODEL_API_KEY" in st.secrets:
        model_api_key = st.secrets['MODEL_API_KEY']
    elif st.session_state.model_api_key:
        model_api_key = st.session_state.model_api_key
    else:
        st.warning('Please provide Model API key in sidebar.', icon="⚠️")
        st.stop()

    if st.session_state.model_name is None or st.session_state.model_name == "":
        st.warning('Please provide Model Name in sidebar.', icon="⚠️")
        st.stop()
    
    if is_azure:
        st.session_state.llm = AzureChatOpenAI(
            model=st.session_state.model_name,
            api_version = "2024-02-01",
            temperature=st.session_state.temperature or 0.1,
            max_tokens=st.session_state.max_tokens or 2500,
            azure_endpoint=model_base_url,
            api_key=model_api_key
        )
    else:
        st.session_state.llm = ChatOpenAI(
            model=st.session_state.model_name,
            temperature=st.session_state.temperature or 0.1,
            max_tokens=st.session_state.max_tokens or 2500,
            base_url=model_base_url,
            api_key=model_api_key
        )

async def llm_generate(prompt, name="llm-generate"):
    trace = st.session_state.trace
    if trace:
        generation = trace.generation(
            name=name,
            model=st.session_state.model_name,
            input=prompt,
        )
    result = st.session_state.llm.invoke(prompt).content
    if trace:
        generation.end(output=result)
    return result

def llm_stream(prompt, name="llm-stream"):
    trace = st.session_state.trace
    if trace:
        generation = trace.generation(
            name=name,
            model=st.session_state.model_name,
            input=prompt,
        )
    st.session_state.messages.append({"role": "assistant", "content": ""})
    for chunk in st.session_state.llm.stream(prompt):
        st.session_state.messages[-1]["content"] += str(chunk.content)
        yield str(chunk.content)
    if trace:
        generation.end(output=st.session_state.messages[-1]["content"])

