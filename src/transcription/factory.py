"""Factory for creating the configured transcription provider.

Mirrors `src/llm/llm_factory.py`'s provider-by-name pattern, kept minimal
since only one provider is implemented today. See docs/transcription.md and
docs/transcription_research.md for the providers this is meant to grow into
(local Whisper, Azure, Google) and how they'd be compared.
"""

import os
from typing import ClassVar

from src.transcription.base import TranscriptionService
from src.transcription.openai_whisper import OpenAIWhisperTranscription


class TranscriptionFactory:
    """Creates a `TranscriptionService` based on the `TRANSCRIPTION_PROVIDER` env var."""

    _provider_map: ClassVar[dict[str, type[TranscriptionService]]] = {
        "openai": OpenAIWhisperTranscription,
    }

    @classmethod
    def create(cls, provider: str | None = None) -> TranscriptionService:
        """Create the transcription provider to use.

        Args:
            provider: Provider name (e.g. "openai"). Defaults to the
                `TRANSCRIPTION_PROVIDER` env var, then "openai".

        Returns:
            A configured `TranscriptionService`.

        Raises:
            ValueError: If the provider name isn't registered.
        """
        provider = (provider or os.getenv("TRANSCRIPTION_PROVIDER", "openai")).lower()

        if provider not in cls._provider_map:
            supported = ", ".join(sorted(cls._provider_map))
            raise ValueError(f"Unsupported transcription provider: {provider!r} (supported: {supported})")

        return cls._provider_map[provider]()
