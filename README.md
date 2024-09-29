# ✨ WizSearch
Your intelligent ally for effortless data retrieval across documents and seamless browsing the web.

## Demo 🎬
1. Get your API key [groq](https://console.groq.com/keys)
2. Checkout https://wizsearch.streamlit.app/

[Quick start with Ollama in local 🦙✨](./docs/OLLAMA.md)

https://github.com/user-attachments/assets/fa4fae96-6e78-474d-9d90-2e1d64833008

## How we built it 🛠️
We built Wiz Search using the following components:
- **LLM/VLM:** Open source models like llama3.1, mistral, LLaVA, etc are supported by platforms such as [Ollama](https://ollama.ai/) and [Groq](https://console.groq.com/docs/models). Closed source models like gpt-4o, gpt-4 supported by [OpenAI](https://platform.openai.com/docs/models) and [Azure OpenAI](https://azure.microsoft.com/en-in/products/ai-services/openai-service) for natural language understanding and generation.
- **Embeddings:** `jina-embeddings-v2-base-en` and `BM25` using [fastembed](https://github.com/qdrant/fastembed) to enhance search relevance.
- **Intelligent Search:** [Tavily](https://tavily.com/) for advanced search capabilities.
- **Vector Databases:** [Qdrant](https://qdrant.tech/) for efficient data storage and retrieval.
- **Observability:** [Langfuse](https://www.langfuse.com/) for monitoring and observability.
- **UI:** [Streamlit](https://streamlit.io/) for creating an interactive and user-friendly interface.

![Architecture](./src/assets/arch.png)

## Run The Application ⚙️
1. Clone the repo
```
git clone https://github.com/SSK-14/WizSearch.git
```

2. Installation and setup  
```
bash setup.sh
```

3. Running
```
streamlit run app.py 
```

## Contributing 🤝
Contributions to this project are welcome! If you find any issues or have suggestions for improvement, please open an issue or submit a pull request on the project's GitHub repository.

## License 📝
This project is licensed under the [MIT License](https://github.com/SSK-14/WizSearch/blob/main/LICENSE). Feel free to use, modify, and distribute the code as per the terms of the license.

