#!/bin/bash

# Step 1: Check if Python is installed
if ! command -v python3 &> /dev/null
then
    echo "Python3 is not installed. Please install Python3 to proceed."
    exit
fi

# Step 2: Check if Ollama is installed
if ! command -v ollama &> /dev/null
then
    echo "Ollama is not installed. Please install Ollama to proceed."
    exit
fi

# Step 3: Check if Ollama is running
if ! pgrep -x "ollama" > /dev/null
then
    echo "Ollama is not running. Please start Ollama."
    exit
else
    echo "Ollama is running."
fi

# Optional: Check where Ollama is running (on a specific port)
OLLAMA_PORT=11434
if lsof -Pi :$OLLAMA_PORT -sTCP:LISTEN -t >/dev/null ; then
    echo "Ollama is running on port $OLLAMA_PORT"
else
    echo "Ollama is not running on port $OLLAMA_PORT. Please start it on the correct port."
    exit
fi

# Step 4: Check if 'llava' and 'llama3.1' models are pulled by Ollama
MODELS=("llava" "llama3.1")
for model in "${MODELS[@]}"
do
    if ollama list | grep -q "$model"; then
        echo "Model '$model' is pulled in Ollama."
    else
        echo "Model '$model' is not found. Please pull the model using 'ollama pull $model'."
        exit
    fi
done

# Step 5: Check if Qdrant is running
QDRANT_PORT=6333
if lsof -Pi :$QDRANT_PORT -sTCP:LISTEN -t >/dev/null ; then
    QDRANT_URL="http://localhost:$QDRANT_PORT"
    echo "Qdrant is running on port $QDRANT_PORT"
else
    QDRANT_URL="./temp"  # Default to a file path for persistence
    echo "Qdrant is not running. Defaulting to temporary path: $QDRANT_URL"
fi

# Step 6: Create a virtual environment
echo "Creating virtual environment..."
python3 -m venv venv

# Activate the virtual environment
source venv/bin/activate

# Step 7: Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

# Step 8: Create a secrets.toml file
mkdir -p .streamlit
cat <<EOT > .streamlit/secrets.toml
IS_AZURE = false
MODEL_BASE_URL = "http://localhost:$OLLAMA_PORT/v1"
MODEL_API_KEY = ""
MODEL_NAMES = ["llava", "llama3.1"]
VISION_MODELS = ["llava"]
QDRANT_URL = "$QDRANT_URL"
EOT
echo "secrets.toml file created."

# Step 9: Run the Streamlit app
echo "Starting the Streamlit app..."
streamlit run app.py
