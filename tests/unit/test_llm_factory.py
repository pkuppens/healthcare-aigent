"""Unit tests for the LLM factory.

This module contains tests for the LLMFactory class, which is responsible for
creating different types of LLMs based on requirements for speed, accuracy, and
data sensitivity.
"""

from unittest.mock import patch

import pytest
from langchain_community.chat_models import ChatOllama
from langchain_openai import ChatOpenAI

from src.llm.llm_factory import LLMFactory, LLMType


class TestLLMFactory:
    """Test cases for the LLM factory.

    These tests verify that the LLMFactory correctly creates different types of LLMs
    based on the specified requirements and handles error cases appropriately.
    """

    @patch("langchain_community.chat_models.ChatOllama")
    def test_create_local_fast_llm(self, mock_ollama):
        """Test creating a fast local LLM.

        Verifies that:
        1. The factory creates a ChatOllama instance with the correct model
        2. The base URL is set to the default Ollama endpoint
        3. The temperature is set to the default value
        """
        llm = LLMFactory.create_llm(LLMType.LOCAL_FAST)
        mock_ollama.assert_called_once_with(model="llama3", base_url="http://localhost:11434", temperature=0.7)
        assert isinstance(llm, ChatOllama)

    @patch("langchain_community.chat_models.ChatOllama")
    def test_create_local_accurate_llm(self, mock_ollama):
        """Test creating an accurate local LLM.

        Verifies that:
        1. The factory creates a ChatOllama instance with the correct model
        2. The base URL is set to the default Ollama endpoint
        3. The temperature is set to the default value
        """
        llm = LLMFactory.create_llm(LLMType.LOCAL_ACCURATE)
        mock_ollama.assert_called_once_with(model="llama3:70b", base_url="http://localhost:11434", temperature=0.7)
        assert isinstance(llm, ChatOllama)

    @patch("langchain_openai.ChatOpenAI")
    def test_create_cloud_fast_llm(self, mock_openai):
        """Test creating a fast cloud LLM.

        Verifies that:
        1. The factory creates a ChatOpenAI instance with the correct model
        2. The model name is set to gpt-3.5-turbo for fast processing
        3. The temperature is set to the default value
        """
        llm = LLMFactory.create_llm(LLMType.CLOUD_FAST)
        mock_openai.assert_called_once_with(model_name="gpt-3.5-turbo", temperature=0.7)
        assert isinstance(llm, ChatOpenAI)

    @patch("langchain_openai.ChatOpenAI")
    def test_create_cloud_accurate_llm(self, mock_openai):
        """Test creating an accurate cloud LLM.

        Verifies that:
        1. The factory creates a ChatOpenAI instance with the correct model
        2. The model name is set to gpt-4 for high accuracy
        3. The temperature is set to the default value
        """
        llm = LLMFactory.create_llm(LLMType.CLOUD_ACCURATE)
        mock_openai.assert_called_once_with(model_name="gpt-4", temperature=0.7)
        assert isinstance(llm, ChatOpenAI)

    def test_create_llm_invalid_type(self):
        """Test creating an LLM with an invalid type.

        Verifies that:
        1. A ValueError is raised when an invalid LLM type is provided
        2. The error message clearly indicates that the type is unsupported
        """
        with pytest.raises(ValueError, match="Unsupported LLM type"):
            LLMFactory.create_llm("invalid_type")

    @patch("src.llm.llm_factory.LLMFactory.create_llm")
    def test_get_llm_for_task_sensitive_data(self, mock_create_llm):
        """Test getting LLM for sensitive data.

        Verifies that:
        1. When sensitive data is involved, a local accurate LLM is selected
        2. This ensures data privacy by keeping sensitive information on-premises
        """
        LLMFactory.get_llm_for_task("any_task", sensitive_data=True)
        mock_create_llm.assert_called_once_with(LLMType.LOCAL_ACCURATE)

    @patch("src.llm.llm_factory.LLMFactory.create_llm")
    def test_get_llm_for_task_summarization(self, mock_create_llm):
        """Test getting LLM for summarization task.

        Verifies that:
        1. For summarization tasks, a cloud accurate LLM is selected
        2. This ensures high-quality summaries with accurate medical information
        """
        LLMFactory.get_llm_for_task("summarization", sensitive_data=False)
        mock_create_llm.assert_called_once_with(LLMType.CLOUD_ACCURATE)

    @patch("src.llm.llm_factory.LLMFactory.create_llm")
    def test_get_llm_for_task_extraction(self, mock_create_llm):
        """Test getting LLM for extraction task.

        Verifies that:
        1. For extraction tasks, a cloud accurate LLM is selected
        2. This ensures accurate extraction of medical information from conversations
        """
        LLMFactory.get_llm_for_task("extraction", sensitive_data=False)
        mock_create_llm.assert_called_once_with(LLMType.CLOUD_ACCURATE)

    @patch("src.llm.llm_factory.LLMFactory.create_llm")
    def test_get_llm_for_task_default(self, mock_create_llm):
        """Test getting default LLM for other tasks.

        Verifies that:
        1. For tasks not specifically optimized, a cloud fast LLM is selected
        2. This provides a good balance of speed and accuracy for general tasks
        """
        LLMFactory.get_llm_for_task("other_task", sensitive_data=False)
        mock_create_llm.assert_called_once_with(LLMType.CLOUD_FAST)
