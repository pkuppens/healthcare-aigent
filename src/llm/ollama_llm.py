"""Ollama LLM implementation."""

import os
from typing import Any

import requests
from langchain.callbacks.manager import CallbackManagerForLLMRun
from langchain_community.chat_models import ChatOllama

from src.llm.base import BaseLLM
from src.llm.circuit_breaker import HTTP_OK


def check_ollama_availability() -> bool:
    """Check if Ollama service is available.

    Returns:
        True if Ollama is available, False otherwise
    """
    base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    try:
        response = requests.get(f"{base_url}/api/tags", timeout=2)
        return response.status_code == HTTP_OK
    except (requests.RequestException, TimeoutError):
        return False


class OllamaLLM(BaseLLM):
    """Ollama LLM implementation.

    This class implements the BaseLLM interface for Ollama's language models.
    It wraps the LangChain ChatOllama class to provide a consistent interface.
    """

    def __init__(
        self,
        model_name: str = "llama3",
        temperature: float = 0.7,
        base_url: str | None = None,
        **kwargs: Any,
    ):
        """Initialize the Ollama LLM.

        Args:
            model_name: The name of the Ollama model to use
            temperature: The temperature setting for the model
            base_url: The base URL for the Ollama API (if not provided, will be read from environment)
            **kwargs: Additional arguments to pass to the ChatOllama constructor
        """
        self._model_name = model_name
        self._temperature = temperature
        self._base_url = base_url or os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")

        self._llm = ChatOllama(
            model=model_name,
            base_url=self._base_url,
            temperature=temperature,
            **kwargs,
        )

    def _call(
        self,
        prompt: str,
        stop: list[str] | None = None,
        run_manager: CallbackManagerForLLMRun | None = None,
        **kwargs: Any,
    ) -> str:
        """Call the Ollama LLM with the given prompt.

        Args:
            prompt: The prompt to send to the LLM
            stop: Optional list of strings to stop generation
            run_manager: Optional callback manager for the run
            **kwargs: Additional arguments to pass to the LLM

        Returns:
            The generated text from the LLM
        """
        response = self._llm.invoke(prompt)
        if isinstance(response, str):
            return response
        return str(response.content)

    def _llm_type(self) -> str:
        """Return type of LLM.

        Returns:
            A string representing the type of LLM
        """
        return "ollama"

    @property
    def temperature(self) -> float:
        """Get the temperature setting for the LLM.

        Returns:
            The temperature value
        """
        return self._temperature

    @temperature.setter
    def temperature(self, value: float) -> None:
        """Set the temperature for the LLM.

        Args:
            value: The temperature value to set
        """
        self._temperature = value
        self._llm.temperature = value

    @property
    def model_name(self) -> str:
        """Get the model name for the LLM.

        Returns:
            The model name
        """
        return self._model_name

    @property
    def provider(self) -> str:
        """Get the provider name for the LLM.

        Returns:
            The provider name (Ollama)
        """
        return "ollama"
