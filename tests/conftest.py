"""Common test fixtures for healthcare multi-agent system."""

import os
from unittest.mock import patch

import pytest


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
        "Spreker B: Goedemorgen dokter, het gaat wel. Ik heb wat last van hoofdpijn.\n"
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
