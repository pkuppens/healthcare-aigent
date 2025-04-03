"""Unit tests for tools module."""

from unittest.mock import AsyncMock

import pytest

from src.tools.database_tools import propose_database_update, read_patient_data
from src.tools.logging_tools import log_audit_event
from src.tools.medical_tools import ClinicalExtractionTool, MedicalTerminologyTool, PatientLanguageTool
from src.tools.web_tools import WebSearchTool


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
async def test_read_patient_data(mock_db):
    """Test reading patient data."""
    result = await read_patient_data("patient_123", mock_db)
    assert isinstance(result, dict)
    assert "patient_id" in result
    assert "history" in result
    mock_db.read_patient_data.assert_called_once_with("patient_123")


@pytest.mark.asyncio
async def test_propose_database_update(mock_db):
    """Test proposing database update."""
    update_data = {"new_diagnosis": "hypertension"}
    result = await propose_database_update("patient_123", update_data, mock_db)
    assert isinstance(result, bool)
    assert result is True
    mock_db.propose_database_update.assert_called_once_with("patient_123", update_data)


@pytest.mark.asyncio
async def test_web_search_tool():
    """Test web search tool."""
    tool = WebSearchTool()
    result = await tool._run("hypertension")
    assert isinstance(result, str)
    assert "Mock search results for: hypertension" in result


@pytest.mark.asyncio
async def test_log_audit_event(mock_logger):
    """Test audit event logging."""
    result = await log_audit_event(event_type="data_access", patient_id="patient_123", user_id="doctor_456", logger=mock_logger)
    assert isinstance(result, bool)
    assert result is True
    mock_logger.log_audit_event.assert_called_once()


@pytest.mark.asyncio
async def test_medical_terminology_tool():
    """Test MedicalTerminologyTool execution."""
    tool = MedicalTerminologyTool()
    result = await tool._run("Patient has hypertension")
    assert isinstance(result, str)
    assert len(result) > 0


@pytest.mark.asyncio
async def test_patient_language_tool():
    """Test PatientLanguageTool execution."""
    tool = PatientLanguageTool()
    result = await tool._run("I feel tired and my blood pressure is high")
    assert isinstance(result, dict)
    assert "language_proficiency" in result
    assert "medical_literacy" in result
    assert "suggested_communication_level" in result


@pytest.mark.asyncio
async def test_clinical_extraction_tool():
    """Test ClinicalExtractionTool execution."""
    tool = ClinicalExtractionTool()
    result = await tool._run("Patient reports fatigue and elevated blood pressure")
    assert isinstance(result, dict)
    assert "symptoms" in result
    assert "diagnosis" in result
    assert "treatment" in result
    assert "follow_up" in result
