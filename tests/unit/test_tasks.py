"""Unit tests for tasks module.

This module contains tests for the various task classes that implement specific
functionality in the healthcare system, such as preprocessing medical text,
assessing patient language proficiency, extracting clinical information,
generating summaries, and performing quality control.
"""

import pytest

from src.tasks import (
    AssessPatientLanguageTask,
    ExtractClinicalInfoTask,
    GenerateSummaryTask,
    PreprocessMedicalTextTask,
    QualityControlTask,
)


# Test constants
QUALITY_SCORE = 95
ACCURACY_SCORE = 0.95


@pytest.fixture
def mock_llm(mock_task_llm):
    """Alias onto the shared mock LLM fixture from conftest.py."""
    return mock_task_llm


@pytest.fixture
def mock_db(mock_task_db):
    """Alias onto the shared mock database fixture from conftest.py."""
    return mock_task_db


@pytest.fixture
def mock_logger(mock_task_logger):
    """Alias onto the shared mock logger fixture from conftest.py."""
    return mock_task_logger


@pytest.mark.asyncio
async def test_preprocess_medical_text_task(mock_llm):
    """Test PreprocessMedicalTextTask execution.

    Verifies that:
    1. The task successfully processes medical text
    2. The result is a non-empty string
    3. The LLM is called with the appropriate input
    """
    task = PreprocessMedicalTextTask()
    result = await task.execute("Patient has hypertension", mock_llm)
    assert isinstance(result, str)
    assert len(result) > 0
    assert "Preprocessed" in result


@pytest.mark.asyncio
async def test_assess_patient_language_task(mock_llm):
    """Test AssessPatientLanguageTask execution.

    Verifies that:
    1. The task successfully assesses patient language proficiency
    2. The result is a dictionary with the expected keys
    3. The assessment includes language proficiency, medical literacy, and communication level
    """
    task = AssessPatientLanguageTask()
    result = await task.execute("I feel tired and my blood pressure is high", mock_llm)
    assert isinstance(result, dict)
    assert "proficiency" in result
    assert "needs_interpreter" in result
    assert "language_proficiency_scale" in result
    assert result["proficiency"] == "intermediate"
    assert result["needs_interpreter"] is False
    assert result["language_proficiency_scale"] == "B2"


@pytest.mark.asyncio
async def test_extract_clinical_info_task(mock_llm):
    """Test ExtractClinicalInfoTask execution.

    Verifies that:
    1. The task successfully extracts clinical information from text
    2. The result is a dictionary with the expected keys
    3. The extraction includes symptoms, diagnosis, treatment, and follow-up information
    """
    task = ExtractClinicalInfoTask()
    result = await task.execute("Patient reports fatigue and elevated blood pressure", mock_llm)
    assert isinstance(result, dict)
    assert "symptoms" in result
    assert "diagnosis" in result
    assert "conditions" in result
    assert "medications" in result
    assert "hypertension" in result["conditions"]
    assert "metoprolol" in result["medications"]


@pytest.mark.asyncio
async def test_generate_summary_task(mock_llm):
    """Test GenerateSummaryTask execution.

    Verifies that:
    1. The task successfully generates a summary from the input
    2. The result is a non-empty string
    3. The LLM is called with the appropriate input
    """
    task = GenerateSummaryTask()
    result = await task.execute("Patient consultation notes", mock_llm)
    assert isinstance(result, str)
    assert len(result) > 0
    assert "hypertension" in result.lower()


@pytest.mark.asyncio
async def test_quality_control_task(mock_llm, mock_db, mock_logger):
    """Test QualityControlTask execution.

    Verifies that:
    1. The task successfully performs quality control on the input
    2. The result is a dictionary with the expected keys
    3. The quality assessment includes a score, identified issues, and recommendations
    4. The task interacts with the database and logger as expected
    """
    task = QualityControlTask()
    result = await task.execute("Patient summary", mock_llm, mock_db, mock_logger)
    assert isinstance(result, dict)
    assert "accuracy_score" in result
    assert "requires_human_review" in result
    assert "quality_rating" in result
    assert result["accuracy_score"] == ACCURACY_SCORE
    assert result["requires_human_review"] is False
    assert result["quality_rating"] == QUALITY_SCORE

    # Verify database and logger interactions
    mock_db.read_patient_data.assert_called_once()
    mock_logger.log_audit_event.assert_called_once()
