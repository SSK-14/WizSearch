import streamlit as st

def side_info():
    with st.sidebar:
        st.image("src/assets/title.png")
        st.image("src/assets/side-logo.png")
        st.markdown(">🌟 Your super-smart AI assistant! Just ask, and watch as it finds exactly what you need, like magic!")
        st.image("src/assets/devpost.png")
        with st.expander("More settings"):
            st.slider('temperature', min_value=0.01, max_value=5.0, value=0.3,
                                step=0.01, key="temperature")
            st.slider('top_p', min_value=0.01, max_value=1.0, value=0.9, step=0.01,
                            key="top_p")