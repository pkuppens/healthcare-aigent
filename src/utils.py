"""Utility functions for the healthcare multi-agent system."""

import os
from typing import Any

from dotenv import load_dotenv


def load_config() -> dict[str, Any]:
    """Load configuration variables from .env file.

    Returns:
        Dict[str, Any]: Dictionary containing configuration variables
    """
    load_dotenv()

    config = {
        "openai_api_key": os.getenv("OPENAI_API_KEY"),
        "openai_model_name": os.getenv("OPENAI_MODEL_NAME", "gpt-3.5-turbo"),
        "ollama_base_url": os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"),
        "ollama_model_name": os.getenv("OLLAMA_MODEL_NAME", "llama3"),
        "llm_provider": os.getenv("LLM_PROVIDER", "OPENAI"),
    }

    return config
