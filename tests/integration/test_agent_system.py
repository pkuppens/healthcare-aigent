"""Integration tests for agent system."""

from unittest.mock import AsyncMock

import pytest

from src.tasks import (
    AssessPatientLanguageTask,
    ExtractClinicalInfoTask,
    GenerateSummaryTask,
    PreprocessMedicalTextTask,
    QualityControlTask,
)


@pytest.fixture
def mock_llm():
    """Create a mock LLM for testing."""
    return AsyncMock()


@pytest.fixture
def mock_db():
    """Create a mock database for testing."""
    return AsyncMock()


@pytest.fixture
def mock_logger():
    """Create a mock logger for testing."""
    return AsyncMock()


@pytest.mark.asyncio
async def test_agent_system_integration(mock_llm, mock_db, mock_logger):
    """Test the integration of all agents and tasks."""
    # Create tasks
    tasks = [
        PreprocessMedicalTextTask(),
        AssessPatientLanguageTask(),
        ExtractClinicalInfoTask(),
        GenerateSummaryTask(),
        QualityControlTask(),
    ]

    # Test task execution
    for task in tasks:
        if isinstance(task, QualityControlTask):
            result = await task.execute("Test conversation", mock_llm, mock_db, mock_logger)
        else:
            result = await task.execute("Test conversation", mock_llm)
        assert result is not None
