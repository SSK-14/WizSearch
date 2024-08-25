import streamlit as st
from langchain_openai import ChatOpenAI, AzureChatOpenAI

if "IS_AZURE" in st.secrets:
    is_azure = st.secrets["IS_AZURE"]
else:
    is_azure = False

if "MODEL_NAME" in st.secrets:
    model_name = st.secrets["MODEL_NAME"]
else:
    st.warning('Please provide Model name in secrets.', icon="⚠️")
    st.stop()

if "MODEL_BASE_URL" in st.secrets:
    model_base_url = st.secrets['MODEL_BASE_URL']
else:
    st.warning('Please provide Model server URL in secrets.', icon="⚠️")
    st.stop()

if "MODEL_API_KEY" in st.secrets:
    model_api_key = st.secrets['MODEL_API_KEY']

def initialise_model():
    if "llm" not in st.session_state:
        st.session_state.llm = None
    if is_azure:
        st.session_state.llm = AzureChatOpenAI(
            model=model_name,
            api_version = "2024-02-01",
            temperature=st.session_state.temperature or 0.1,
            max_tokens=st.session_state.max_tokens or 2500,
            azure_endpoint=model_base_url,
            api_key=model_api_key
        )
    else:
        st.session_state.llm = ChatOpenAI(
            model=model_name,
            temperature=st.session_state.temperature or 0.1,
            max_tokens=st.session_state.max_tokens or 2500,
            base_url=model_base_url,
            api_key=model_api_key
        )

async def llm_generate(prompt, trace, name="llm-generate"):
    generation = trace.generation(
        name=name,
        model=model_name,
        input=prompt,
    )
    result = st.session_state.llm.invoke(prompt).content
    generation.end(output=result)
    return result

def llm_stream(prompt, trace, name="llm-stream"):
    generation = trace.generation(
        name=name,
        model=model_name,
        input=prompt,
    )
    st.session_state.messages.append({"role": "assistant", "content": ""})
    for chunk in st.session_state.llm.stream(prompt):
        st.session_state.messages[-1]["content"] += str(chunk.content)
        yield str(chunk.content)
    generation.end(output=st.session_state.messages[-1]["content"])

