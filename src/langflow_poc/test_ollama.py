"""Test script for Ollama integration with error handling."""

import os
import sys

import requests
from langchain_ollama import OllamaLLM


# Constants
HTTP_OK = 200


def test_ollama_connection(model_name: str = "mistral") -> str | None:
    """Test connection to Ollama and return a test response if successful."""
    try:
        # Get Ollama host from environment variable or use default
        ollama_host = os.getenv("OLLAMA_HOST", "http://localhost:11434")
        base_url = ollama_host.rstrip("/")

        # First check if Ollama is running
        response = requests.get(f"{base_url}/api/tags")
        if response.status_code != HTTP_OK:
            print(f"Error: Ollama service is not running at {base_url}")
            print("Please ensure Ollama is running and accessible")
            return None

        # Try to get a response from the model
        llm = OllamaLLM(model=model_name, base_url=base_url)
        response = llm.invoke("Say 'Hello, I am working!' in one sentence.")
        return response

    except requests.exceptions.ConnectionError:
        print(f"Error: Could not connect to Ollama service at {base_url}")
        print("Please check if:")
        print("1. Ollama is running")
        print("2. The service is accessible at the correct URL")
        print("3. If using Docker, ensure the containers are running and properly networked")
        return None
    except Exception as e:
        print(f"Error: An unexpected error occurred: {e!s}")
        return None


if __name__ == "__main__":
    print("Testing Ollama connection...")
    result = test_ollama_connection()
    if result:
        print("Success! Ollama is working correctly.")
        print(f"Test response: {result}")
    else:
        print("Failed to connect to Ollama. Please check the error messages above.")
        sys.exit(1)
