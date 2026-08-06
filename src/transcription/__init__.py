"""Transcription providers for turning recorded consultations into text.

This package mirrors the `src/llm` provider-abstraction pattern: a
`TranscriptionService` interface with one or more concrete implementations,
so the rest of the pipeline (`src/tasks`) never needs to know which provider
produced the transcript.
"""

from src.transcription.base import TranscriptionService
from src.transcription.openai_whisper import OpenAIWhisperTranscription


__all__ = ["TranscriptionService", "OpenAIWhisperTranscription"]
