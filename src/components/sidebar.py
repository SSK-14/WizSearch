import streamlit as st
from src.modules.model import model_options

def side_info():
    with st.sidebar:
        st.image("src/assets/title.png")
        st.image("src/assets/logo.png")
        st.warning("🌟 Your super-smart AI assistant! Just ask, and watch as it finds exactly what you need, like magic!")

        if "MODEL_API_TOKEN" not in st.secrets:
            st.text_input(
                "Openai API Key",
                type="password",
                placeholder="Paste your api key here",
                help="You can get your API key from https://platform.openai.com/account/api-keys",
                key="model_api_key"
            )

        if "TAVILY_API_KEY" not in st.secrets:
            st.text_input(
                "Tavily API Key",
                type="password",
                placeholder="Paste your tavily key here",
                help="You can get your API key from https://app.tavily.com/home",
                key="tavily_api_key"
            )

        st.sidebar.selectbox("Select a model", list(model_options.keys()), key="model_name")
        with st.popover("More settings", use_container_width=True):
            st.slider(
                "Temperature", min_value=0.0, max_value=2.0, step=0.1, value=0.1, key="temperature"
            )
            st.slider(
                "Max Tokens", min_value=0, max_value=8000, value=2500, key="max_tokens"
            )

        st.markdown("---")
        st.link_button("🔗 Source Code", "https://github.com/SSK-14/WizSearch", use_container_width=True)