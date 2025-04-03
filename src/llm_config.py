"""LLM configuration for healthcare system."""

import os

from langchain_community.chat_models import ChatOllama
from langchain_openai import ChatOpenAI


def get_llm(provider: str | None = None, temperature: float = 0.7) -> ChatOpenAI | ChatOllama:
    """Get LLM instance based on configuration."""
    provider = provider or os.getenv("LLM_PROVIDER", "OPENAI")

    if provider.upper() == "OPENAI":
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable not set")

        model = os.getenv("OPENAI_MODEL_NAME", "gpt-3.5-turbo")
        return ChatOpenAI(model=model, temperature=temperature, openai_api_key=api_key)

    elif provider.upper() == "OLLAMA":
        base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        model = os.getenv("OLLAMA_MODEL_NAME", "llama3")
        return ChatOllama(model=model, base_url=base_url, temperature=temperature)

    else:
        raise ValueError(f"Unsupported LLM provider: {provider}")
