"""Base interface for transcription providers."""

from abc import ABC, abstractmethod
from pathlib import Path


class TranscriptionService(ABC):
    """Abstract interface for turning a recorded consultation into text.

    A real deployment would swap this for a provider bound to its data
    processing agreement (verwerkersovereenkomst) and hosting region — e.g.
    AWS Transcribe in eu-central-1 for a multi-tenant EU setup. This
    abstraction exists so that swap is a new implementation of this
    interface, not a change to the pipeline that consumes it.
    """

    @abstractmethod
    async def transcribe(self, audio_path: str | Path, language: str | None = None) -> str:
        """Transcribe an audio file to text.

        Args:
            audio_path: Path to the audio file (e.g. a recorded consultation).
            language: Optional ISO 639-1 language hint (e.g. "nl"). Providers
                that support auto-detection may ignore this.

        Returns:
            The transcribed text.

        Raises:
            RuntimeError: If transcription fails.
        """
