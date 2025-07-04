"""Integration tests for the FastAPI application.

This module contains tests that verify the functionality of the API endpoints,
ensuring they process requests correctly and return the expected responses.
"""

from fastapi.testclient import TestClient

from src.api.api_server import app


client = TestClient(app)


def test_process_conversation_endpoint():
    """Tests the /process_conversation/ endpoint.

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
