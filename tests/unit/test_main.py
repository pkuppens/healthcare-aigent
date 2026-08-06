"""Unit tests for the top-level pipeline entry points in src/main.py."""

from unittest.mock import AsyncMock

import pytest

from src.main import process_audio_conversation_async, process_medical_conversation_async


@pytest.mark.asyncio
async def test_process_medical_conversation_async_runs_full_pipeline(mock_task_llm, monkeypatch):
    """The text pipeline runs all five tasks and returns their combined results."""
    monkeypatch.setattr("src.main.LLMFactory.get_llm_for_task", lambda *a, **kw: mock_task_llm)

    result = await process_medical_conversation_async("Patient has hypertension.")

    assert set(result.keys()) == {
        "preprocessed_text",
        "language_assessment",
        "clinical_info",
        "summary",
        "quality_check",
    }
    assert result["quality_check"]["requires_human_review"] is False


@pytest.mark.asyncio
async def test_process_audio_conversation_async_transcribes_then_processes(mock_task_llm, monkeypatch):
    """The audio pipeline transcribes first, then runs the same task pipeline."""
    monkeypatch.setattr("src.main.LLMFactory.get_llm_for_task", lambda *a, **kw: mock_task_llm)

    mock_transcriber = AsyncMock()
    mock_transcriber.transcribe.return_value = "Patient has hypertension."

    result = await process_audio_conversation_async("fake/path.wav", transcription_service=mock_transcriber)

    mock_transcriber.transcribe.assert_called_once_with("fake/path.wav", language="nl")
    assert result["transcript"] == "Patient has hypertension."
    assert "summary" in result
