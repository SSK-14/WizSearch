import os
from langchain_openai import ChatOpenAI

def init_llm():
    return ChatOpenAI(
        openai_api_key=os.getenv("OPENAI_API_KEY"),
        model_name="gpt-3.5-turbo-16k",
        temperature=0.1,
    )

