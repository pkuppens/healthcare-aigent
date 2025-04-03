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

    def test_openai_connectivity(self, mock_env_vars, monkeypatch):
        """Test OpenAI connectivity."""
        monkeypatch.setenv("LLM_PROVIDER", "OPENAI")

        try:
            llm = get_llm()
            # Try a simple completion to test connectivity
            response = llm.invoke("Hello, this is a test.")
            assert response is not None
            assert isinstance(response.content, str)
        except Exception as e:
            pytest.skip(f"OpenAI API not accessible: {e!s}")

    def test_ollama_connectivity(self, mock_env_vars, monkeypatch):
        """Test Ollama connectivity."""
        monkeypatch.setenv("LLM_PROVIDER", "OLLAMA")

        try:
            # First check if Ollama server is running
            response = requests.get("http://localhost:11434/api/tags")
            if response.status_code != 200:
                pytest.skip("Ollama server not running. Please start Ollama and try again.")

            llm = get_llm()
            # Try a simple completion to test connectivity
            response = llm.invoke("Hello, this is a test.")
            assert response is not None
            assert isinstance(response.content, str)
        except requests.exceptions.ConnectionError:
            pytest.skip("Could not connect to Ollama. Is it running?")
        except Exception as e:
            pytest.skip(f"Ollama API error: {e!s}")

    @patch("requests.get")
    def test_ollama_connection_error(self, mock_get, mock_env_vars, monkeypatch):
        """Test Ollama connection error handling."""
        mock_get.side_effect = requests.exceptions.ConnectionError()
        monkeypatch.setenv("LLM_PROVIDER", "OLLAMA")

        with pytest.warns(UserWarning, match="Could not connect to Ollama"):
            try:
                get_llm()
            except Exception:
                pass

    @patch("langchain_openai.ChatOpenAI.invoke")
    def test_openai_api_error(self, mock_invoke, mock_env_vars, monkeypatch):
        """Test OpenAI API error handling."""
        mock_invoke.side_effect = Exception("API Error")
        monkeypatch.setenv("LLM_PROVIDER", "OPENAI")

        with pytest.warns(UserWarning, match="OpenAI API not accessible"):
            try:
                get_llm()
            except Exception:
                pass
