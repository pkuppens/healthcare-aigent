"""Integration tests for LLM connectivity.

This module contains tests that verify connectivity to different LLM providers
and ensure that the system can properly interact with these services using the LLMFactory.
"""

import os
from unittest.mock import patch

import pytest
import requests

from src.llm.circuit_breaker import is_ollama_available, is_openai_available
from src.llm.llm_factory import LLMFactory, LLMType


# Constants
HTTP_OK = 200
CUSTOM_TEMPERATURE = 0.5


@pytest.mark.integration
def test_ollama_connectivity():
    """Test connectivity to the Ollama server via the LLMFactory.

    Verifies that:
    1. The factory can create an Ollama LLM instance if the service is running.
    2. The created LLM has the correct model and default temperature.
    """
    if not is_ollama_available():
        pytest.skip("Ollama server not running or not available. Please start Ollama and try again.")

    llm = LLMFactory.create_llm(LLMType.LOCAL_FAST)
    assert llm is not None
    assert llm.model_name == "llama3"
    assert llm.temperature == 0.7  # Default for LOCAL_FAST


@pytest.mark.integration
def test_openai_connectivity():
    """Test connectivity to the OpenAI API via the LLMFactory.

    Verifies that:
    1. The factory can create an OpenAI LLM instance if the API key is set.
    2. The created LLM has the correct model and default temperature.
    """
    if not is_openai_available():
        pytest.skip("OPENAI_API_KEY not set or service is unavailable. Please set the environment variable and try again.")

    llm = LLMFactory.create_llm(LLMType.CLOUD_FAST)
    assert llm is not None
    assert llm.model_name == "gpt-3.5-turbo"
    assert llm.temperature == 0.7  # Default for CLOUD_FAST


@pytest.mark.integration
def test_custom_temperature_with_factory():
    """Test LLM creation with a custom temperature using the factory.

    Verifies that the factory correctly applies a custom temperature override
    to the created LLM instance.
    """
    if not is_openai_available():
        pytest.skip("OPENAI_API_KEY not set. Cannot run this test without it.")

    llm = LLMFactory.create_llm(LLMType.CLOUD_ACCURATE, temperature=CUSTOM_TEMPERATURE)
    assert llm is not None
    assert llm.temperature == CUSTOM_TEMPERATURE


@pytest.mark.integration
def test_factory_fallback_from_openai_to_ollama():
    """Test the factory's fallback mechanism from OpenAI to Ollama.

    Verifies that if OpenAI is unavailable, the factory's `get_llm_for_task`
    method correctly falls back to an available Ollama model.
    """
    if not is_ollama_available():
        pytest.skip("Ollama must be available to test the fallback mechanism.")

    with patch("src.llm.circuit_breaker.is_openai_available", return_value=False):
        llm = LLMFactory.get_llm_for_task("summarization")
        assert llm is not None
        assert "ollama" in llm.__class__.__module__.lower()


@pytest.mark.integration
def test_factory_fallback_from_ollama_to_openai():
    """Test the factory's fallback mechanism from Ollama to OpenAI.

    Verifies that if Ollama is unavailable, the factory's `get_llm_for_task`
    method correctly falls back to an available OpenAI model.
    """
    if not is_openai_available():
        pytest.skip("OpenAI must be available to test the fallback mechanism.")

    with patch("src.llm.circuit_breaker.is_ollama_available", return_value=False):
        # We need to select a type that defaults to local
        llm = LLMFactory.create_llm(LLMType.LOCAL_FAST)
        assert llm is not None
        assert "openai" in llm.__class__.__module__.lower()
