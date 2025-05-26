"""Unit tests for LLM fallback mechanisms.

This module contains tests for the fallback mechanisms that provide resilience
when LLM services fail. It includes tests for fallback strategies, retry strategies,
and the FallbackLLM wrapper that implements these strategies.
"""

from unittest.mock import MagicMock, patch

import pytest

from src.llm.base import BaseLLM
from src.llm.fallback import FallbackLLM, FallbackStrategy, RetryStrategy
from src.llm.llm_factory import LLMType


# Test constants
TEST_MAX_RETRIES = 2
TEST_INITIAL_DELAY = 0.1
TEST_TEMPERATURE = 0.7
TEST_TEMPERATURE_LOW = 0.5
TEST_TEMPERATURE_HIGH = 0.9
TEST_RETRY_ATTEMPTS = 2  # Number of attempts (initial + one retry)


class MockLLM(BaseLLM):
    """Mock LLM for testing fallback mechanisms.

    This mock implementation allows testing of fallback behavior by simulating
    LLM failures and successes in a controlled manner.
    """

    def __init__(self, provider="mock", model_name="mock-model", temperature=TEST_TEMPERATURE, should_fail=False):
        """Initialize the mock LLM.

        Args:
            provider: The provider name for the mock LLM
            model_name: The model name for the mock LLM
            temperature: The temperature setting for the mock LLM
            should_fail: Whether the mock LLM should fail when called
        """
        self._provider = provider
        self._model_name = model_name
        self._temperature = temperature
        self.should_fail = should_fail

    def _call(self, prompt, stop=None, run_manager=None, **kwargs):
        """Mock call method that simulates LLM behavior.

        Args:
            prompt: The input prompt
            stop: Optional stop sequences
            run_manager: Optional run manager for callbacks
            **kwargs: Additional keyword arguments

        Returns:
            A response string or raises an exception if should_fail is True
        """
        if self.should_fail:
            raise Exception("Mock LLM failed")
        return f"Response from {self._provider} {self._model_name}: {prompt}"

    def _llm_type(self):
        """Return the LLM type.

        Returns:
            The string "mock" as the LLM type
        """
        return "mock"

    @property
    def temperature(self):
        """Get the temperature setting.

        Returns:
            The current temperature value
        """
        return self._temperature

    @temperature.setter
    def temperature(self, value):
        """Set the temperature value.

        Args:
            value: The new temperature value
        """
        self._temperature = value

    @property
    def model_name(self):
        """Get the model name.

        Returns:
            The current model name
        """
        return self._model_name

    @property
    def provider(self):
        """Get the provider name.

        Returns:
            The current provider name
        """
        return self._provider


class TestFallbackStrategy:
    """Test cases for the FallbackStrategy class.

    These tests verify that the FallbackStrategy correctly determines
    appropriate fallback options for different LLM types and providers.
    """

    def test_get_fallback_llm_type_cloud_fast(self):
        """Test getting fallback LLM type for cloud fast LLM.

        Verifies that:
        1. When a cloud fast LLM fails, the strategy recommends a local fast LLM
        2. The fallback maintains the same speed/accuracy profile
        """
        fallback_type = FallbackStrategy.get_fallback_llm_type(LLMType.CLOUD_FAST)
        assert fallback_type == LLMType.LOCAL_FAST

    def test_get_fallback_llm_type_cloud_accurate(self):
        """Test getting fallback LLM type for cloud accurate LLM.

        Verifies that:
        1. When a cloud accurate LLM fails, the strategy recommends a local accurate LLM
        2. The fallback maintains the same speed/accuracy profile
        """
        fallback_type = FallbackStrategy.get_fallback_llm_type(LLMType.CLOUD_ACCURATE)
        assert fallback_type == LLMType.LOCAL_ACCURATE

    def test_get_fallback_llm_type_local_fast(self):
        """Test getting fallback LLM type for local fast LLM.

        Verifies that:
        1. When a local fast LLM fails, the strategy recommends a cloud fast LLM
        2. The fallback maintains the same speed/accuracy profile
        """
        fallback_type = FallbackStrategy.get_fallback_llm_type(LLMType.LOCAL_FAST)
        assert fallback_type == LLMType.CLOUD_FAST

    def test_get_fallback_llm_type_local_accurate(self):
        """Test getting fallback LLM type for local accurate LLM.

        Verifies that:
        1. When a local accurate LLM fails, the strategy recommends a cloud accurate LLM
        2. The fallback maintains the same speed/accuracy profile
        """
        fallback_type = FallbackStrategy.get_fallback_llm_type(LLMType.LOCAL_ACCURATE)
        assert fallback_type == LLMType.CLOUD_ACCURATE

    @patch("src.llm.fallback.config_manager")
    def test_get_fallback_provider_openai(self, mock_config_manager):
        """Test getting fallback provider for OpenAI.

        Verifies that:
        1. The strategy correctly retrieves the fallback provider from configuration
        2. The fallback provider is correctly set to "ollama" for OpenAI
        """
        mock_config = MagicMock()
        mock_config.fallback_provider = "ollama"
        mock_config_manager.get_config.return_value = mock_config

        fallback_provider = FallbackStrategy.get_fallback_provider("openai")
        assert fallback_provider == "ollama"

    def test_get_fallback_provider_ollama(self):
        """Test getting fallback provider for Ollama.

        Verifies that:
        1. The strategy correctly returns "openai" as the fallback for Ollama
        2. This provides a complete fallback cycle between providers
        """
        fallback_provider = FallbackStrategy.get_fallback_provider("ollama")
        assert fallback_provider == "openai"


class TestRetryStrategy:
    """Test cases for the RetryStrategy class.

    These tests verify that the RetryStrategy correctly implements
    retry logic with exponential backoff for failed operations.
    """

    def test_execute_with_retry_success(self):
        """Test executing an operation that succeeds after one retry.

        Verifies that:
        1. The operation is retried when it fails initially
        2. The operation succeeds on the second attempt
        3. The correct number of attempts are made
        """
        retry_strategy = RetryStrategy(max_retries=TEST_MAX_RETRIES, initial_delay=TEST_INITIAL_DELAY)
        operation = MagicMock(side_effect=[Exception("Failed"), "success"])

        result = retry_strategy.execute_with_retry(operation)

        assert result == "success"
        assert operation.call_count == TEST_RETRY_ATTEMPTS  # Initial attempt + one retry

    def test_execute_with_retry_failure_then_success(self):
        """Test executing an operation that succeeds after one retry.

        Verifies that:
        1. The operation is retried when it fails initially
        2. The operation succeeds on the second attempt
        3. The correct number of attempts are made
        """
        retry_strategy = RetryStrategy(max_retries=TEST_MAX_RETRIES, initial_delay=TEST_INITIAL_DELAY)
        operation = MagicMock(side_effect=[Exception("Failed"), "success"])

        result = retry_strategy.execute_with_retry(operation)

        assert result == "success"
        assert operation.call_count == TEST_RETRY_ATTEMPTS  # Initial attempt + one retry

    def test_execute_with_retry_all_failures(self):
        """Test executing an operation that always fails.

        Verifies that:
        1. The operation is retried the maximum number of times
        2. The final exception is propagated to the caller
        3. The correct number of attempts are made before giving up
        """
        retry_strategy = RetryStrategy(max_retries=TEST_MAX_RETRIES, initial_delay=TEST_INITIAL_DELAY)
        operation = MagicMock(side_effect=Exception("Failed"))

        with pytest.raises(Exception, match="Failed"):
            retry_strategy.execute_with_retry(operation)

        assert operation.call_count == TEST_MAX_RETRIES + 1  # Initial attempt + max_retries


class TestFallbackLLM:
    """Test cases for the FallbackLLM class.

    These tests verify that the FallbackLLM wrapper correctly implements
    fallback behavior when the primary LLM fails.
    """

    def test_fallback_llm_primary_success(self):
        """Test FallbackLLM when primary LLM succeeds.

        Verifies that:
        1. The primary LLM is used when it succeeds
        2. The fallback LLM is not used
        3. The last_successful_llm is set to the primary LLM
        """
        primary_llm = MockLLM(provider="primary", model_name="primary-model")
        fallback_llm = MockLLM(provider="fallback", model_name="fallback-model")

        fallback_llm_wrapper = FallbackLLM(primary_llm, fallback_llm)
        result = fallback_llm_wrapper.invoke("test prompt")

        assert result == "Response from primary primary-model: test prompt"
        assert fallback_llm_wrapper.last_successful_llm == primary_llm

    def test_fallback_llm_primary_failure_fallback_success(self):
        """Test FallbackLLM when primary LLM fails but fallback succeeds.

        Verifies that:
        1. The primary LLM is tried first and fails
        2. The fallback LLM is used when the primary fails
        3. The last_successful_llm is set to the fallback LLM
        """
        primary_llm = MockLLM(provider="primary", model_name="primary-model", should_fail=True)
        fallback_llm = MockLLM(provider="fallback", model_name="fallback-model")

        fallback_llm_wrapper = FallbackLLM(primary_llm, fallback_llm)
        result = fallback_llm_wrapper.invoke("test prompt")

        assert result == "Response from fallback fallback-model: test prompt"
        assert fallback_llm_wrapper.last_successful_llm == fallback_llm

    def test_fallback_llm_both_failure(self):
        """Test FallbackLLM when both primary and fallback LLMs fail.

        Verifies that:
        1. The primary LLM is tried first and fails
        2. The fallback LLM is tried and also fails
        3. The exception from the fallback LLM is propagated
        """
        primary_llm = MockLLM(provider="primary", model_name="primary-model", should_fail=True)
        fallback_llm = MockLLM(provider="fallback", model_name="fallback-model", should_fail=True)

        fallback_llm_wrapper = FallbackLLM(primary_llm, fallback_llm)

        with pytest.raises(Exception, match="Mock LLM failed"):
            fallback_llm_wrapper.invoke("test prompt")

    def test_fallback_llm_no_fallback(self):
        """Test FallbackLLM when no fallback LLM is provided.

        Verifies that:
        1. When the primary LLM fails and no fallback is provided
        2. A ValueError is raised with an appropriate message
        """
        primary_llm = MockLLM(provider="primary", model_name="primary-model", should_fail=True)

        fallback_llm_wrapper = FallbackLLM(primary_llm)

        with pytest.raises(ValueError, match="No fallback LLM available"):
            fallback_llm_wrapper.invoke("test prompt")

    def test_fallback_llm_temperature(self):
        """Test FallbackLLM temperature property.

        Verifies that:
        1. The temperature property returns the primary LLM's temperature
        2. Setting the temperature updates both primary and fallback LLMs
        3. The temperature is correctly propagated to both LLMs
        """
        primary_llm = MockLLM(provider="primary", model_name="primary-model", temperature=TEST_TEMPERATURE)
        fallback_llm = MockLLM(provider="fallback", model_name="fallback-model", temperature=TEST_TEMPERATURE_LOW)

        fallback_llm_wrapper = FallbackLLM(primary_llm, fallback_llm)

        assert fallback_llm_wrapper.temperature == TEST_TEMPERATURE

        fallback_llm_wrapper.temperature = TEST_TEMPERATURE_HIGH
        assert primary_llm.temperature == TEST_TEMPERATURE_HIGH
        assert fallback_llm.temperature == TEST_TEMPERATURE_HIGH
