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
    @abstractmethod
    def temperature(self) -> float:
        """Get the temperature setting for the LLM.

        Returns:
            The temperature value
        """
        pass

    @temperature.setter
    @abstractmethod
    def temperature(self, value: float) -> None:
        """Set the temperature for the LLM.

        Args:
            value: The temperature value to set
        """
        pass

    @property
    @abstractmethod
    def model_name(self) -> str:
        """Get the model name for the LLM.

        Returns:
            The model name
        """
        pass

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
        """
        if isinstance(prompt, str):
            return self._call(prompt, **kwargs)
        elif isinstance(prompt, list) and all(isinstance(msg, BaseMessage) for msg in prompt):
            # Convert messages to a single string
            text = "\n".join(msg.content for msg in prompt)
            return self._call(text, **kwargs)
        else:
            raise ValueError("Prompt must be a string or a list of BaseMessage objects")
