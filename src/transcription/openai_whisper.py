"""OpenAI Whisper API transcription provider."""

import os

from openai import AsyncOpenAI

from src.transcription.base import TranscriptionService


class OpenAIWhisperTranscription(TranscriptionService):
    """Transcribes audio using OpenAI's hosted Whisper API (`whisper-1`).

    This is the cloud option: no local model download, but audio leaves the
    process boundary. For a real GGZ deployment this would need to run
    somewhere covered by a signed subverwerkersovereenkomst (or be replaced
    entirely by a self-hosted/AWS Transcribe pipeline) — this implementation
    is a showcase stub, not a compliant path for real patient data.

    No speaker diarization: `whisper-1` returns a single undifferentiated
    text block, not "Spreker A / Spreker B" turns. See docs/transcription.md
    for why that's a real gap for this use case and the concrete next steps.
    """

    def __init__(self, api_key: str | None = None, model: str = "whisper-1"):
        """Initialize the provider.

        Args:
            api_key: OpenAI API key. Falls back to the OPENAI_API_KEY env var.
            model: The Whisper model name to use.

        Raises:
            ValueError: If no API key is available.
        """
        self._api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self._api_key:
            raise ValueError("OpenAI API key not provided and OPENAI_API_KEY environment variable not set")
        self._model = model
        self._client = AsyncOpenAI(api_key=self._api_key)

    async def transcribe(self, audio: bytes, *, filename: str = "audio.wav", language: str | None = None) -> str:
        """Transcribe raw audio bytes using the Whisper API.

        The API takes the audio content directly — it never touches a
        filesystem path — and infers the format from `filename`'s extension.

        Args:
            audio: The raw audio bytes.
            filename: Original filename; only its extension is used, to tell
                the API what audio format it's receiving.
            language: Optional ISO 639-1 language hint (e.g. "nl").

        Returns:
            The transcribed text.

        Raises:
            RuntimeError: If the API call fails.
        """
        try:
            kwargs = {"model": self._model, "file": (filename, audio)}
            if language:
                kwargs["language"] = language
            response = await self._client.audio.transcriptions.create(**kwargs)
            return response.text
        except Exception as e:
            raise RuntimeError(f"Failed to transcribe {filename}: {e}") from e
