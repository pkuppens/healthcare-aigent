"""OpenAI LLM implementation."""

import os
from typing import Any

import requests
from langchain.callbacks.manager import CallbackManagerForLLMRun
from langchain.schema import BaseMessage
from langchain_openai import ChatOpenAI
from pydantic import SecretStr

from src.llm.base import BaseLLM
from src.llm.circuit_breaker import HTTP_OK


def check_openai_availability() -> bool:
    """Check if OpenAI API is available.

    Returns:
        True if OpenAI is available, False otherwise
    """
    api_key = os.getenv("OPENAI_API_KEY", "")
    if not api_key:
        return False

    try:
        # Simple check to see if the API key is valid
        response = requests.get("https://api.openai.com/v1/models", headers={"Authorization": f"Bearer {api_key}"}, timeout=2)
        return response.status_code == HTTP_OK
    except (requests.RequestException, TimeoutError):
        return False


class OpenAILLM(BaseLLM):
    """OpenAI LLM implementation.

    This class implements the BaseLLM interface for OpenAI's language models.
    It wraps the LangChain ChatOpenAI class to provide a consistent interface.
    """

    def __init__(
        self,
        model_name: str = "gpt-3.5-turbo",
        temperature: float = 0.7,
        api_key: str | None = None,
        **kwargs: Any,
    ) -> None:
        """Initialize the OpenAI LLM.

        Args:
            model_name: The name of the model to use
            temperature: The temperature to use for generation
            api_key: The OpenAI API key. If not provided, will be read from environment
            **kwargs: Additional arguments to pass to the ChatOpenAI constructor
        """
        super().__init__(model_name=model_name, temperature=temperature)
        self._model_name = model_name
        self._temperature = temperature
        self._api_key = api_key or os.getenv("OPENAI_API_KEY")

        if not self._api_key:
            raise ValueError("OpenAI API key not provided and OPENAI_API_KEY environment variable not set")

        self._llm = ChatOpenAI(
            model=model_name,
            temperature=temperature,
            api_key=SecretStr(self._api_key),
            **kwargs,
        )

    def _call(
        self,
        prompt: str,
        stop: list[str] | None = None,
        run_manager: CallbackManagerForLLMRun | None = None,
        **kwargs: Any,
    ) -> str:
        """Call the LLM with the given prompt.

        Args:
            prompt: The prompt to send to the LLM
            stop: Optional list of stop sequences
            run_manager: Optional callback manager
            **kwargs: Additional arguments to pass to the LLM

        Returns:
            The generated text from the LLM
        """
        response = self._llm.invoke(prompt)
        if isinstance(response, str):
            return response
        return str(response.content)

    def __call__(self, prompt: str | list[BaseMessage], **kwargs: Any) -> str:
        """Call the LLM with the given prompt.

        Args:
            prompt: The prompt to send to the LLM
            **kwargs: Additional arguments to pass to the LLM

        Returns:
            The generated text from the LLM

        Raises:
            ValueError: If the prompt is not a string or list of BaseMessage objects
        """
        if isinstance(prompt, str):
            return self._call(prompt, **kwargs)
        elif isinstance(prompt, list) and all(isinstance(msg, BaseMessage) for msg in prompt):
            # Convert messages to a single string, ensuring each message's content is a string
            text = "\n".join(str(msg.content) for msg in prompt)
            return self._call(text, **kwargs)
        else:
            raise ValueError("Prompt must be a string or a list of BaseMessage objects")

    def _llm_type(self) -> str:
        """Return type of LLM.

        Returns:
            A string representing the type of LLM
        """
        return "openai"

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
            The provider name (OpenAI)
        """
        return "openai"
