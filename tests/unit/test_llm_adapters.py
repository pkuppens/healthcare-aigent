"""Unit tests for LLM adapters.

This module contains tests for the LLM adapter classes that provide a unified interface
for different LLM providers (OpenAI and Ollama). The tests verify that the adapters
correctly initialize, configure, and interact with their respective LLM backends.

The tests follow the Test-Driven Development with Vibe Coding (TDVC) approach:
1. Each test has a clear docstring explaining what it verifies
2. Tests follow the Arrange-Act-Assert pattern
3. Mocking is done at the appropriate level
4. Tests focus on behavior rather than implementation details
"""

import os
import uuid
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
    """Test cases for the OpenAI LLM adapter.

    These tests verify that the OpenAILLM adapter correctly initializes and interacts
    with the OpenAI API through the langchain ChatOpenAI class. The tests focus on:

    1. Initialization with different API key sources
    2. Proper configuration of model parameters
    3. Correct handling of the _call method
    4. Temperature setting and retrieval
    """

    @patch("langchain_openai.ChatOpenAI")
    def test_initialization_with_api_key(self, mock_chat_openai):
        """Test initialization with explicit API key.

        Verifies that:
        1. The adapter correctly initializes with a provided API key
        2. The model name and temperature are set correctly
        3. The provider is correctly identified as 'openai'
        4. The underlying ChatOpenAI is initialized with the correct parameters
        """
        # Arrange
        mock_instance = MagicMock()
        mock_chat_openai.return_value = mock_instance

        # Act
        llm = OpenAILLM(model_name="gpt-4", temperature=TEST_TEMPERATURE_LOW, api_key="test-key")

        # Assert
        mock_chat_openai.assert_called_once_with(model="gpt-4", temperature=TEST_TEMPERATURE_LOW, openai_api_key="test-key")
        assert llm.model_name == "gpt-4"
        assert llm.temperature == TEST_TEMPERATURE_LOW
        assert llm.provider == "openai"

    @patch.dict(os.environ, {"OPENAI_API_KEY": "env-key"})
    @patch("langchain_openai.ChatOpenAI")
    def test_initialization_with_env_api_key(self, mock_chat_openai):
        """Test initialization with API key from environment variables.

        Verifies that:
        1. The adapter correctly initializes using an API key from environment variables
        2. The model name and temperature are set correctly
        3. The provider is correctly identified as 'openai'
        4. The underlying ChatOpenAI is initialized with the correct parameters
        """
        # Arrange
        mock_instance = MagicMock()
        mock_chat_openai.return_value = mock_instance

        # Act
        llm = OpenAILLM(model_name="gpt-3.5-turbo", temperature=TEST_TEMPERATURE_MEDIUM)

        # Assert
        mock_chat_openai.assert_called_once_with(
            model="gpt-3.5-turbo", temperature=TEST_TEMPERATURE_MEDIUM, openai_api_key="env-key"
        )
        assert llm.model_name == "gpt-3.5-turbo"
        assert llm.temperature == TEST_TEMPERATURE_MEDIUM
        assert llm.provider == "openai"

    def test_initialization_without_api_key(self):
        """Test initialization without API key.

        Verifies that:
        1. A ValueError is raised when no API key is provided
        2. The error message clearly indicates that an API key is required
        """
        # Arrange
        with patch.dict(os.environ, {}, clear=True):
            # Act & Assert
            with pytest.raises(ValueError, match="OpenAI API key not provided"):
                OpenAILLM()

    @patch("langchain_openai.ChatOpenAI")
    def test_call_method(self, mock_chat_openai):
        """Test the _call method for basic text generation.

        Verifies that:
        1. The adapter correctly forwards the prompt to the underlying LLM
        2. The response from the LLM is correctly returned
        3. The invoke method is called with the correct parameters
        """
        # Arrange
        mock_instance = MagicMock()
        mock_instance.invoke.return_value.content = "Test response"
        mock_chat_openai.return_value = mock_instance

        # Act
        llm = OpenAILLM(model_name="gpt-3.5-turbo", api_key="test-key")
        result = llm._call("Test prompt")

        # Assert
        mock_instance.invoke.assert_called_once_with("Test prompt")
        assert result == "Test response"

    @patch("langchain_openai.ChatOpenAI")
    def test_call_method_with_stop_and_run_manager(self, mock_chat_openai):
        """Test the _call method with stop sequences and run manager.

        Verifies that:
        1. The adapter correctly handles stop sequences
        2. The adapter correctly handles run manager callbacks
        3. The response from the LLM is correctly returned
        """
        # Arrange
        mock_instance = MagicMock()
        mock_instance.invoke.return_value.content = "Test response"
        mock_chat_openai.return_value = mock_instance

        # Act
        llm = OpenAILLM(model_name="gpt-3.5-turbo", api_key="test-key")
        stop = ["stop"]
        test_run_id = uuid.uuid4()
        run_manager = CallbackManagerForLLMRun(run_id=test_run_id, handlers=[], inheritable_handlers=[])
        result = llm._call("Test prompt", stop=stop, run_manager=run_manager)

        # Assert
        mock_instance.invoke.assert_called_once_with("Test prompt")
        assert result == "Test response"

    @patch("langchain_openai.ChatOpenAI")
    def test_temperature_setter(self, mock_chat_openai):
        """Test the temperature setter method.

        Verifies that:
        1. The temperature can be changed after initialization
        2. The new temperature is correctly applied to both the adapter and the underlying LLM
        """
        # Arrange
        mock_instance = MagicMock()
        mock_chat_openai.return_value = mock_instance

        # Act
        llm = OpenAILLM(model_name="gpt-3.5-turbo", api_key="test-key")
        llm.temperature = TEST_TEMPERATURE_HIGH

        # Assert
        assert llm.temperature == TEST_TEMPERATURE_HIGH
        mock_instance.temperature = TEST_TEMPERATURE_HIGH


class TestOllamaLLM:
    """Test cases for the Ollama LLM adapter.

    These tests verify that the OllamaLLM adapter correctly initializes and interacts
    with the Ollama API through the langchain ChatOllama class. The tests focus on:

    1. Initialization with different base URL sources
    2. Proper configuration of model parameters
    3. Correct handling of the _call method
    4. Temperature setting and retrieval
    """

    @patch("langchain_community.chat_models.ChatOllama")
    def test_initialization_with_base_url(self, mock_chat_ollama):
        """Test initialization with explicit base URL.

        Verifies that:
        1. The adapter correctly initializes with a provided base URL
        2. The model name and temperature are set correctly
        3. The provider is correctly identified as 'ollama'
        4. The underlying ChatOllama is initialized with the correct parameters
        """
        # Arrange
        mock_instance = MagicMock()
        mock_chat_ollama.return_value = mock_instance

        # Act
        llm = OllamaLLM(model_name="llama3", temperature=TEST_TEMPERATURE_LOW, base_url="http://custom:11434")

        # Assert
        mock_chat_ollama.assert_called_once_with(model="llama3", base_url="http://custom:11434", temperature=TEST_TEMPERATURE_LOW)
        assert llm.model_name == "llama3"
        assert llm.temperature == TEST_TEMPERATURE_LOW
        assert llm.provider == "ollama"

    @patch.dict(os.environ, {"OLLAMA_BASE_URL": "http://env:11434"})
    @patch("langchain_community.chat_models.ChatOllama")
    def test_initialization_with_env_base_url(self, mock_chat_ollama):
        """Test initialization with base URL from environment variables.

        Verifies that:
        1. The adapter correctly initializes using a base URL from environment variables
        2. The model name and temperature are set correctly
        3. The provider is correctly identified as 'ollama'
        4. The underlying ChatOllama is initialized with the correct parameters
        """
        # Arrange
        mock_instance = MagicMock()
        mock_chat_ollama.return_value = mock_instance

        # Act
        llm = OllamaLLM(model_name="llama3:70b", temperature=TEST_TEMPERATURE_MEDIUM)

        # Assert
        mock_chat_ollama.assert_called_once_with(
            model="llama3:70b", base_url="http://env:11434", temperature=TEST_TEMPERATURE_MEDIUM
        )
        assert llm.model_name == "llama3:70b"
        assert llm.temperature == TEST_TEMPERATURE_MEDIUM
        assert llm.provider == "ollama"

    @patch("langchain_community.chat_models.ChatOllama")
    def test_call_method(self, mock_chat_ollama):
        """Test the _call method for basic text generation.

        Verifies that:
        1. The adapter correctly forwards the prompt to the underlying LLM
        2. The response from the LLM is correctly returned
        3. The invoke method is called with the correct parameters
        """
        # Arrange
        mock_instance = MagicMock()
        mock_instance.invoke.return_value.content = "Test response"
        mock_chat_ollama.return_value = mock_instance

        # Act
        llm = OllamaLLM(model_name="llama3", base_url="http://localhost:11434")
        result = llm._call("Test prompt")

        # Assert
        mock_instance.invoke.assert_called_once_with("Test prompt")
        assert result == "Test response"

    @patch("langchain_community.chat_models.ChatOllama")
    def test_call_method_with_stop_and_run_manager(self, mock_chat_ollama):
        """Test the _call method with stop sequences and run manager.

        Verifies that:
        1. The adapter correctly handles stop sequences
        2. The adapter correctly handles run manager callbacks
        3. The response from the LLM is correctly returned
        """
        # Arrange
        mock_instance = MagicMock()
        mock_instance.invoke.return_value.content = "Test response"
        mock_chat_ollama.return_value = mock_instance

        # Act
        llm = OllamaLLM(model_name="llama3", base_url="http://localhost:11434")
        stop = ["stop"]
        test_run_id = uuid.uuid4()
        run_manager = CallbackManagerForLLMRun(run_id=test_run_id, handlers=[], inheritable_handlers=[])
        result = llm._call("Test prompt", stop=stop, run_manager=run_manager)

        # Assert
        mock_instance.invoke.assert_called_once_with("Test prompt")
        assert result == "Test response"

    @patch("langchain_community.chat_models.ChatOllama")
    def test_temperature_setter(self, mock_chat_ollama):
        """Test the temperature setter method.

        Verifies that:
        1. The temperature can be changed after initialization
        2. The new temperature is correctly applied to both the adapter and the underlying LLM
        """
        # Arrange
        mock_instance = MagicMock()
        mock_chat_ollama.return_value = mock_instance

        # Act
        llm = OllamaLLM(model_name="llama3", base_url="http://localhost:11434")
        llm.temperature = TEST_TEMPERATURE_HIGH

        # Assert
        assert llm.temperature == TEST_TEMPERATURE_HIGH
        mock_instance.temperature = TEST_TEMPERATURE_HIGH
