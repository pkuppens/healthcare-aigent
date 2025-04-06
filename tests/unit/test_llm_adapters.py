"""Unit tests for LLM adapters."""

import os
from unittest.mock import MagicMock, patch

import pytest
from langchain.callbacks.manager import CallbackManagerForLLMRun

from src.llm.ollama_llm import OllamaLLM
from src.llm.openai_llm import OpenAILLM

# Test constants
TEST_TEMPERATURE_LOW = 0.5
TEST_TEMPERATURE_MEDIUM = 0.7
TEST_TEMPERATURE_HIGH = 0.9


class TestOpenAILLM:
    """Test cases for the OpenAI LLM adapter."""

    @patch("langchain_openai.ChatOpenAI")
    def test_initialization_with_api_key(self, mock_chat_openai):
        """Test initialization with API key."""
        mock_instance = MagicMock()
        mock_chat_openai.return_value = mock_instance

        llm = OpenAILLM(model_name="gpt-4", temperature=TEST_TEMPERATURE_LOW, api_key="test-key")

        mock_chat_openai.assert_called_once_with(model="gpt-4", temperature=TEST_TEMPERATURE_LOW, openai_api_key="test-key")
        assert llm.model_name == "gpt-4"
        assert llm.temperature == TEST_TEMPERATURE_LOW
        assert llm.provider == "openai"

    @patch.dict(os.environ, {"OPENAI_API_KEY": "env-key"})
    @patch("langchain_openai.ChatOpenAI")
    def test_initialization_with_env_api_key(self, mock_chat_openai):
        """Test initialization with API key from environment."""
        mock_instance = MagicMock()
        mock_chat_openai.return_value = mock_instance

        llm = OpenAILLM(model_name="gpt-3.5-turbo", temperature=TEST_TEMPERATURE_MEDIUM)

        mock_chat_openai.assert_called_once_with(
            model="gpt-3.5-turbo", temperature=TEST_TEMPERATURE_MEDIUM, openai_api_key="env-key"
        )
        assert llm.model_name == "gpt-3.5-turbo"
        assert llm.temperature == TEST_TEMPERATURE_MEDIUM
        assert llm.provider == "openai"

    def test_initialization_without_api_key(self):
        """Test initialization without API key."""
        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(ValueError, match="OpenAI API key not provided"):
                OpenAILLM()

    @patch("langchain_openai.ChatOpenAI")
    def test_call_method(self, mock_chat_openai):
        """Test the _call method."""
        mock_instance = MagicMock()
        mock_instance.invoke.return_value.content = "Test response"
        mock_chat_openai.return_value = mock_instance

        llm = OpenAILLM(model_name="gpt-3.5-turbo", api_key="test-key")
        result = llm._call("Test prompt")

        mock_instance.invoke.assert_called_once_with("Test prompt")
        assert result == "Test response"

    @patch("langchain_openai.ChatOpenAI")
    def test_call_method_with_stop_and_run_manager(self, mock_chat_openai):
        """Test the _call method with stop and run_manager."""
        mock_instance = MagicMock()
        mock_instance.invoke.return_value.content = "Test response"
        mock_chat_openai.return_value = mock_instance

        llm = OpenAILLM(model_name="gpt-3.5-turbo", api_key="test-key")
        stop = ["stop"]
        run_manager = CallbackManagerForLLMRun(run_id="test-run")
        result = llm._call("Test prompt", stop=stop, run_manager=run_manager)

        mock_instance.invoke.assert_called_once_with("Test prompt")
        assert result == "Test response"

    @patch("langchain_openai.ChatOpenAI")
    def test_temperature_setter(self, mock_chat_openai):
        """Test the temperature setter."""
        mock_instance = MagicMock()
        mock_chat_openai.return_value = mock_instance

        llm = OpenAILLM(model_name="gpt-3.5-turbo", api_key="test-key")
        llm.temperature = TEST_TEMPERATURE_HIGH

        assert llm.temperature == TEST_TEMPERATURE_HIGH
        mock_instance.temperature = TEST_TEMPERATURE_HIGH


class TestOllamaLLM:
    """Test cases for the Ollama LLM adapter."""

    @patch("langchain_community.chat_models.ChatOllama")
    def test_initialization_with_base_url(self, mock_chat_ollama):
        """Test initialization with base URL."""
        mock_instance = MagicMock()
        mock_chat_ollama.return_value = mock_instance

        llm = OllamaLLM(model_name="llama3", temperature=TEST_TEMPERATURE_LOW, base_url="http://custom:11434")

        mock_chat_ollama.assert_called_once_with(model="llama3", base_url="http://custom:11434", temperature=TEST_TEMPERATURE_LOW)
        assert llm.model_name == "llama3"
        assert llm.temperature == TEST_TEMPERATURE_LOW
        assert llm.provider == "ollama"

    @patch.dict(os.environ, {"OLLAMA_BASE_URL": "http://env:11434"})
    @patch("langchain_community.chat_models.ChatOllama")
    def test_initialization_with_env_base_url(self, mock_chat_ollama):
        """Test initialization with base URL from environment."""
        mock_instance = MagicMock()
        mock_chat_ollama.return_value = mock_instance

        llm = OllamaLLM(model_name="llama3:70b", temperature=TEST_TEMPERATURE_MEDIUM)

        mock_chat_ollama.assert_called_once_with(
            model="llama3:70b", base_url="http://env:11434", temperature=TEST_TEMPERATURE_MEDIUM
        )
        assert llm.model_name == "llama3:70b"
        assert llm.temperature == TEST_TEMPERATURE_MEDIUM
        assert llm.provider == "ollama"

    @patch("langchain_community.chat_models.ChatOllama")
    def test_call_method(self, mock_chat_ollama):
        """Test the _call method."""
        mock_instance = MagicMock()
        mock_instance.invoke.return_value.content = "Test response"
        mock_chat_ollama.return_value = mock_instance

        llm = OllamaLLM(model_name="llama3", base_url="http://localhost:11434")
        result = llm._call("Test prompt")

        mock_instance.invoke.assert_called_once_with("Test prompt")
        assert result == "Test response"

    @patch("langchain_community.chat_models.ChatOllama")
    def test_call_method_with_stop_and_run_manager(self, mock_chat_ollama):
        """Test the _call method with stop and run_manager."""
        mock_instance = MagicMock()
        mock_instance.invoke.return_value.content = "Test response"
        mock_chat_ollama.return_value = mock_instance

        llm = OllamaLLM(model_name="llama3", base_url="http://localhost:11434")
        stop = ["stop"]
        run_manager = CallbackManagerForLLMRun(run_id="test-run")
        result = llm._call("Test prompt", stop=stop, run_manager=run_manager)

        mock_instance.invoke.assert_called_once_with("Test prompt")
        assert result == "Test response"

    @patch("langchain_community.chat_models.ChatOllama")
    def test_temperature_setter(self, mock_chat_ollama):
        """Test the temperature setter."""
        mock_instance = MagicMock()
        mock_chat_ollama.return_value = mock_instance

        llm = OllamaLLM(model_name="llama3", base_url="http://localhost:11434")
        llm.temperature = TEST_TEMPERATURE_HIGH

        assert llm.temperature == TEST_TEMPERATURE_HIGH
        mock_instance.temperature = TEST_TEMPERATURE_HIGH
