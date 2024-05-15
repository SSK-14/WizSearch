import streamlit as st


def display_chat_messages(messages):
    icons = {"assistant": "./src/assets/logo.png", "user": "👤"}
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