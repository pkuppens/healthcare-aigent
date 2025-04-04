"""Unit tests for LLM configuration."""

import os
from unittest.mock import patch

import pytest
from langchain_community.chat_models import ChatOllama
from langchain_openai import ChatOpenAI

from src.llm_config import get_llm

# Constants
DEFAULT_TEMPERATURE = 0.7
CUSTOM_TEMPERATURE = 0.5

@pytest.fixture
def mock_env_vars():
    """Mock environment variables for testing."""
    with patch.dict(
        os.environ,
        {
            "OPENAI_API_KEY": "test-key",
            "OPENAI_MODEL_NAME": "gpt-3.5-turbo",
            "OLLAMA_BASE_URL": "http://localhost:11434",
            "OLLAMA_MODEL_NAME": "llama3",
        },
    ):
        yield

def test_get_llm_openai(mock_env_vars):
    """Test getting OpenAI LLM."""
    llm = get_llm(provider="OPENAI")
    assert isinstance(llm, ChatOpenAI)
    assert llm.model_name == "gpt-3.5-turbo"
    assert llm.temperature == DEFAULT_TEMPERATURE
    assert llm.api_key == "test-key"

def test_get_llm_ollama(mock_env_vars):
    """Test getting Ollama LLM."""
    llm = get_llm(provider="OLLAMA")
    assert isinstance(llm, ChatOllama)
    assert llm.model == "llama3"
    assert llm.base_url == "http://localhost:11434"
    assert llm.temperature == DEFAULT_TEMPERATURE

def test_get_llm_default(mock_env_vars):
    """Test getting default LLM."""
    llm = get_llm()
    assert isinstance(llm, ChatOpenAI)
    assert llm.model_name == "gpt-3.5-turbo"
    assert llm.temperature == DEFAULT_TEMPERATURE
    assert llm.api_key == "test-key"

def test_get_llm_custom_temperature(mock_env_vars):
    """Test getting LLM with custom temperature."""
    llm = get_llm(temperature=CUSTOM_TEMPERATURE)
    assert isinstance(llm, ChatOpenAI)
    assert llm.temperature == CUSTOM_TEMPERATURE

def test_get_llm_invalid_provider(mock_env_vars):
    """Test getting LLM with invalid provider."""
    with pytest.raises(ValueError, match="Unsupported LLM provider: INVALID"):
        get_llm(provider="INVALID")

@pytest.mark.unit
class TestLLMConfig:
    """Test LLM configuration and initialization."""

    @patch.dict(os.environ, {"LLM_PROVIDER": "OPENAI", "OPENAI_API_KEY": "test-key", "OPENAI_MODEL_NAME": "gpt-3.5-turbo"})
    def test_get_openai_llm(self):
        """Test getting OpenAI LLM with valid configuration."""
        llm = get_llm()
        assert isinstance(llm, ChatOpenAI)
        assert llm.model_name == "gpt-3.5-turbo"
        assert llm.temperature == DEFAULT_TEMPERATURE
        assert llm.api_key == "test-key"

    @patch.dict(os.environ, {"LLM_PROVIDER": "OPENAI", "OPENAI_MODEL_NAME": "gpt-3.5-turbo"})
    def test_get_openai_llm_missing_api_key(self):
        """Test getting OpenAI LLM with missing API key."""
        with pytest.raises(ValueError, match="OPENAI_API_KEY environment variable not set"):
            get_llm()

    @patch.dict(os.environ, {"LLM_PROVIDER": "OLLAMA", "OLLAMA_BASE_URL": "http://localhost:11434", "OLLAMA_MODEL_NAME": "llama3"})
    def test_get_ollama_llm(self):
        """Test getting Ollama LLM with valid configuration."""
        llm = get_llm()
        assert isinstance(llm, ChatOllama)
        assert llm.model == "llama3"
        assert llm.base_url == "http://localhost:11434"
        assert llm.temperature == DEFAULT_TEMPERATURE

    @patch.dict(os.environ, {"LLM_PROVIDER": "OLLAMA"})
    def test_get_ollama_llm_default_values(self):
        """Test getting Ollama LLM with default values."""
        llm = get_llm()
        assert isinstance(llm, ChatOllama)
        assert llm.model == "llama3"
        assert llm.base_url == "http://localhost:11434"
        assert llm.temperature == DEFAULT_TEMPERATURE

    @patch.dict(os.environ, {"LLM_PROVIDER": "INVALID"})
    def test_get_llm_invalid_provider(self):
        """Test getting LLM with invalid provider."""
        with pytest.raises(ValueError, match="Unsupported LLM provider: INVALID"):
            get_llm()

    @patch.dict(os.environ, {"LLM_PROVIDER": "OPENAI", "OPENAI_API_KEY": "test-key", "OPENAI_MODEL_NAME": "gpt-3.5-turbo"})
    def test_get_llm_custom_temperature(self):
        """Test getting LLM with custom temperature."""
        llm = get_llm(temperature=CUSTOM_TEMPERATURE)
        assert llm.temperature == CUSTOM_TEMPERATURE
