import os
import streamlit as st
import replicate

def initialise_replicate():
    if "REPLICATE_API_TOKEN" in st.secrets:
        os.environ['REPLICATE_API_TOKEN'] = st.secrets['REPLICATE_API_TOKEN']
    elif st.session_state.replicate_api_key:
        os.environ['REPLICATE_API_TOKEN'] = st.session_state.replicate_api_key
    else:
        st.warning('Please provide Replicate API key in the sidebar.', icon="⚠️")
        st.stop()

MODEL = "snowflake/snowflake-arctic-instruct"

async def llm_generate(prompt, trace, name="llm-generate"):
    generation = trace.generation(
        name=name,
        model=MODEL,
        input=prompt,
    )
    input = {
        "prompt": prompt,
    }
    output = replicate.run(MODEL,input=input)
    result = "".join(output)
    generation.end(output=result)
    return result

def llm_stream(prompt, trace, name="llm-stream"):
    generation = trace.generation(
        name=name,
        model=MODEL,
        input=prompt,
    )
    st.session_state.messages.append({"role": "assistant", "content": ""})
    input = {
        "prompt": prompt,
        "prompt_template": r"{prompt}",
        "temperature": st.session_state.temperature,
        "top_p": st.session_state.top_p,
    }
    for event_index, event in enumerate(replicate.stream(MODEL,input=input)):
        st.session_state.messages[-1]["content"] += str(event)
        yield str(event)
    generation.end(output=st.session_state.messages[-1]["content"])

