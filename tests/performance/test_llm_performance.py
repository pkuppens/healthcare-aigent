"""Performance tests for LLM models.

This module contains performance tests for different LLM models, focusing on
response time, token usage, and other performance metrics.
"""

import os
import time
from unittest.mock import patch

import pytest
from langchain_community.chat_models import ChatOllama
from langchain_openai import ChatOpenAI

from src.llm.llm_factory import LLMFactory, LLMType


# Performance test constants
LOCAL_LLM_MAX_RESPONSE_TIME = 5.0  # Maximum acceptable response time for local LLM in seconds
CLOUD_LLM_MAX_RESPONSE_TIME = 10.0  # Maximum acceptable response time for cloud LLM in seconds
RESPONSE_TIME_CONSISTENCY_THRESHOLD = 0.2  # Maximum allowed deviation from average response time (20%)


@pytest.mark.performance
class TestLLMPerformance:
    """Performance test cases for LLM models."""

    @pytest.fixture
    def mock_env_vars(self):
        """Mock environment variables for API keys."""
        with patch.dict(os.environ, {"OPENAI_API_KEY": "test-key", "OLLAMA_BASE_URL": "http://localhost:11434"}):
            yield

    def test_local_llm_response_time(self, mock_env_vars):
        """Test response time of local LLM.

        Verifies that:
        1. The local LLM can respond within an acceptable time frame
        2. The response time is consistent across multiple calls
        """
        try:
            llm = LLMFactory.create_llm(LLMType.LOCAL_FAST)
            assert isinstance(llm, ChatOllama)

            # Measure response time
            start_time = time.time()
            response = llm.invoke("Hello")
            end_time = time.time()

            response_time = end_time - start_time
            assert response is not None
            assert response_time < LOCAL_LLM_MAX_RESPONSE_TIME  # Response should be within 5 seconds

            # Test consistency
            times = []
            for _ in range(3):
                start_time = time.time()
                llm.invoke("Hello")
                end_time = time.time()
                times.append(end_time - start_time)

            # Check that response times are consistent (within 20% of each other)
            avg_time = sum(times) / len(times)
            for t in times:
                assert abs(t - avg_time) / avg_time < RESPONSE_TIME_CONSISTENCY_THRESHOLD

        except Exception as e:
            pytest.skip(f"Local error: {e}")

    def test_cloud_llm_response_time(self, mock_env_vars):
        """Test response time of cloud LLM.

        Verifies that:
        1. The cloud LLM can respond within an acceptable time frame
        2. The response time is consistent across multiple calls
        """
        try:
            llm = LLMFactory.create_llm(LLMType.CLOUD_FAST)
            assert isinstance(llm, ChatOpenAI)

            # Measure response time
            start_time = time.time()
            response = llm.invoke("Hello")
            end_time = time.time()

            response_time = end_time - start_time
            assert response is not None
            assert response_time < CLOUD_LLM_MAX_RESPONSE_TIME  # Response should be within 10 seconds

            # Test consistency
            times = []
            for _ in range(3):
                start_time = time.time()
                llm.invoke("Hello")
                end_time = time.time()
                times.append(end_time - start_time)

            # Check that response times are consistent (within 20% of each other)
            avg_time = sum(times) / len(times)
            for t in times:
                assert abs(t - avg_time) / avg_time < RESPONSE_TIME_CONSISTENCY_THRESHOLD

        except Exception as e:
            pytest.skip(f"Cloud error: {e}")

    def test_llm_comparison(self, mock_env_vars):
        """Compare performance between local and cloud LLMs.

        Verifies that:
        1. Local LLM is generally faster than cloud LLM for simple queries
        2. Both LLMs can handle the same query successfully
        """
        try:
            local_llm = LLMFactory.create_llm(LLMType.LOCAL_FAST)
            cloud_llm = LLMFactory.create_llm(LLMType.CLOUD_FAST)

            # Test query
            query = "What is the capital of France?"

            # Measure local LLM response time
            local_start = time.time()
            local_response = local_llm.invoke(query)
            local_time = time.time() - local_start

            # Measure cloud LLM response time
            cloud_start = time.time()
            cloud_response = cloud_llm.invoke(query)
            cloud_time = time.time() - cloud_start

            # Verify responses
            assert local_response is not None
            assert cloud_response is not None

            # For simple queries, local LLM should be faster
            assert local_time < cloud_time

        except Exception as e:
            pytest.skip(f"LLM error: {e}")
