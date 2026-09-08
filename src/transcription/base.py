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

    The `str` return type below is deliberately the simplest thing that
    works today: it does not carry speaker turns or timestamps. See
    docs/transcription.md ("Next step: speaker diarization") for why that's
    a real gap for consult recordings and how the interface would need to
    change (e.g. a `Transcript` with per-turn speaker labels) to close it.
    """

    @abstractmethod
    async def transcribe(self, audio: bytes, *, filename: str = "audio.wav", language: str | None = None) -> str:
        """Transcribe raw audio bytes to text.

        Implementations work on in-memory audio, not a filesystem path: the
        source may just as well be an API upload or a microphone capture as
        a file on disk, and a file is only one of several ways to get bytes
        in front of a transcriber.

        Args:
            audio: The raw audio bytes.
            filename: Original filename, used by providers (e.g. OpenAI's
                Whisper API) that infer the audio format from its extension.
            language: Optional ISO 639-1 language hint (e.g. "nl"). Providers
                that support auto-detection may ignore this.

        Returns:
            The transcribed text.

        Raises:
            RuntimeError: If transcription fails.
        """

    async def transcribe_file(self, audio_path: str | Path, language: str | None = None) -> str:
        """Convenience wrapper for callers that only have a file path (e.g.
        CLI/script use, or `scripts/fetch_sample_audio.py` output).

        Reads the file into memory and delegates to `transcribe`, so
        individual providers never need to implement file-reading
        themselves.

        Args:
            audio_path: Path to the audio file (e.g. a recorded consultation).
            language: Optional ISO 639-1 language hint (e.g. "nl").

        Returns:
            The transcribed text.

        Raises:
            RuntimeError: If the file doesn't exist or transcription fails.
        """
        path = Path(audio_path)
        if not path.is_file():
            raise RuntimeError(f"Audio file not found: {path}")
        return await self.transcribe(path.read_bytes(), filename=path.name, language=language)
