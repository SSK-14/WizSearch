# Ollama Setup with WizSearch 🦙✨

## ⏳ Download Ollama
Start by downloading the Ollama application from the official website: [Ollama Download](https://ollama.com/). 
Once installed, Ollama will be running at: http://localhost:11434

## 📦 Pull a Model
Explore the various models available in the Ollama library: [Ollama Library](https://ollama.com/library?sort=popular). 

To run a model, use the following command:
```
ollama pull llama3.1
```

Recommended Models:
- Llama3.1
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

3. Set up your `secrets.toml` file
Create a `secrets.toml` file in .streamlit folder [Refer](../.streamlit/example.secrets.toml).
Add the following values:
```
MODEL_BASE_URL = "http://localhost:11434/v1"
MODEL_NAMES = ["llama3.1", "llava"] 
VISION_MODELS = ["llava"]
TAVILY_API_KEY = "Your Tavily API Key"
QDRANT_URL = "Your Qdrant URL" Eg: "http://localhost:6333"
QDRANT_API_KEY = "Your Qdrant API Key" (optional for cloud deployments)
```

4. Running
```
streamlit run app.py 
```