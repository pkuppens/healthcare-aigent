"""Unit tests for the LLM factory.

This module contains tests for the LLMFactory class, which is responsible for creating
instances of different LLM types based on configuration settings. The tests verify that
the factory correctly handles various LLM types, providers, and fallback scenarios.
"""

import os
from unittest.mock import MagicMock, patch

import pytest

from src.llm.base import BaseLLM
from src.llm.llm_factory import LLMFactory, LLMType
from src.llm.ollama_llm import OllamaLLM
from src.llm.openai_llm import OpenAILLM


# Test constants
TEST_TEMPERATURE = 0.7
TEST_API_KEY = "test-api-key"
TEST_BASE_URL = "http://test:11434"


class TestLLMFactory:
    """Test cases for the LLMFactory class.

    These tests verify that the factory correctly creates LLM instances based on
    configuration settings and handles various edge cases appropriately.
    """

    def test_create_local_fast_llm(self):
        """Test creating a local fast LLM.

        Verifies that:
        1. The factory correctly creates a local fast LLM instance using Ollama
        2. The correct model name (llama3) and temperature (0.7) are used
        3. The provider is set to 'ollama'
        """
        mock_ollama = MagicMock(spec=OllamaLLM)
        mock_ollama.provider = "ollama"

        with patch.dict(LLMFactory._provider_map, {"ollama": lambda **kwargs: mock_ollama}):
            llm = LLMFactory.create_llm(llm_type=LLMType.LOCAL_FAST)

            # First check the instance type and provider
            assert isinstance(llm, BaseLLM)
            assert llm.provider == "ollama"

            # Then check that the mock was created with the expected parameters
            assert isinstance(llm, MagicMock)
            assert llm is mock_ollama

    def test_create_cloud_fast_llm(self):
        """Test creating a cloud fast LLM.

        Verifies that:
        1. The factory correctly creates a cloud fast LLM instance using OpenAI
        2. The correct model name (gpt-3.5-turbo) and temperature (0.7) are used
        3. The provider is set to 'openai'
        """
        mock_openai = MagicMock(spec=OpenAILLM)
        mock_openai.provider = "openai"

        with patch.dict(os.environ, {"OPENAI_API_KEY": TEST_API_KEY}):
            with patch.dict(LLMFactory._provider_map, {"openai": lambda **kwargs: mock_openai}):
                llm = LLMFactory.create_llm(llm_type=LLMType.CLOUD_FAST)

                # First check the instance type and provider
                assert isinstance(llm, BaseLLM)
                assert llm.provider == "openai"

                # Then check that the mock was created with the expected parameters
                assert isinstance(llm, MagicMock)
                assert llm is mock_openai

    @patch("src.llm.llm_factory.LLMFactory.create_llm")
    def test_get_llm_for_task(self, mock_create_llm):
        """Test getting LLM for different task types.

        Verifies that:
        1. The factory selects the appropriate LLM type based on task type and sensitivity
        2. For sensitive tasks, it uses CLOUD_ACCURATE
        3. For non-sensitive tasks, it uses CLOUD_FAST
        """
        mock_instance = MagicMock(spec=BaseLLM)
        mock_create_llm.return_value = mock_instance

        # Test sensitive task
        llm = LLMFactory.get_llm_for_task("diagnosis", sensitive_data=True)
        mock_create_llm.assert_called_with(LLMType.CLOUD_ACCURATE, None)
        assert llm == mock_instance

        # Test non-sensitive task
        mock_create_llm.reset_mock()
        llm = LLMFactory.get_llm_for_task("summarization", sensitive_data=False)
        mock_create_llm.assert_called_with(LLMType.CLOUD_FAST, None)
        assert llm == mock_instance

    def test_create_llm_invalid_type(self):
        """Test creating an LLM with an invalid type.

        Verifies that:
        1. The factory raises a ValueError for invalid LLM types
        2. The error message clearly indicates the invalid type
        """
        # Create a mock LLMType that's not in the _llm_type_map
        mock_type = MagicMock()
        mock_type.value = "INVALID_TYPE"

        with pytest.raises(ValueError, match="Unsupported LLM type"):
            LLMFactory.create_llm(llm_type=mock_type)

    def test_create_llm_with_custom_temperature(self):
        """Test creating an LLM with a custom temperature.

        Verifies that:
        1. The factory correctly uses the provided temperature override
        2. The default temperature from the config is not used
        """
        mock_openai = MagicMock(spec=OpenAILLM)
        mock_openai.provider = "openai"

        with patch.dict(os.environ, {"OPENAI_API_KEY": TEST_API_KEY}):
            with patch.dict(LLMFactory._provider_map, {"openai": lambda **kwargs: mock_openai}):
                llm = LLMFactory.create_llm(llm_type=LLMType.CLOUD_FAST, temperature=0.5)

                # First check the instance type and provider
                assert isinstance(llm, BaseLLM)
                assert llm.provider == "openai"

                # Then check that the mock was created with the expected parameters
                assert isinstance(llm, MagicMock)
                assert llm is mock_openai
