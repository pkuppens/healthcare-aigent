"""LLM configuration for healthcare system."""

import os

from langchain_community.llms import Ollama
from langchain_openai import ChatOpenAI


def get_llm(model_name: str | None = None):
    """Get LLM based on configuration.

    Args:
        model_name: Optional model name to use

    Returns:
        Configured LLM instance
    """
    provider = os.getenv("LLM_PROVIDER", "OPENAI").upper()

    if provider == "OPENAI":
        api_key = os.getenv("OPENAI_API_KEY")
        model = model_name or os.getenv("OPENAI_MODEL_NAME", "gpt-3.5-turbo")
        return ChatOpenAI(openai_api_key=api_key, model=model, temperature=0.7)

    elif provider == "OLLAMA":
        base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        model = model_name or os.getenv("OLLAMA_MODEL_NAME", "llama2")
        return Ollama(base_url=base_url, model=model, temperature=0.7)

    else:
        raise ValueError(f"Unsupported LLM provider: {provider}")
