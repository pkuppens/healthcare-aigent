"""Fallback mechanisms for LLM providers."""

import logging
import time
from collections.abc import Callable
from typing import Any

from src.llm.base import BaseLLM
from src.llm.config import config_manager
from src.llm.llm_factory import LLMType


# Configure logging
logger = logging.getLogger(__name__)


class FallbackStrategy:
    """Strategy for handling LLM fallbacks."""

    @staticmethod
    def get_fallback_llm_type(llm_type: LLMType) -> LLMType:
        """Get the fallback LLM type for a given LLM type.

        Args:
            llm_type: The original LLM type

        Returns:
            The fallback LLM type
        """
        if llm_type == LLMType.CLOUD_FAST:
            return LLMType.LOCAL_FAST
        elif llm_type == LLMType.CLOUD_ACCURATE:
            return LLMType.LOCAL_ACCURATE
        elif llm_type == LLMType.LOCAL_FAST:
            return LLMType.CLOUD_FAST
        elif llm_type == LLMType.LOCAL_ACCURATE:
            return LLMType.CLOUD_ACCURATE
        else:
            return LLMType.CLOUD_FAST  # Default fallback

    @staticmethod
    def get_fallback_provider(provider: str) -> str:
        """Get the fallback provider for a given provider.

        Args:
            provider: The original provider

        Returns:
            The fallback provider
        """
        config = config_manager.get_config()

        if provider.lower() == "openai":
            return config.fallback_provider
        elif provider.lower() == "ollama":
            return "openai"  # Default fallback for Ollama
        else:
            return "openai"  # Default fallback


class RetryStrategy:
    """Strategy for retrying LLM operations."""

    def __init__(
        self,
        max_retries: int = 3,
        initial_delay: float = 1.0,
        max_delay: float = 10.0,
        backoff_factor: float = 2.0,
    ):
        """Initialize the retry strategy.

        Args:
            max_retries: Maximum number of retries
            initial_delay: Initial delay between retries in seconds
            max_delay: Maximum delay between retries in seconds
            backoff_factor: Factor to increase delay by after each retry
        """
        self.max_retries = max_retries
        self.initial_delay = initial_delay
        self.max_delay = max_delay
        self.backoff_factor = backoff_factor

    def execute_with_retry(self, operation: Callable, *args: Any, **kwargs: Any) -> Any:
        """Execute an operation with retry logic.

        Args:
            operation: The operation to execute
            *args: Positional arguments to pass to the operation
            **kwargs: Keyword arguments to pass to the operation

        Returns:
            The result of the operation

        Raises:
            Exception: If all retries fail
        """
        last_exception = None
        delay = self.initial_delay

        for attempt in range(self.max_retries + 1):
            try:
                return operation(*args, **kwargs)
            except Exception as e:
                last_exception = e
                if attempt < self.max_retries:
                    logger.warning(
                        f"Operation failed (attempt {attempt + 1}/{self.max_retries}): {e}. Retrying in {delay:.2f} seconds..."
                    )
                    time.sleep(delay)
                    delay = min(delay * self.backoff_factor, self.max_delay)
                else:
                    logger.error(f"Operation failed after {self.max_retries} retries: {e}")
                    raise last_exception from e


class FallbackLLM(BaseLLM):
    """LLM implementation with fallback capabilities.

    This class wraps another LLM and provides fallback mechanisms
    when the primary LLM fails.
    """

    def __init__(
        self,
        primary_llm: BaseLLM,
        fallback_llm: BaseLLM | None = None,
        retry_strategy: RetryStrategy | None = None,
    ):
        """Initialize the fallback LLM.

        Args:
            primary_llm: The primary LLM to use
            fallback_llm: The fallback LLM to use if the primary fails
            retry_strategy: The retry strategy to use
        """
        self._primary_llm = primary_llm
        self._fallback_llm = fallback_llm
        self._retry_strategy = retry_strategy or RetryStrategy()
        self._last_successful_llm = primary_llm

    def _call(
        self,
        prompt: str,
        stop: list[str] | None = None,
        run_manager: Any | None = None,
        **kwargs: Any,
    ) -> str:
        """Call the LLM with the given prompt, with fallback if needed.

        Args:
            prompt: The prompt to send to the LLM
            stop: Optional list of strings to stop generation
            run_manager: Optional callback manager for the run
            **kwargs: Additional arguments to pass to the LLM

        Returns:
            The generated text from the LLM
        """

        def try_primary_llm() -> str:
            return self._primary_llm._call(prompt, stop, run_manager, **kwargs)

        def try_fallback_llm() -> str:
            if self._fallback_llm:
                return self._fallback_llm._call(prompt, stop, run_manager, **kwargs)
            raise ValueError("No fallback LLM available")

        try:
            # Try the primary LLM first
            result = self._retry_strategy.execute_with_retry(try_primary_llm)
            self._last_successful_llm = self._primary_llm
            return result
        except Exception as e:
            logger.warning(f"Primary LLM failed: {e}. Trying fallback...")

            # If primary fails, try the fallback
            try:
                result = self._retry_strategy.execute_with_retry(try_fallback_llm)
                self._last_successful_llm = self._fallback_llm
                return result
            except Exception as e:
                logger.error(f"Fallback LLM also failed: {e}")
                raise

    def _llm_type(self) -> str:
        """Return type of LLM.

        Returns:
            A string representing the type of LLM
        """
        return f"fallback({self._primary_llm._llm_type()})"

    @property
    def temperature(self) -> float:
        """Get the temperature setting for the LLM.

        Returns:
            The temperature value
        """
        return self._primary_llm.temperature

    @temperature.setter
    def temperature(self, value: float) -> None:
        """Set the temperature for the LLM.

        Args:
            value: The temperature value to set
        """
        self._primary_llm.temperature = value
        if self._fallback_llm:
            self._fallback_llm.temperature = value

    @property
    def model_name(self) -> str:
        """Get the model name for the LLM.

        Returns:
            The model name
        """
        return self._primary_llm.model_name

    @property
    def provider(self) -> str:
        """Get the provider name for the LLM.

        Returns:
            The provider name
        """
        return self._primary_llm.provider

    @property
    def last_successful_llm(self) -> BaseLLM:
        """Get the last successful LLM.

        Returns:
            The last successful LLM
        """
        return self._last_successful_llm
