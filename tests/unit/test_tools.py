"""Unit tests for tools module."""

from unittest.mock import AsyncMock

import pytest

from src.tools.database_tools import (
    propose_database_update,
    read_patient_data,
)
from src.tools.logging_tools import log_audit_event
from src.tools.medical_tools import (
    ClinicalExtractionTool,
    MedicalTerminologyTool,
    PatientLanguageTool,
)
from src.tools.web_tools import WebSearchTool


@pytest.fixture
def mock_db():
    """Create a mock database for testing."""
    db = AsyncMock()
    # The database operations are async because they may involve:
    # 1. Network calls to external databases
    # 2. File I/O operations
    # 3. Integration with other async services
    # Using async/await allows these operations to be non-blocking
    db.get_patient_data = AsyncMock(
        return_value={
            "patient_id": "123",
            "name": "John Doe",
            "history": "Hypertension",
            "allergies": ["Penicillin"],
        }
    )
    db.update_patient_data = AsyncMock(return_value=True)
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
    # Arrange: Set up test data - patient ID to query
    patient_id = "patient_123"

    # Act: Call the function under test to read patient data
    result = await read_patient_data(patient_id, mock_db)

    # Assert: Verify the result is a dictionary containing expected patient data
    assert isinstance(result, dict), f"Expected dict but got {type(result)}: {result}"
    assert "patient_id" in result, f"Missing 'patient_id' key in result: {result}"
    assert "history" in result, f"Missing 'history' key in result: {result}"

    # Assert: Verify the mock was called correctly
    mock_db.get_patient_data.assert_called_once_with(patient_id)


@pytest.mark.asyncio
async def test_propose_database_update(mock_db):
    """Test proposing database update."""
    # Arrange: Set up test data - patient ID and update data
    patient_id = "patient_123"
    update_data = {"new_diagnosis": "hypertension"}

    # Act: Call the function under test to propose database update
    result = await propose_database_update(patient_id, update_data, mock_db)

    # Assert: Verify the result is a boolean indicating success
    assert isinstance(result, bool), f"Expected bool but got {type(result)}: {result}"
    assert result is True, f"Expected True but got {result}"

    # Assert: Verify the mock was called with correct parameters
    mock_db.update_patient_data.assert_called_once_with(patient_id, update_data)


@pytest.mark.asyncio
async def test_web_search_tool():
    """Test web search tool."""
    # Arrange: Create WebSearchTool instance and set up search query
    tool = WebSearchTool()
    search_query = "hypertension"

    # Act: Execute the web search tool with the query
    result = await tool._run(search_query)

    # Assert: Verify the result is a string containing search results
    assert isinstance(result, str), f"Expected str but got {type(result)}: {result}"
    assert f"Mock search results for: {search_query}" in result, f"Expected mock search results in output, but got: {result}"


@pytest.mark.asyncio
async def test_log_audit_event(mock_logger):
    """Test audit event logging."""
    # Arrange: Set up audit event parameters
    event_type = "data_access"
    patient_id = "patient_123"
    user_id = "doctor_456"

    # Act: Call the function under test to log audit event
    result = await log_audit_event(
        event_type=event_type,
        patient_id=patient_id,
        user_id=user_id,
        logger=mock_logger,
    )

    # Assert: Verify the result indicates successful logging
    assert isinstance(result, bool), f"Expected bool but got {type(result)}: {result}"
    assert result is True, f"Expected True but got {result}"

    # Assert: Verify the logger mock was called
    mock_logger.log_audit_event.assert_called_once()


@pytest.mark.asyncio
async def test_medical_terminology_tool():
    """Test MedicalTerminologyTool execution."""
    # Arrange: Create MedicalTerminologyTool instance and set up medical text
    tool = MedicalTerminologyTool()
    medical_text = "Patient has hypertension"

    # Act: Execute the medical terminology tool with the text
    result = await tool._run(medical_text)

    # Assert: Verify the result is a non-empty string
    assert isinstance(result, str), f"Expected str but got {type(result)}: {result}"
    assert len(result) > 0, f"Expected non-empty string but got: '{result}'"


@pytest.mark.asyncio
async def test_patient_language_tool():
    """Test PatientLanguageTool execution."""
    # Arrange: Create PatientLanguageTool instance and set up patient communication
    tool = PatientLanguageTool()
    patient_input = "I feel tired and my blood pressure is high"

    # Act: Execute the patient language tool with the input
    result = await tool._run(patient_input)

    # Assert: Verify the result is a dictionary with expected language analysis keys
    assert isinstance(result, dict), f"Expected dict but got {type(result)}: {result}"
    assert "language_proficiency" in result, f"Missing 'language_proficiency' key in result: {result}"
    assert "medical_literacy" in result, f"Missing 'medical_literacy' key in result: {result}"
    assert "suggested_communication_level" in result, f"Missing 'suggested_communication_level' key in result: {result}"


@pytest.mark.asyncio
async def test_clinical_extraction_tool():
    """Test ClinicalExtractionTool execution."""
    # Arrange: Create ClinicalExtractionTool instance and set up clinical text
    tool = ClinicalExtractionTool()
    clinical_text = "Patient reports fatigue and elevated blood pressure"

    # Act: Execute the clinical extraction tool with the text
    result = await tool._run(clinical_text)

    # Assert: Verify the result is a dictionary with expected clinical data keys
    assert isinstance(result, dict), f"Expected dict but got {type(result)}: {result}"
    assert "symptoms" in result, f"Missing 'symptoms' key in result: {result}"
    assert "diagnosis" in result, f"Missing 'diagnosis' key in result: {result}"
    assert "treatment" in result, f"Missing 'treatment' key in result: {result}"
    assert "follow_up" in result, f"Missing 'follow_up' key in result: {result}"
