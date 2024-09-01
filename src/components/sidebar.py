import streamlit as st
from src.modules.tools.vectorstore import all_collections, delete_collection

@st.dialog("Wiz Settings")
def system_settings():
    if "vectorstore" in st.session_state and st.session_state.vectorstore:
        st.slider("Top K results", min_value=1, max_value=10, value=4, key="top_k")
    col1, col2 = st.columns(2)
    col1.slider("Temperature", min_value=0.0, max_value=2.0, step=0.1, value=0.1, key="temperature")
    col2.slider("Max Tokens", min_value=0, max_value=8000, value=2500, key="max_tokens")
    collections = all_collections()
    st.subheader("Manage Documents")
    if len(collections):
        col1, col2, col3 = st.columns([4, 1, 1])
        collection_name = col1.selectbox("Select a document", collections, index=0, label_visibility="collapsed")
        if col2.button("➕", use_container_width=True):
            st.session_state.collection_name = collection_name
            st.session_state.vectorstore = True
            st.rerun()
        if col3.button("🗑️", use_container_width=True):
            delete_collection(collection_name)
            st.rerun()
    else:
        st.warning("No documents found")

def side_info():
    with st.sidebar:
        st.logo("src/assets/title.png", icon_image="src/assets/title.png", link="https://github.com/SSK-14")
        st.image("src/assets/logo.png", use_column_width=True)
        st.image("src/assets/header.png", use_column_width=True)

        if "MODEL_NAMES" in st.secrets:
            st.selectbox(
                "Select Model",
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

        if st.button("⚙️ Wiz Settings", use_container_width=True):
            system_settings()

        st.markdown("---")
        st.link_button("🔗 Source Code", "https://github.com/SSK-14/WizSearch", use_container_width=True)