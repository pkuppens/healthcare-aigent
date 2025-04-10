"""Unit tests for the LLM factory.

This module contains tests for the LLMFactory class, which is responsible for creating
instances of different LLM types based on configuration settings. The tests verify that
the factory correctly handles various LLM types, providers, and fallback scenarios.
"""

import os
from unittest.mock import MagicMock, patch

import pytest

from src.llm.base import BaseLLM
from src.llm.fallback import FallbackLLM
from src.llm.llm_factory import LLMFactory, LLMType
from src.llm.ollama_llm import OllamaLLM
from src.llm.openai_llm import OpenAILLM

# Test constants
TEST_TEMPERATURE = 0.7
TEST_MODEL_NAME = "test-model"
TEST_API_KEY = "test-api-key"
TEST_BASE_URL = "http://test:11434"


class TestLLMFactory:
    """Test cases for the LLMFactory class.

    These tests verify that the factory correctly creates LLM instances based on
    configuration settings and handles various edge cases appropriately.
    """

    @patch("src.llm.openai_llm.OpenAILLM")
    def test_create_local_fast_llm(self, mock_openai_llm):
        """Test creating a local fast LLM.

        Verifies that:
        1. The factory correctly creates a local fast LLM instance
        2. The correct model name and temperature are used
        3. The provider is set to 'openai'
        """
        mock_instance = MagicMock(spec=OpenAILLM)
        mock_openai_llm.return_value = mock_instance

        llm = LLMFactory.create_llm(
            llm_type=LLMType.LOCAL_FAST, model_name=TEST_MODEL_NAME, temperature=TEST_TEMPERATURE, api_key=TEST_API_KEY
        )

        mock_openai_llm.assert_called_once_with(model_name=TEST_MODEL_NAME, temperature=TEST_TEMPERATURE, api_key=TEST_API_KEY)
        assert isinstance(llm, BaseLLM)
        assert llm.provider == "openai"

    @patch("src.llm.ollama_llm.OllamaLLM")
    def test_create_cloud_fast_llm(self, mock_ollama_llm):
        """Test creating a cloud fast LLM.

        Verifies that:
        1. The factory correctly creates a cloud fast LLM instance
        2. The correct model name and temperature are used
        3. The provider is set to 'ollama'
        """
        mock_instance = MagicMock(spec=OllamaLLM)
        mock_ollama_llm.return_value = mock_instance

        llm = LLMFactory.create_llm(
            llm_type=LLMType.CLOUD_FAST, model_name=TEST_MODEL_NAME, temperature=TEST_TEMPERATURE, base_url=TEST_BASE_URL
        )

        mock_ollama_llm.assert_called_once_with(model_name=TEST_MODEL_NAME, temperature=TEST_TEMPERATURE, base_url=TEST_BASE_URL)
        assert isinstance(llm, BaseLLM)
        assert llm.provider == "ollama"

    @patch("src.llm.fallback.FallbackLLM")
    def test_create_fallback_llm(self, mock_fallback_llm):
        """Test creating a fallback LLM.

        Verifies that:
        1. The factory correctly creates a fallback LLM instance
        2. The primary and fallback LLMs are correctly configured
        3. The retry strategy is properly set up
        """
        mock_primary = MagicMock(spec=OpenAILLM)
        mock_fallback = MagicMock(spec=OllamaLLM)
        mock_instance = MagicMock(spec=FallbackLLM)
        mock_fallback_llm.return_value = mock_instance

        llm = LLMFactory.create_llm(
            llm_type=LLMType.CLOUD_FAST,  # Using CLOUD_FAST as primary
            primary_llm=mock_primary,
            fallback_llm=mock_fallback,
            max_retries=3,
        )

        mock_fallback_llm.assert_called_once_with(primary_llm=mock_primary, fallback_llm=mock_fallback, max_retries=3)
        assert isinstance(llm, BaseLLM)
        assert llm.provider == "fallback"

    def test_create_llm_invalid_type(self):
        """Test creating an LLM with an invalid type.

        Verifies that:
        1. The factory raises a ValueError for invalid LLM types
        2. The error message clearly indicates the invalid type
        """
        with pytest.raises(ValueError, match="Invalid LLM type: invalid_type"):
            LLMFactory.create_llm(llm_type="invalid_type")  # type: ignore

    @patch("src.llm.openai_llm.OpenAILLM")
    def test_create_llm_with_env_vars(self, mock_openai_llm):
        """Test creating an LLM using environment variables.

        Verifies that:
        1. The factory correctly uses environment variables for configuration
        2. The LLM is created with the correct parameters
        """
        mock_instance = MagicMock(spec=OpenAILLM)
        mock_openai_llm.return_value = mock_instance

        with patch.dict(
            os.environ,
            {"OPENAI_API_KEY": TEST_API_KEY, "OPENAI_MODEL_NAME": TEST_MODEL_NAME, "OPENAI_TEMPERATURE": str(TEST_TEMPERATURE)},
        ):
            llm = LLMFactory.create_llm(llm_type=LLMType.LOCAL_FAST)

        mock_openai_llm.assert_called_once_with(model_name=TEST_MODEL_NAME, temperature=TEST_TEMPERATURE, api_key=TEST_API_KEY)
        assert isinstance(llm, BaseLLM)
        assert llm.provider == "openai"
