"""LLM configuration for healthcare system."""

import json
import logging
import os

from langchain_community.chat_models import ChatOllama
from langchain_openai import ChatOpenAI

# Configure logging
logger = logging.getLogger(__name__)


def get_llm(provider: str | None = None, temperature: float = 0.7) -> ChatOpenAI | ChatOllama:
    """
    Get LLM instance based on configuration.

    Args:
        provider: The LLM provider to use (OPENAI or OLLAMA)
        temperature: The temperature parameter for the LLM

    Returns:
        An instance of ChatOpenAI or ChatOllama

    Raises:
        ValueError: If the provider is not supported or required environment variables are not set
    """
    provider = provider or os.getenv("LLM_PROVIDER", "OPENAI")
    provider = provider.upper()

    logger.info(f"Initializing LLM with provider: {provider}")

    if provider == "OPENAI":
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            error_msg = "OPENAI_API_KEY environment variable not set"
            logger.error(error_msg)
            raise ValueError(error_msg)

        model = os.getenv("OPENAI_MODEL_NAME", "gpt-3.5-turbo")
        logger.info(f"Using OpenAI model: {model}")

        try:
            llm = ChatOpenAI(model=model, temperature=temperature, openai_api_key=api_key)
            logger.debug(f"OpenAI LLM configuration: {json.dumps({'model': model, 'temperature': temperature}, indent=2)}")
            return llm
        except Exception as e:
            logger.error(f"Error creating OpenAI LLM: {e}")
            raise

    elif provider == "OLLAMA":
        base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        model = os.getenv("OLLAMA_MODEL_NAME", "llama3")
        logger.info(f"Using Ollama model: {model} at {base_url}")

        try:
            llm = ChatOllama(model=model, base_url=base_url, temperature=temperature)
            logger.debug(
                f"Ollama LLM configuration: {json.dumps({'model': model, 'base_url': base_url, 'temperature': temperature}, indent=2)}"
            )
            return llm
        except Exception as e:
            logger.error(f"Error creating Ollama LLM: {e}")
            raise

    else:
        error_msg = f"Unsupported LLM provider: {provider}"
        logger.error(error_msg)
        raise ValueError(error_msg)
