"""Unit tests for tasks module."""

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
    llm = AsyncMock()
    llm.ainvoke = AsyncMock(return_value="Mock response")
    return llm


@pytest.fixture
def mock_db():
    """Create a mock database for testing."""
    db = AsyncMock()
    db.read_patient_data = AsyncMock(
        return_value={"patient_id": "123", "name": "John Doe", "history": "Hypertension", "allergies": ["Penicillin"]}
    )
    db.propose_database_update = AsyncMock(return_value=True)
    return db


@pytest.fixture
def mock_logger():
    """Create a mock logger for testing."""
    logger = AsyncMock()
    logger.log_audit_event = AsyncMock(return_value=True)
    return logger


@pytest.mark.asyncio
async def test_preprocess_medical_text_task(mock_llm):
    """Test PreprocessMedicalTextTask execution."""
    task = PreprocessMedicalTextTask()
    result = await task.execute("Patient has hypertension", mock_llm)
    assert isinstance(result, str)
    assert len(result) > 0


@pytest.mark.asyncio
async def test_assess_patient_language_task(mock_llm):
    """Test AssessPatientLanguageTask execution."""
    task = AssessPatientLanguageTask()
    result = await task.execute("I feel tired and my blood pressure is high", mock_llm)
    assert isinstance(result, dict)
    assert "language_proficiency" in result
    assert "medical_literacy" in result
    assert "suggested_communication_level" in result


@pytest.mark.asyncio
async def test_extract_clinical_info_task(mock_llm):
    """Test ExtractClinicalInfoTask execution."""
    task = ExtractClinicalInfoTask()
    result = await task.execute("Patient reports fatigue and elevated blood pressure", mock_llm)
    assert isinstance(result, dict)
    assert "symptoms" in result
    assert "diagnosis" in result
    assert "treatment" in result
    assert "follow_up" in result


@pytest.mark.asyncio
async def test_generate_summary_task(mock_llm):
    """Test GenerateSummaryTask execution."""
    task = GenerateSummaryTask()
    result = await task.execute("Patient consultation notes", mock_llm)
    assert isinstance(result, str)
    assert len(result) > 0


@pytest.mark.asyncio
async def test_quality_control_task(mock_llm, mock_db, mock_logger):
    """Test QualityControlTask execution."""
    task = QualityControlTask()
    result = await task.execute("Patient summary", mock_llm, mock_db, mock_logger)
    assert isinstance(result, dict)
    assert "quality_score" in result
    assert "issues_found" in result
    assert "recommendations" in result
