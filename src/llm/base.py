"""Base classes for LLM implementations."""

from abc import ABC, abstractmethod
from typing import Any

from langchain.callbacks.manager import CallbackManagerForLLMRun
from langchain.schema import BaseMessage, LLMResult


class BaseLLM(ABC):
    """Abstract base class for LLM implementations.

    This class defines the interface that all LLM implementations must follow.
    It extends the LangChain BaseLLM class to ensure compatibility with the
    LangChain ecosystem while providing a consistent interface for our application.
    """

    def __init__(
        self,
        model_name: str,
        temperature: float = 0.7,
        **kwargs: Any,
    ):
        """Initialize the base LLM.

        Args:
            model_name: The name of the model to use
            temperature: The temperature setting for the model
            **kwargs: Additional arguments to pass to the LLM constructor
        """
        self._model_name = model_name
        self._temperature = temperature

    @abstractmethod
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
            stop: Optional list of strings to stop generation
            run_manager: Optional callback manager for the run
            **kwargs: Additional arguments to pass to the LLM

        Returns:
            The generated text from the LLM
        """
        pass

    @abstractmethod
    def _llm_type(self) -> str:
        """Return type of LLM.

        Returns:
            A string representing the type of LLM
        """
        pass

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

    @property
    def model_name(self) -> str:
        """Get the model name for the LLM.

        Returns:
            The model name
        """
        return self._model_name

    @property
    @abstractmethod
    def provider(self) -> str:
        """Get the provider name for the LLM.

        Returns:
            The provider name
        """
        pass

    def invoke(self, prompt: str, **kwargs: Any) -> str:
        """Invoke the LLM with the given prompt.

        This is a convenience method that wraps the _call method.

        Args:
            prompt: The prompt to send to the LLM
            **kwargs: Additional arguments to pass to the LLM

        Returns:
            The generated text from the LLM
        """
        return self._call(prompt, **kwargs)

    def generate(self, prompts: list[str], **kwargs: Any) -> LLMResult:
        """Generate text for multiple prompts.

        Args:
            prompts: List of prompts to generate text for
            **kwargs: Additional arguments to pass to the LLM

        Returns:
            An LLMResult containing the generated text
        """
        generations = []
        for prompt in prompts:
            text = self._call(prompt, **kwargs)
            generations.append([{"text": text}])

        return LLMResult(generations=generations)

    def __call__(self, prompt: str | list[BaseMessage], **kwargs: Any) -> str:
        """Call the LLM with the given prompt.

        This method allows the LLM to be called like a function.

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
