"""LLM configuration and initialization."""

from langchain.schema import BaseChatModel
from langchain_community.chat_models import ChatOllama
from langchain_openai import ChatOpenAI

from .utils import load_config


def get_llm() -> BaseChatModel:
    """Initialize and return the appropriate LLM based on configuration.

    Returns:
        BaseChatModel: Initialized LLM instance
    """
    config = load_config()

    if config["llm_provider"].upper() == "OPENAI":
        return ChatOpenAI(api_key=config["openai_api_key"], model_name=config["openai_model_name"], temperature=0.7)
    elif config["llm_provider"].upper() == "OLLAMA":
        return ChatOllama(base_url=config["ollama_base_url"], model=config["ollama_model_name"], temperature=0.7)
    else:
        raise ValueError(f"Unsupported LLM provider: {config['llm_provider']}")
