"""Unit tests for the LLM factory."""

from unittest.mock import patch

import pytest
from langchain_community.chat_models import ChatOllama
from langchain_openai import ChatOpenAI

from src.llm.llm_factory import LLMFactory, LLMType


class TestLLMFactory:
    """Test cases for the LLM factory."""

    @patch("langchain_community.chat_models.ChatOllama")
    def test_create_local_fast_llm(self, mock_ollama):
        """Test creating a fast local LLM."""
        llm = LLMFactory.create_llm(LLMType.LOCAL_FAST)
        mock_ollama.assert_called_once_with(model="llama3", base_url="http://localhost:11434", temperature=0.7)
        assert isinstance(llm, ChatOllama)

    @patch("langchain_community.chat_models.ChatOllama")
    def test_create_local_accurate_llm(self, mock_ollama):
        """Test creating an accurate local LLM."""
        llm = LLMFactory.create_llm(LLMType.LOCAL_ACCURATE)
        mock_ollama.assert_called_once_with(model="llama3:70b", base_url="http://localhost:11434", temperature=0.7)
        assert isinstance(llm, ChatOllama)

    @patch("langchain_openai.ChatOpenAI")
    def test_create_cloud_fast_llm(self, mock_openai):
        """Test creating a fast cloud LLM."""
        llm = LLMFactory.create_llm(LLMType.CLOUD_FAST)
        mock_openai.assert_called_once_with(model_name="gpt-3.5-turbo", temperature=0.7)
        assert isinstance(llm, ChatOpenAI)

    @patch("langchain_openai.ChatOpenAI")
    def test_create_cloud_accurate_llm(self, mock_openai):
        """Test creating an accurate cloud LLM."""
        llm = LLMFactory.create_llm(LLMType.CLOUD_ACCURATE)
        mock_openai.assert_called_once_with(model_name="gpt-4", temperature=0.7)
        assert isinstance(llm, ChatOpenAI)

    def test_create_llm_invalid_type(self):
        """Test creating an LLM with an invalid type."""
        with pytest.raises(ValueError, match="Unsupported LLM type"):
            LLMFactory.create_llm("invalid_type")

    @patch("src.llm.llm_factory.LLMFactory.create_llm")
    def test_get_llm_for_task_sensitive_data(self, mock_create_llm):
        """Test getting LLM for sensitive data."""
        LLMFactory.get_llm_for_task("any_task", sensitive_data=True)
        mock_create_llm.assert_called_once_with(LLMType.LOCAL_ACCURATE)

    @patch("src.llm.llm_factory.LLMFactory.create_llm")
    def test_get_llm_for_task_summarization(self, mock_create_llm):
        """Test getting LLM for summarization task."""
        LLMFactory.get_llm_for_task("summarization", sensitive_data=False)
        mock_create_llm.assert_called_once_with(LLMType.CLOUD_ACCURATE)

    @patch("src.llm.llm_factory.LLMFactory.create_llm")
    def test_get_llm_for_task_extraction(self, mock_create_llm):
        """Test getting LLM for extraction task."""
        LLMFactory.get_llm_for_task("extraction", sensitive_data=False)
        mock_create_llm.assert_called_once_with(LLMType.CLOUD_ACCURATE)

    @patch("src.llm.llm_factory.LLMFactory.create_llm")
    def test_get_llm_for_task_default(self, mock_create_llm):
        """Test getting default LLM for other tasks."""
        LLMFactory.get_llm_for_task("other_task", sensitive_data=False)
        mock_create_llm.assert_called_once_with(LLMType.CLOUD_FAST)
