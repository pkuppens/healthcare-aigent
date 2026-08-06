"""Integration tests for the FastAPI application.

This module contains tests that verify the functionality of the API endpoints,
ensuring they process requests correctly and return the expected responses.
"""

from unittest.mock import AsyncMock

import pytest
from fastapi.testclient import TestClient

from src.api.api_server import app


client = TestClient(app)


@pytest.mark.llm
def test_process_conversation_endpoint():
    """Tests the /process_conversation/ endpoint.

    This exercises the full crew pipeline via LLMType.CLOUD_FAST, which
    requires a working OpenAI API key. Skipped automatically (see conftest.py)
    when OPENAI_API_KEY isn't set or the API isn't reachable.

    Verifies that:
    1. The endpoint returns a successful response (status code 200).
    2. The response is a valid JSON object.
    3. The response contains the expected keys for the processed results.
    """
    # Define a sample conversation payload
    payload = {"text": "Doctor: How are you? Patient: I have a headache."}

    # Send a POST request to the endpoint
    response = client.post("/process_conversation/", json=payload)

    # Assert that the request was successful
    assert response.status_code == 200

    # Assert that the response is a JSON object
    response_data = response.json()
    assert isinstance(response_data, dict)

    # Assert that the response contains the expected keys
    expected_keys = [
        "preprocessed_text",
        "language_assessment",
        "clinical_info",
        "summary",
        "quality_check",
    ]
    for key in expected_keys:
        assert key in response_data


def test_transcribe_and_process_endpoint(monkeypatch):
    """Tests the /transcribe_and_process/ endpoint's wiring: file upload in,
    transcript + pipeline results out. The transcription/LLM pipeline itself
    is mocked here — it's covered separately by test_main.py (mocked) and
    test_agent_system.py (live, marked integration).
    """
    mock_result = {
        "transcript": "Patient heeft hoofdpijn.",
        "preprocessed_text": "Patient has a headache.",
        "language_assessment": {"proficiency": "intermediate", "needs_interpreter": False, "language_proficiency_scale": "B1"},
        "clinical_info": {"symptoms": ["headache"], "conditions": [], "medications": [], "diagnosis": "Headache"},
        "summary": "The patient reports a headache.",
        "quality_check": {"accuracy_score": 0.9, "requires_human_review": True, "quality_rating": 90},
    }
    mock_process_audio = AsyncMock(return_value=mock_result)
    monkeypatch.setattr("src.api.api_server.process_audio_conversation_async", mock_process_audio)

    response = client.post(
        "/transcribe_and_process/",
        files={"audio": ("consult.wav", b"fake-audio-bytes", "audio/wav")},
    )

    assert response.status_code == 200
    assert response.json() == mock_result
    mock_process_audio.assert_called_once()
    args, kwargs = mock_process_audio.call_args
    assert kwargs.get("language") == "nl"
