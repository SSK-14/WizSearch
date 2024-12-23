# Ollama Setup with WizSearch 🦙✨

## ⏳ Download Ollama
Start by downloading the Ollama application from the official website: [Ollama Download](https://ollama.com/). 
Once installed, Ollama will be running at: http://localhost:11434

## 📦 Pull a Model
Explore the various models available in the Ollama library: [Ollama Library](https://ollama.com/library?sort=popular). 

To run a model, use the following command:
```
ollama pull llama3.2
```

Recommended Models:
- Llama3.2
- Llava (Vision model)

## 🌐 Tavily
Get your tavily api key by signing up at https://app.tavily.com/home

## 📚 Qdrant Database (Optional) 
- Use qdrant cloud:
1. Sign up at https://cloud.qdrant.io/
2. Create your cluster 
3. Get url database URL and API key

- Run qdrant in local using docker:
```
docker run -p 6333:6333 -p 6334:6334 qdrant/qdrant
```

## 🚀 Serve with Wiz
1. Clone the repo
```
git clone https://github.com/SSK-14/WizSearch.git
```

2. Install required libraries

- Create virtual environment
```
pip3 install virtualenv
python3 -m venv {your-venvname}
source {your-venvname}/bin/activate
```

- Install required libraries
```
pip3 install -r requirements.txt
```

- Activate your virtual environment
```
source {your-venvname}/bin/activate
```

3. Set up your `config.yaml` file
Update a `config.yaml` file in root folder [Refer](../example.config.yaml).
Add the following values:
```
model_list:
  - model_name: llava
    litellm_params:
      model: "ollama/llava"
    model_info:
      supports_vision: True
  - model_name: "llama3.2"
    litellm_params:
      model: "ollama_chat/llama3.2"
```

4. Create a `.env` file in root folder [Refer](../example.env)
Add the following values:
```
TAVILY_API_KEY=
QDRANT_URL=
```
Other optional keys can be added as per the requirements

5. Running
```
streamlit run app.py 
```