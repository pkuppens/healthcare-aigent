"""Common test fixtures for healthcare multi-agent system."""

import os
from unittest.mock import patch

import pytest
import requests

from src.llm.circuit_breaker import is_ollama_available, is_openai_available


# Constants
HTTP_OK = 200


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
