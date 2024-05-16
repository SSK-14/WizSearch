import streamlit as st

def side_info():
    with st.sidebar:
        st.title("Personal Search Assistant")
        st.info("⚡ Your intelligent ally for effortless data retrieval and seamless browsing across databases and the web.✨", icon="ℹ️")
        st.markdown("---")
        st.image("src/assets/chat.svg")