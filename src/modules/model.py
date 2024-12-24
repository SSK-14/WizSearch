import streamlit as st
import litellm
import yaml, os

litellm.modify_params = True
litellm.drop_params = True

if os.environ.get("LANGFUSE_SECRET_KEY") and os.environ.get("LANGFUSE_PUBLIC_KEY"):
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
            if "model_info" in model and "supports_vision" in model["model_info"]:
                return model["model_info"]["supports_vision"]
            else:
                return False
    return False

def select_model(model_name):
    model_list = CONFIG.get("model_list", [])
    for model in model_list:
        if model["model_name"] == model_name:
            return model["litellm_params"]["model"]
    return None

def get_llm_params(prompt, name, stream=False):
    params = {
        "model": select_model(st.session_state.model_name),
        "messages": prompt,
        "metadata": {
            "generation_name": name,
            "trace_id": st.session_state.trace.id,
        },
        "max_tokens": st.session_state.max_tokens,
        "temperature": st.session_state.temperature,
    }
    if stream:
        params["stream"] = True
    return params

async def llm_generate(prompt, name="llm-generate"):
    params = get_llm_params(prompt, name)
    result = litellm.completion(**params)['choices'][0]['message']['content']
    return result

def llm_stream(prompt, name="llm-stream"):
    params = get_llm_params(prompt, name, stream=True)
    st.session_state.messages.append({"role": "assistant", "content": ""})
    for chunk in litellm.completion(**params):
        st.session_state.messages[-1]["content"] += str(chunk['choices'][0]['delta']['content'])
        yield str(chunk['choices'][0]['delta']['content'])
