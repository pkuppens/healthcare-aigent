"""Unit tests for the transcription providers."""

import os
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.transcription.openai_whisper import OpenAIWhisperTranscription


class TestOpenAIWhisperTranscription:
    """Tests for the OpenAI Whisper API transcription provider."""

    def test_initialization_without_api_key(self):
        """A ValueError is raised when no API key is available."""
        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(ValueError, match="OpenAI API key not provided"):
                OpenAIWhisperTranscription()

    @pytest.mark.asyncio
    @patch("src.transcription.openai_whisper.AsyncOpenAI")
    async def test_transcribe_file_missing_file(self, mock_openai_cls):
        """A RuntimeError is raised when the audio file doesn't exist."""
        provider = OpenAIWhisperTranscription(api_key="test-key")

        with pytest.raises(RuntimeError, match="Audio file not found"):
            await provider.transcribe_file("this/path/does/not/exist.wav")

    @pytest.mark.asyncio
    @patch("src.transcription.openai_whisper.AsyncOpenAI")
    async def test_transcribe_returns_text(self, mock_openai_cls):
        """The provider forwards the audio bytes and returns the transcribed text."""
        mock_client = MagicMock()
        mock_client.audio.transcriptions.create = AsyncMock(return_value=MagicMock(text="Patient heeft hoofdpijn."))
        mock_openai_cls.return_value = mock_client

        provider = OpenAIWhisperTranscription(api_key="test-key")
        result = await provider.transcribe(b"fake-audio-bytes", filename="sample.wav", language="nl")

        assert result == "Patient heeft hoofdpijn."
        _, kwargs = mock_client.audio.transcriptions.create.call_args
        assert kwargs["model"] == "whisper-1"
        assert kwargs["language"] == "nl"
        assert kwargs["file"] == ("sample.wav", b"fake-audio-bytes")

    @pytest.mark.asyncio
    @patch("src.transcription.openai_whisper.AsyncOpenAI")
    async def test_transcribe_file_reads_then_transcribes(self, mock_openai_cls, tmp_path):
        """`transcribe_file` reads the file into memory and delegates to `transcribe`."""
        audio_path = tmp_path / "sample.wav"
        audio_path.write_bytes(b"fake-audio-bytes")

        mock_client = MagicMock()
        mock_client.audio.transcriptions.create = AsyncMock(return_value=MagicMock(text="Patient heeft hoofdpijn."))
        mock_openai_cls.return_value = mock_client

        provider = OpenAIWhisperTranscription(api_key="test-key")
        result = await provider.transcribe_file(audio_path, language="nl")

        assert result == "Patient heeft hoofdpijn."
        _, kwargs = mock_client.audio.transcriptions.create.call_args
        assert kwargs["file"] == ("sample.wav", b"fake-audio-bytes")

    @pytest.mark.asyncio
    @patch("src.transcription.openai_whisper.AsyncOpenAI")
    async def test_transcribe_wraps_api_errors(self, mock_openai_cls):
        """API failures are wrapped in a RuntimeError with context."""
        mock_client = MagicMock()
        mock_client.audio.transcriptions.create = AsyncMock(side_effect=Exception("rate limited"))
        mock_openai_cls.return_value = mock_client

        provider = OpenAIWhisperTranscription(api_key="test-key")

        with pytest.raises(RuntimeError, match="Failed to transcribe"):
            await provider.transcribe(b"fake-audio-bytes", filename="sample.wav")
