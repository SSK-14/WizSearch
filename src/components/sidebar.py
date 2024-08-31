import streamlit as st

def side_info():
    with st.sidebar:
        st.logo("src/assets/title.png", icon_image="src/assets/title.png", link="https://github.com/SSK-14")
        st.image("src/assets/logo.png", use_column_width=True)
        st.image("src/assets/header.png", use_column_width=True)

        if "MODEL_NAMES" in st.secrets:
            st.selectbox(
                "Model Name",
                options=st.secrets["MODEL_NAMES"],
                index=0,
                key="model_name"
            )

        if "MODEL_API_KEY" not in st.secrets:
            st.text_input(
                "Model API Key",
                type="password",
                placeholder="Paste your model key here",
                help="You can get your API key from [openai](https://platform.openai.com/account/api-keys)",
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

        with st.popover("More settings", use_container_width=True):
            if "collection_name" in st.session_state:
                st.slider("Top K results", min_value=1, max_value=10, value=4, key="top_k")

            st.slider(
                "Temperature", min_value=0.0, max_value=2.0, step=0.1, value=0.1, key="temperature"
            )
            st.slider(
                "Max Tokens", min_value=0, max_value=8000, value=2500, key="max_tokens"
            )

        st.markdown("---")
        st.link_button("🔗 Source Code", "https://github.com/SSK-14/WizSearch", use_container_width=True)