import streamlit as st
import litellm
import yaml

litellm.modify_params = True
litellm.success_callback = ["langfuse"]
litellm.failure_callback = ["langfuse"]

config_path = "config.yaml"
with open(config_path, "r") as file:
    CONFIG = yaml.safe_load(file)

def model_list():
    models = [model["model_name"] for model in CONFIG.get("model_list", [])]
    return models

def is_vision_model(model_name):
    model_list = CONFIG.get("model_list", [])
    for model in model_list:
        if model["model_name"] == model_name:
            return model["model_info"].get("supports_vision", False)
    return False

def select_model(model_name):
    model_list = CONFIG.get("model_list", [])
    for model in model_list:
        if model["model_name"] == model_name:
            api_key = model["litellm_params"].get("api_key")
            if api_key:
                litellm.api_key = st.secrets[api_key]
            return model["litellm_params"]["model"]
    return None


async def llm_generate(prompt, name="llm-generate"):
    model = select_model(st.session_state.model_name)
    result = litellm.completion(
        model=model,
        messages=prompt,
        metadata={
            "generation_name": name,
            "trace_id": st.session_state.trace.id,
        },
    )['choices'][0]['message']['content']
    return result

def llm_stream(prompt, name="llm-stream"):
    model = select_model(st.session_state.model_name)
    metadata = {
        "generation_name": name,
        "trace_id": st.session_state.trace.id,
    }
    st.session_state.messages.append({"role": "assistant", "content": ""})
    for chunk in litellm.completion(model=model, messages=prompt, stream=True, metadata=metadata):
        st.session_state.messages[-1]["content"] += str(chunk['choices'][0]['delta']['content'])
        yield str(chunk['choices'][0]['delta']['content'])

