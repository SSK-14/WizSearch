import streamlit as st
import replicate

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

