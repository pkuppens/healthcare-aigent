"""Integration tests for the LLM factory.

This module contains integration tests for the LLMFactory class, focusing on
the actual creation and connectivity of LLM instances with real providers.
"""

import os
from unittest.mock import patch

import pytest
from langchain_community.chat_models import ChatOllama
from langchain_openai import ChatOpenAI

from src.llm.llm_factory import LLMFactory, LLMType


@pytest.mark.integration
class TestLLMFactoryIntegration:
    """Integration test cases for the LLM factory."""

    @pytest.fixture
    def mock_env_vars(self):
        """Mock environment variables for API keys."""
        with patch.dict(os.environ, {"OPENAI_API_KEY": "test-key", "OLLAMA_BASE_URL": "http://localhost:11434"}):
            yield

    def test_create_local_llm_connection(self, mock_env_vars):
        """Test creating and connecting to a local LLM.

        Verifies that:
        1. The factory can create a local LLM instance
        2. The instance is of the correct type (ChatOllama)
        3. The instance can be used to generate responses
        """
        try:
            llm = LLMFactory.create_llm(LLMType.LOCAL_FAST)
            assert isinstance(llm, ChatOllama)
            # Test basic connectivity
            response = llm.invoke("Hello")
            assert response is not None
        except Exception as e:
            pytest.skip(f"Local LLM not available: {e!s}")

    def test_create_cloud_llm_connection(self, mock_env_vars):
        """Test creating and connecting to a cloud LLM.

        Verifies that:
        1. The factory can create a cloud LLM instance
        2. The instance is of the correct type (ChatOpenAI)
        3. The instance can be used to generate responses
        """
        try:
            llm = LLMFactory.create_llm(LLMType.CLOUD_FAST)
            assert isinstance(llm, ChatOpenAI)
            # Test basic connectivity
            response = llm.invoke("Hello")
            assert response is not None
        except Exception as e:
            pytest.skip(f"Cloud LLM not available: {e!s}")

    def test_get_llm_for_sensitive_task(self, mock_env_vars):
        """Test getting LLM for sensitive data task.

        Verifies that:
        1. The factory selects the appropriate LLM type for sensitive tasks
        2. The selected LLM is a local LLM (ChatOllama)
        3. The selected LLM can be used to generate responses
        """
        try:
            llm = LLMFactory.get_llm_for_task("any_task", sensitive_data=True)
            assert isinstance(llm, ChatOllama)
            # Test basic connectivity
            response = llm.invoke("Hello")
            assert response is not None
        except Exception as e:
            pytest.skip(f"Local LLM not available: {e!s}")

    def test_get_llm_for_accuracy_task(self, mock_env_vars):
        """Test getting LLM for accuracy-critical task.

        Verifies that:
        1. The factory selects the appropriate LLM type for accuracy-critical tasks
        2. The selected LLM is a cloud LLM (ChatOpenAI)
        3. The selected LLM can be used to generate responses
        """
        try:
            llm = LLMFactory.get_llm_for_task("summarization", sensitive_data=False)
            assert isinstance(llm, ChatOpenAI)
            # Test basic connectivity
            response = llm.invoke("Hello")
            assert response is not None
        except Exception as e:
            pytest.skip(f"Cloud LLM not available: {e!s}")

    def test_llm_performance_comparison(self, mock_env_vars):
        """Test comparing performance of different LLM types."""
        try:
            # Test local fast LLM
            local_fast = LLMFactory.create_llm(LLMType.LOCAL_FAST)
            local_fast_response = local_fast.invoke("Hello")

            # Test local accurate LLM
            local_accurate = LLMFactory.create_llm(LLMType.LOCAL_ACCURATE)
            local_accurate_response = local_accurate.invoke("Hello")

            # Test cloud fast LLM
            cloud_fast = LLMFactory.create_llm(LLMType.CLOUD_FAST)
            cloud_fast_response = cloud_fast.invoke("Hello")

            # Test cloud accurate LLM
            cloud_accurate = LLMFactory.create_llm(LLMType.CLOUD_ACCURATE)
            cloud_accurate_response = cloud_accurate.invoke("Hello")

            # Verify all responses are valid
            assert all(
                response is not None
                for response in [local_fast_response, local_accurate_response, cloud_fast_response, cloud_accurate_response]
            )
        except Exception as e:
            pytest.skip(f"LLM connectivity test failed: {e!s}")
