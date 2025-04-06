"""OpenAI LLM implementation."""

import os
from typing import Any

from langchain.callbacks.manager import CallbackManagerForLLMRun
from langchain_openai import ChatOpenAI

from src.llm.base import BaseLLM


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
    ):
        """Initialize the OpenAI LLM.

        Args:
            model_name: The name of the OpenAI model to use
            temperature: The temperature setting for the model
            api_key: The OpenAI API key (if not provided, will be read from environment)
            **kwargs: Additional arguments to pass to the ChatOpenAI constructor
        """
        self._model_name = model_name
        self._temperature = temperature
        self._api_key = api_key or os.getenv("OPENAI_API_KEY")

        if not self._api_key:
            raise ValueError("OpenAI API key not provided and OPENAI_API_KEY environment variable not set")

        self._llm = ChatOpenAI(
            model=model_name,
            temperature=temperature,
            openai_api_key=self._api_key,
            **kwargs,
        )

    def _call(
        self,
        prompt: str,
        stop: list[str] | None = None,
        run_manager: CallbackManagerForLLMRun | None = None,
        **kwargs: Any,
    ) -> str:
        """Call the OpenAI LLM with the given prompt.

        Args:
            prompt: The prompt to send to the LLM
            stop: Optional list of strings to stop generation
            run_manager: Optional callback manager for the run
            **kwargs: Additional arguments to pass to the LLM

        Returns:
            The generated text from the LLM
        """
        return self._llm.invoke(prompt).content

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
            The provider name
        """
        return "openai"
