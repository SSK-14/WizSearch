import streamlit as st
from streamlit_feedback import streamlit_feedback

def display_chat_messages(messages):
    icons = {"assistant": "./src/assets/logo.svg", "user": "👤"}
    for message in messages:
        with st.chat_message(message["role"], avatar=icons[message["role"]]):
            st.markdown(message["content"])

def display_search_result(search_results):
    with st.expander("Image Results", expanded=False):
        col1, col2, col3, col4, col5 = st.columns(5)
        col1.image(search_results["images"][0], use_column_width=True)
        col2.image(search_results["images"][1], use_column_width=True)
        col3.image(search_results["images"][2], use_column_width=True)
        col4.image(search_results["images"][3], use_column_width=True)
        col5.image(search_results["images"][4], use_column_width=True)

    with st.expander("Search Results", expanded=False):
        for result in search_results["results"]:
            st.write(f"- [{result['title']}]({result['url']})")

def abort_chat(error_message: str):
    assert error_message, "Error message must be provided."
    error_message = f":red[{error_message}]"
    if st.session_state.messages[-1]["role"] != "assistant":
        st.session_state.messages.append({"role": "assistant", "content": error_message})
    else:
        st.session_state.messages[-1]["content"] = error_message
    st.session_state.chat_aborted = True
    st.rerun()

def feedback():
    trace = st.session_state.trace
    scores = {"😀": 1, "🙂": 0.75, "😐": 0.5, "🙁": 0.25, "😞": 0}
    if "feedback_" + trace.id not in st.session_state:
        streamlit_feedback(
            feedback_type="faces",
            optional_text_label="[Optional] Please provide an explanation",
            key=f"feedback_{trace.id}",
        )
    else:
        feedback = st.session_state["feedback_" + trace.id]
        trace.score(
            name="user-explicit-feedback",
            value=scores[feedback["score"]],
            comment=feedback["text"],
        )