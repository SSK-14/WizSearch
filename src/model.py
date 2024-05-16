import streamlit as st
import replicate

def llm_generate(prompt):
    input = {
        "prompt": prompt,
    }
    output = replicate.run(
        "snowflake/snowflake-arctic-instruct",
        input=input
    )
    return "".join(output)

def llm_stream(prompt):
    st.session_state.messages.append({"role": "assistant", "content": ""})
    input = {
        "prompt": prompt,
        "prompt_template": r"{prompt}",
    }
    for event_index, event in enumerate(replicate.stream(
        "snowflake/snowflake-arctic-instruct",
        input=input
    )):
        st.session_state.messages[-1]["content"] += str(event)
        yield str(event)

