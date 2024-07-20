import streamlit as st
from src.modules.model import model_options

def side_info():
    with st.sidebar:
        st.logo("src/assets/ssk.png", icon_image="src/assets/title.png", link="https://github.com/SSK-14")
        st.image("src/assets/title.png")
        st.image("src/assets/logo.png")
        card_html = """
        <div style="background-color: #0E1117; border: 2px solid #DE834D; border-radius: 10px; padding: 0px 8px; width: 100%; box-sizing: border-box; color: white; text-align: center; font-family: 'Arial', sans-serif; font-size: 14px; color: #FAFAFA;">
            <p>🌟 Your super-smart AI assistant! Just ask, and watch as it finds exactly what you need, like magic!</p>
        </div>
        """
        st.components.v1.html(card_html, height=100, scrolling=False)

        if "OLLAMA_SERVER_URL" not in st.secrets:
            st.text_input(
                "Ollama Server Url",
                placeholder="Paste your url here",
                value="http://localhost:11434",
                key="ollama_server_url",
                help="Checkout [Ollama setup](https://github.com/SSK-14/WizSearch/blob/main/docs/OLLAMA.md)"
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