"""Integration tests for the agent/task pipeline.

Two tiers are covered here:
1. A mocked run through all tasks in sequence (always runs, no external services).
2. A live run against a real LLM provider (Ollama or OpenAI), skipped when neither
   is available.
"""

import pytest

from src.llm.circuit_breaker import is_ollama_available, is_openai_available
from src.llm.llm_factory import LLMFactory, LLMType
from src.tasks import (
    AssessPatientLanguageTask,
    ExtractClinicalInfoTask,
    GenerateSummaryTask,
    PreprocessMedicalTextTask,
    QualityControlTask,
)


@pytest.mark.asyncio
async def test_agent_system_pipeline_with_mocks(mock_task_llm, mock_task_db, mock_task_logger):
    """Test that all tasks run end-to-end in sequence against a mocked LLM."""
    tasks = [
        PreprocessMedicalTextTask(),
        AssessPatientLanguageTask(),
        ExtractClinicalInfoTask(),
        GenerateSummaryTask(),
        QualityControlTask(),
    ]

    for task in tasks:
        if isinstance(task, QualityControlTask):
            result = await task.execute("Test conversation", mock_task_llm, mock_task_db, mock_task_logger)
        else:
            result = await task.execute("Test conversation", mock_task_llm)
        assert result is not None


@pytest.mark.integration
@pytest.mark.asyncio
async def test_agent_system_pipeline_with_live_llm():
    """Test the first pipeline stage against a real, running LLM provider.

    Skipped automatically (via conftest.pytest_runtest_setup) when neither
    Ollama nor an OpenAI API key is available. Deliberately only exercises
    PreprocessMedicalTextTask, which returns free-form text rather than
    strict JSON, so this test isn't flaky against normal LLM output variance.
    """
    if not (is_ollama_available() or is_openai_available()):
        pytest.skip("No LLM service available for integration tests")

    llm_type = LLMType.LOCAL_FAST if is_ollama_available() else LLMType.CLOUD_FAST
    llm = LLMFactory.create_llm(llm_type)

    result = await PreprocessMedicalTextTask().execute("Patient reports headaches for the past week.", llm)
    assert isinstance(result, str)
    assert len(result) > 0
