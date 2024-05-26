import streamlit as st

def side_info():
    with st.sidebar:
        st.image("src/assets/title.png")
        st.image("src/assets/logo.png")
        st.markdown(">🌟 Your super-smart AI assistant! Just ask, and watch as it finds exactly what you need, like magic!")

        if "REPLICATE_API_TOKEN" not in st.secrets:
            st.text_input(
                "Replicate API Key",
                type="password",
                placeholder="Paste your replicate key here",
                help="You can get your API key from https://replicate.com/account/api-tokens.",
                key="replicate_api_key"
            )

        if "TAVILY_API_KEY" not in st.secrets:
            st.text_input(
                "Tavil API Key",
                type="password",
                placeholder="Paste your tavil key here",
                help="You can get your API key from https://app.tavily.com/home",
                key="tavily_api_key"
            )

        with st.popover("More settings", use_container_width=True):
            st.slider('temperature', min_value=0.01, max_value=5.0, value=0.3,
                                step=0.01, key="temperature")
            st.slider('top_p', min_value=0.01, max_value=1.0, value=0.9, step=0.01,
                            key="top_p")
        
        st.markdown("---")
        st.image("src/assets/devpost.png")
        st.link_button("🔗 Source Code", "https://github.com/SSK-14/WizSearch", use_container_width=True)