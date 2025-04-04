"""Integration tests for LLM connectivity."""

import os
from unittest.mock import AsyncMock, patch

import pytest
import requests

from src.llm_config import get_llm

# Constants
HTTP_OK = 200
CUSTOM_TEMPERATURE = 0.5


@pytest.fixture
def mock_llm():
    """Create a mock LLM for testing."""
    return AsyncMock()


@pytest.mark.integration
def test_ollama_connectivity():
    """Test connectivity to Ollama server."""
    try:
        # First check if Ollama server is running
        response = requests.get("http://localhost:11434/api/tags")
        if response.status_code != HTTP_OK:
            pytest.skip("Ollama server not running. Please start Ollama and try again.")

        # Test LLM creation
        llm = get_llm(provider="OLLAMA")
        assert llm is not None
        assert llm.model == "llama3"
        assert llm.base_url == "http://localhost:11434"
    except requests.exceptions.ConnectionError:
        pytest.skip("Ollama server not running. Please start Ollama and try again.")


@pytest.mark.integration
def test_openai_connectivity():
    """Test connectivity to OpenAI API."""
    # Skip if no API key
    if not os.getenv("OPENAI_API_KEY"):
        pytest.skip("OPENAI_API_KEY not set. Please set the environment variable and try again.")

    # Test LLM creation
    llm = get_llm(provider="OPENAI")
    assert llm is not None
    assert llm.model == "gpt-3.5-turbo"


@pytest.mark.integration
def test_custom_temperature():
    """Test LLM creation with custom temperature."""
    llm = get_llm(temperature=CUSTOM_TEMPERATURE)
    assert llm is not None
    assert llm.temperature == CUSTOM_TEMPERATURE


@pytest.mark.integration
def test_ollama_connection_error(mock_env_vars, monkeypatch):
    """Test Ollama connection error handling."""
    monkeypatch.setenv("LLM_PROVIDER", "OLLAMA")
    with patch("requests.get") as mock_get:
        mock_get.side_effect = requests.exceptions.ConnectionError()
        with pytest.warns(UserWarning, match="Could not connect to Ollama"):
            try:
                get_llm()
            except Exception:
                pass


@pytest.mark.integration
def test_openai_api_error(mock_env_vars, monkeypatch):
    """Test OpenAI API error handling."""
    monkeypatch.setenv("LLM_PROVIDER", "OPENAI")
    with patch("langchain_openai.ChatOpenAI.invoke") as mock_invoke:
        mock_invoke.side_effect = Exception("API Error")
        with pytest.warns(UserWarning, match="OpenAI API not accessible"):
            try:
                get_llm()
            except Exception:
                pass
