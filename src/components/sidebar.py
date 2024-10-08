import json
import streamlit as st
from streamlit_lottie import st_lottie
from src.modules.tools.vectorstore import all_collections, delete_collection, collection_info

@st.dialog("View knowledge")
def system_settings():
    collections = all_collections()
    st.write(f"### :orange[Total documents] : **{len(collections)}**")
    if len(collections):
        col1, col2 = st.columns([4, 1])
        collection_name = col1.selectbox("Select a document", collections, index=0, label_visibility="collapsed")
        if col2.button("🗑️", use_container_width=True):
            delete_collection(collection_name)
            st.rerun()
        if collection_name:
            collection = collection_info(collection_name)
            col1, col2, col3 = st.columns(3)
            col1.metric(label="Status", value=collection.status.name)
            col2.metric(label="Points Count", value=collection.points_count)
            if 'text-dense' in collection.config.params.vectors:
                col3.metric(label="Dense Vector Size", value=collection.config.params.vectors['text-dense'].size) 
    else:
        st.warning("No documents found")

def side_info():
    with st.sidebar:
        st.logo("src/assets/title.png", icon_image="src/assets/title.png", link="https://github.com/SSK-14")
        st.image("src/assets/header.png", use_column_width=True)
        with open("src/assets/header.json","r") as file: 
                url = json.load(file) 
        st_lottie(url)

        if "MODEL_BASE_URL" not in st.secrets:
            st.text_input("Model Base URL", key="model_base_url", value="https://api.groq.com/openai/v1", placeholder="Eg : https://api.openai.com/v1")

        if "MODEL_API_KEY" not in st.secrets:
            st.text_input(
                "Model API Key",
                type="password",
                placeholder="Enter your API key here",
                help="Get your API key from [openai](https://platform.openai.com/account/api-keys) or [groq](https://console.groq.com/keys)",
                key="model_api_key"
            )

        if "MODEL_NAMES" not in st.secrets:
            st.text_input("Model ID", key="model_name", value="llama-3.1-8b-instant", placeholder="Eg : gpt-4o, llama3.1")

        if "MODEL_NAMES" in st.secrets:
            st.selectbox(
                "Select Model",
                options=st.secrets["MODEL_NAMES"],
                index=0,
                key="model_name"
            )

        if "TAVILY_API_KEY" not in st.secrets:
            st.text_input(
                "Tavily API Key",
                type="password",
                placeholder="Paste your tavily key here",
                help="You can get your API key from https://app.tavily.com/home",
                key="tavily_api_key"
            )

        with st.popover("⚙️ Wiz Settings", use_container_width=True):
            st.slider("Temperature", min_value=0.0, max_value=2.0, step=0.1, value=0.1, key="temperature")
            st.slider("Max tokens", min_value=0, max_value=8000, value=2500, key="max_tokens")
            st.slider("Top search results", min_value=1, max_value=10, value=4, key="top_k")
            st.checkbox("Use image search", key="image_search", value=True)

        if st.button("📚 My knowledge's", use_container_width=True):
            system_settings()

        st.markdown("---")
        st.link_button("🔗 Source Code", "https://github.com/SSK-14/WizSearch", use_container_width=True)