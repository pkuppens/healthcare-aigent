"""Common test fixtures for healthcare multi-agent system."""

import json
import os
from unittest.mock import AsyncMock, patch

import pytest
import requests

from src.llm.circuit_breaker import is_ollama_available, is_openai_available


# Constants
HTTP_OK = 200
QUALITY_SCORE = 95
ACCURACY_SCORE = 0.95


def is_service_available(url: str, timeout: int = 5) -> bool:
    """Check if a service is available."""
    try:
        response = requests.get(url, timeout=timeout)
        return response.status_code == HTTP_OK
    except (requests.RequestException, TimeoutError):
        return False


@pytest.fixture
def mock_env_vars():
    """Mock environment variables for testing."""
    with patch.dict(
        os.environ,
        {
            "LLM_PROVIDER": "OPENAI",
            "OPENAI_API_KEY": "test-key",
            "OPENAI_MODEL_NAME": "gpt-3.5-turbo",
            "OLLAMA_BASE_URL": "http://localhost:11434",
            "OLLAMA_MODEL_NAME": "llama3",
        },
    ):
        yield


@pytest.fixture
def mock_transcript():
    """Mock medical conversation transcript."""
    return (
        "Spreker A: Goedemorgen, hoe gaat het met u?\n"
        "Spreker B: Goedemorgen dokter, het gaat wel. "
        "Ik heb wat last van hoofdpijn.\n"
        "Spreker A: Hoelang heeft u hier al last van?\n"
        "Spreker B: Ongeveer een week. Het komt en gaat.\n"
        "Spreker A: Gebruikt u nog medicijnen?\n"
        "Spreker B: Ja, ik gebruik metoprolol voor mijn bloeddruk.\n"
        "Spreker A: Heeft u nog andere klachten?\n"
        "Spreker B: Nee, verder gaat het wel goed."
    )


@pytest.fixture
def mock_patient_data():
    """Mock patient database."""
    return {
        "patient_123": {
            "history": "Bekend met hypertensie en diabetes type 2.",
            "allergies": ["penicilline", "aspirine"],
            "medications": ["metoprolol", "metformine"],
            "last_visit": "2024-01-15",
        }
    }


@pytest.fixture
def mock_task_llm():
    """Create a mock LLM whose responses match the JSON contract each task expects.

    Shared by unit task tests and the agent-system integration test so the mock
    payloads only need to be kept in sync with `src/tasks/*` in one place.
    """
    llm = AsyncMock()

    async def mock_ainvoke(prompt: str) -> str:
        if "Preprocess this medical text" in prompt:
            return "Preprocessed: Patient has hypertension"
        elif "Assess the language proficiency" in prompt:
            return json.dumps({"proficiency": "intermediate", "needs_interpreter": False, "language_proficiency_scale": "B2"})
        elif "Extract clinical information" in prompt:
            return json.dumps(
                {
                    "symptoms": ["headache"],
                    "conditions": ["hypertension"],
                    "medications": ["metoprolol"],
                    "diagnosis": "Essential hypertension",
                }
            )
        elif "Generate a concise medical summary" in prompt:
            return "Patient presents with hypertension"
        elif "Perform quality control" in prompt:
            return json.dumps({"accuracy_score": ACCURACY_SCORE, "requires_human_review": False, "quality_rating": QUALITY_SCORE})
        return "Mock response"

    llm.ainvoke = mock_ainvoke
    return llm


@pytest.fixture
def mock_task_db():
    """Create a mock database returning fixed patient data for task tests."""
    db = AsyncMock()
    db.read_patient_data = AsyncMock(
        return_value={"patient_id": "123", "name": "John Doe", "history": "Hypertension", "allergies": ["Penicillin"]}
    )
    db.propose_database_update = AsyncMock(return_value=True)
    return db


@pytest.fixture
def mock_task_logger():
    """Create a mock audit logger for task tests."""
    logger = AsyncMock()
    logger.log_audit_event = AsyncMock(return_value=True)
    return logger


@pytest.fixture
def ollama_available():
    """Check if Ollama service is available."""
    return is_ollama_available()


@pytest.fixture
def openai_available():
    """Check if OpenAI API is available."""
    return is_openai_available()


def pytest_configure(config):
    """Configure pytest with custom markers."""
    config.addinivalue_line(
        "markers",
        "integration: mark test as integration test requiring external services",
    )
    config.addinivalue_line(
        "markers",
        "llm: mark test as requiring LLM access",
    )
    config.addinivalue_line(
        "markers",
        "slow: mark test as slow running",
    )


def pytest_runtest_setup(item):
    """Skip tests based on service availability."""
    if "integration" in item.keywords:
        if not (is_ollama_available() or is_openai_available()):
            pytest.skip("No LLM service available for integration tests")

    if "llm" in item.keywords:
        if not is_openai_available():
            pytest.skip("OpenAI API not available")
