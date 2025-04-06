"""Unit tests for LLM fallback mechanisms."""

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
    """Mock LLM for testing."""

    def __init__(self, provider="mock", model_name="mock-model", temperature=TEST_TEMPERATURE, should_fail=False):
        """Initialize the mock LLM."""
        self._provider = provider
        self._model_name = model_name
        self._temperature = temperature
        self.should_fail = should_fail

    def _call(self, prompt, stop=None, run_manager=None, **kwargs):
        """Mock call method."""
        if self.should_fail:
            raise Exception("Mock LLM failed")
        return f"Response to: {prompt}"

    def _llm_type(self):
        """Return the LLM type."""
        return "mock"

    @property
    def temperature(self):
        """Get the temperature."""
        return self._temperature

    @temperature.setter
    def temperature(self, value):
        """Set the temperature."""
        self._temperature = value

    @property
    def model_name(self):
        """Get the model name."""
        return self._model_name

    @property
    def provider(self):
        """Get the provider."""
        return self._provider


class TestFallbackStrategy:
    """Test cases for the FallbackStrategy class."""

    def test_get_fallback_llm_type_cloud_fast(self):
        """Test getting fallback LLM type for cloud fast."""
        fallback_type = FallbackStrategy.get_fallback_llm_type(LLMType.CLOUD_FAST)
        assert fallback_type == LLMType.LOCAL_FAST

    def test_get_fallback_llm_type_cloud_accurate(self):
        """Test getting fallback LLM type for cloud accurate."""
        fallback_type = FallbackStrategy.get_fallback_llm_type(LLMType.CLOUD_ACCURATE)
        assert fallback_type == LLMType.LOCAL_ACCURATE

    def test_get_fallback_llm_type_local_fast(self):
        """Test getting fallback LLM type for local fast."""
        fallback_type = FallbackStrategy.get_fallback_llm_type(LLMType.LOCAL_FAST)
        assert fallback_type == LLMType.CLOUD_FAST

    def test_get_fallback_llm_type_local_accurate(self):
        """Test getting fallback LLM type for local accurate."""
        fallback_type = FallbackStrategy.get_fallback_llm_type(LLMType.LOCAL_ACCURATE)
        assert fallback_type == LLMType.CLOUD_ACCURATE

    @patch("src.llm.fallback.config_manager")
    def test_get_fallback_provider_openai(self, mock_config_manager):
        """Test getting fallback provider for OpenAI."""
        mock_config = MagicMock()
        mock_config.fallback_provider = "ollama"
        mock_config_manager.get_config.return_value = mock_config

        fallback_provider = FallbackStrategy.get_fallback_provider("openai")
        assert fallback_provider == "ollama"

    def test_get_fallback_provider_ollama(self):
        """Test getting fallback provider for Ollama."""
        fallback_provider = FallbackStrategy.get_fallback_provider("ollama")
        assert fallback_provider == "openai"


class TestRetryStrategy:
    """Test cases for the RetryStrategy class."""

    def test_execute_with_retry_success(self):
        """Test executing an operation that succeeds after one retry."""
        retry_strategy = RetryStrategy(max_retries=TEST_MAX_RETRIES, initial_delay=TEST_INITIAL_DELAY)
        operation = MagicMock(side_effect=[Exception("Failed"), "success"])

        result = retry_strategy.execute_with_retry(operation)

        assert result == "success"
        assert operation.call_count == TEST_RETRY_ATTEMPTS  # Initial attempt + one retry

    def test_execute_with_retry_failure_then_success(self):
        """Test executing an operation that succeeds after one retry."""
        retry_strategy = RetryStrategy(max_retries=TEST_MAX_RETRIES, initial_delay=TEST_INITIAL_DELAY)
        operation = MagicMock(side_effect=[Exception("Failed"), "success"])

        result = retry_strategy.execute_with_retry(operation)

        assert result == "success"
        assert operation.call_count == TEST_RETRY_ATTEMPTS  # Initial attempt + one retry

    def test_execute_with_retry_all_failures(self):
        """Test executing an operation that always fails."""
        retry_strategy = RetryStrategy(max_retries=TEST_MAX_RETRIES, initial_delay=TEST_INITIAL_DELAY)
        operation = MagicMock(side_effect=Exception("Failed"))

        with pytest.raises(Exception, match="Failed"):
            retry_strategy.execute_with_retry(operation)

        assert operation.call_count == TEST_MAX_RETRIES + 1  # Initial attempt + max_retries


class TestFallbackLLM:
    """Test cases for the FallbackLLM class."""

    def test_fallback_llm_primary_success(self):
        """Test FallbackLLM when primary LLM succeeds."""
        primary_llm = MockLLM(provider="primary", model_name="primary-model")
        fallback_llm = MockLLM(provider="fallback", model_name="fallback-model")

        fallback_llm_wrapper = FallbackLLM(primary_llm, fallback_llm)
        result = fallback_llm_wrapper.invoke("test prompt")

        assert result == "Response from primary primary-model: test prompt"
        assert fallback_llm_wrapper.last_successful_llm == primary_llm

    def test_fallback_llm_primary_failure_fallback_success(self):
        """Test FallbackLLM when primary LLM fails but fallback succeeds."""
        primary_llm = MockLLM(provider="primary", model_name="primary-model", should_fail=True)
        fallback_llm = MockLLM(provider="fallback", model_name="fallback-model")

        fallback_llm_wrapper = FallbackLLM(primary_llm, fallback_llm)
        result = fallback_llm_wrapper.invoke("test prompt")

        assert result == "Response from fallback fallback-model: test prompt"
        assert fallback_llm_wrapper.last_successful_llm == fallback_llm

    def test_fallback_llm_both_failure(self):
        """Test FallbackLLM when both primary and fallback LLMs fail."""
        primary_llm = MockLLM(provider="primary", model_name="primary-model", should_fail=True)
        fallback_llm = MockLLM(provider="fallback", model_name="fallback-model", should_fail=True)

        fallback_llm_wrapper = FallbackLLM(primary_llm, fallback_llm)

        with pytest.raises(Exception, match="Mock LLM failed"):
            fallback_llm_wrapper.invoke("test prompt")

    def test_fallback_llm_no_fallback(self):
        """Test FallbackLLM when no fallback LLM is provided."""
        primary_llm = MockLLM(provider="primary", model_name="primary-model", should_fail=True)

        fallback_llm_wrapper = FallbackLLM(primary_llm)

        with pytest.raises(ValueError, match="No fallback LLM available"):
            fallback_llm_wrapper.invoke("test prompt")

    def test_fallback_llm_temperature(self):
        """Test FallbackLLM temperature property."""
        primary_llm = MockLLM(provider="primary", model_name="primary-model", temperature=TEST_TEMPERATURE)
        fallback_llm = MockLLM(provider="fallback", model_name="fallback-model", temperature=TEST_TEMPERATURE_LOW)

        fallback_llm_wrapper = FallbackLLM(primary_llm, fallback_llm)

        assert fallback_llm_wrapper.temperature == TEST_TEMPERATURE

        fallback_llm_wrapper.temperature = TEST_TEMPERATURE_HIGH
        assert primary_llm.temperature == TEST_TEMPERATURE_HIGH
        assert fallback_llm.temperature == TEST_TEMPERATURE_HIGH
