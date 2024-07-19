# Ollama Setup with Ngrok

## 🚀 Download Ollama
Start by downloading the Ollama application from the official website: [Ollama Download](https://ollama.com/). Once installed, Ollama will be running at:
http://localhost:11434

## 📦 Pull a Model
Explore the various models available in the Ollama library: [Ollama Library](https://ollama.com/library?sort=popular). To run a model, use the following command:
```
ollama run llama3
```

Recommended Models:
- Llama3
- Llava (Vision model)

## 🌐 Serve Ollama Using Ngrok

### 🔧 Install and Run Ngrok
Visit [Ngrok](https://ngrok.com/docs/getting-started/) Getting Started for installation instructions.
Follow steps 1 to 3 to set up Ngrok on your machine.

### 📡 Start Ngrok
Once Ngrok is installed, run the following command to expose your local Ollama server:
```
ngrok http 11434 --host-header="localhost:11434"
```
This command will provide you with a public URL to access your Ollama instance.

## 🎉 Try It Out
Access the Wiz search interface at: [Wiz Search](https://wizsearch-ollama.streamlit.app/).
- Add the Ngrok URL in the sidebar.
- Enjoy exploring the capabilities of Ollama!

Feel free to customize this setup to fit your needs and enjoy your demo!
