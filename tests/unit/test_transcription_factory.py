"""Unit tests for the transcription provider factory."""

import os
from unittest.mock import patch

import pytest

from src.transcription.factory import TranscriptionFactory
from src.transcription.openai_whisper import OpenAIWhisperTranscription


class TestTranscriptionFactory:
    """Tests for `TranscriptionFactory.create`."""

    def test_defaults_to_openai(self):
        """With no provider specified, the factory creates the OpenAI provider."""
        with patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"}, clear=True):
            service = TranscriptionFactory.create()

        assert isinstance(service, OpenAIWhisperTranscription)

    def test_reads_provider_from_env_var(self):
        """`TRANSCRIPTION_PROVIDER` selects the provider when no override is passed."""
        with patch.dict(os.environ, {"OPENAI_API_KEY": "test-key", "TRANSCRIPTION_PROVIDER": "OpenAI"}, clear=True):
            service = TranscriptionFactory.create()

        assert isinstance(service, OpenAIWhisperTranscription)

    def test_unsupported_provider_raises(self):
        """An unregistered provider name raises a clear ValueError."""
        with pytest.raises(ValueError, match="Unsupported transcription provider"):
            TranscriptionFactory.create("azure")
