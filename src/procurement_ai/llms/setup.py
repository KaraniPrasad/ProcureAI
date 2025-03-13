from langchain_groq import ChatGroq
import os

def get_groq_llm():
    return ChatGroq(
        temperature=0.7,
        model_name="mixtral-8x7b-32768",  # Correct model name
        groq_api_key=os.getenv("GROQ_API_KEY")  # Add API key
    )