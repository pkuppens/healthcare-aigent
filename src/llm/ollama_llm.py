"""Ollama LLM implementation."""

import os
from typing import Any

import requests
from langchain_core.callbacks import CallbackManagerForLLMRun
from langchain_ollama import ChatOllama

from src.llm.base import BaseLLM, strip_reasoning, usage_from_response
from src.llm.circuit_breaker import HTTP_OK
from src.llm.ollama_residency import ResidencyMonitor, ollama_session


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


def is_model_available(model: str, base_url: str | None = None) -> bool:
    """Check whether `model` has been pulled into the Ollama server at `base_url`.

    A tag without an explicit version (e.g. "llama3") matches its ":latest" tag, as in Ollama itself.
    Returns False when Ollama is unreachable.
    """
    base_url = base_url or os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    try:
        response = ollama_session.get(f"{base_url}/api/tags", timeout=2)
        if response.status_code != HTTP_OK:
            return False
        names = {m.get("name") for m in response.json().get("models", [])}
    except (requests.RequestException, TimeoutError, ValueError):
        return False
    wanted = model if ":" in model else f"{model}:latest"
    return wanted in names


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
        residency_monitor: ResidencyMonitor | None = None,
        require_gpu: bool = False,
        **kwargs: Any,
    ):
        """Initialize the Ollama LLM.

        Args:
            model_name: The name of the Ollama model to use
            temperature: The temperature setting for the model
            base_url: The base URL for the Ollama API (if not provided, will be read from environment)
            residency_monitor: When given, each call reports early cache evictions and checks
                GPU residency afterwards (see src/llm/ollama_residency.py, issue #26)
            require_gpu: With a residency_monitor: raise GPUResidencyError instead of warning when
                the model is not fully on the GPU
            **kwargs: Additional arguments to pass to the ChatOllama constructor
        """
        self._model_name = model_name
        self._temperature = temperature
        self._base_url = base_url or os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        self._residency_monitor = residency_monitor
        self._require_gpu = require_gpu

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
        if self._residency_monitor:
            self._residency_monitor.before_call()
        response = self._llm.invoke(prompt)
        if self._residency_monitor:
            self._residency_monitor.after_call(self._model_name, self._require_gpu)
        if isinstance(response, str):
            return strip_reasoning(response)
        self.last_usage = usage_from_response(response)
        return strip_reasoning(str(response.content))

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
