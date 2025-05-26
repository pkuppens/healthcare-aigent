import asyncio
import json
import logging
import os
import sys

import requests
from crewai import Agent
from langchain_community.chat_models import ChatOllama
from langchain_openai import ChatOpenAI

from src.llm_config import get_llm
from src.tools.medical_tools import MedicalTerminologyTool
from src.utils import configure_logging, load_config, setup_project_paths


# Add the project root to the Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
sys.path.append(project_root)

# Constants
HTTP_OK_STATUS = 200

# Set up project paths
setup_project_paths()

# Load configuration
config = load_config()

# Configure logging
log_level_str = config.get("log_level", "INFO")
log_level = getattr(logging, log_level_str.upper(), logging.INFO)
log_file = config.get("log_file", "crewai_llm.log")
configure_logging(level=log_level, log_file=log_file)

# Get logger for this module
logger = logging.getLogger(__name__)


class MockedLLM:
    """A mocked LLM for testing when no real LLM is available."""

    def __init__(self, name: str = "MockedLLM"):
        self.name = name
        logger.info(f"Initialized {self.name}")

    def invoke(self, prompt: str) -> str:
        """Mock implementation of invoke method."""
        logger.info(f"MockedLLM.invoke called with prompt: {prompt}")
        return f"This is a mocked response to: {prompt}"

    def generate(self, prompts: list[str]) -> list[str]:
        """Mock implementation of generate method."""
        logger.info(f"MockedLLM.generate called with {len(prompts)} prompts")
        return [f"Mocked response {i + 1} to: {prompt}" for i, prompt in enumerate(prompts)]


def check_ollama_service(base_url: str = "http://localhost:11434") -> bool:
    """
    Check if Ollama service is running.

    Args:
        base_url: The base URL for the Ollama service

    Returns:
        bool: True if Ollama is running, False otherwise
    """
    try:
        response = requests.get(f"{base_url}/api/tags")
        if response.status_code == HTTP_OK_STATUS:
            logger.info("Ollama service is running")
            return True
        else:
            logger.error(f"Ollama service returned status code: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        logger.error(f"Could not connect to Ollama service at {base_url}")
        logger.error("Please ensure Ollama is installed and running")
        logger.error("Installation instructions: https://ollama.ai/download")
        return False
    except Exception as e:
        logger.error(f"Error checking Ollama service: {e}")
        return False


def get_available_ollama_models(base_url: str = "http://localhost:11434") -> list[str]:
    """
    Get list of available Ollama models.

    Args:
        base_url: The base URL for the Ollama service

    Returns:
        List[str]: List of available model names
    """
    try:
        response = requests.get(f"{base_url}/api/tags")
        if response.status_code == HTTP_OK_STATUS:
            models = [model["name"] for model in response.json().get("models", [])]
            logger.info(f"Available Ollama models: {models}")
            return models
        else:
            logger.error(f"Failed to get Ollama models: {response.status_code}")
            return []
    except Exception as e:
        logger.error(f"Error getting Ollama models: {e}")
        return []


def setup_ollama_model(model_name: str | None = None, base_url: str = "http://localhost:11434") -> str:
    """
    Set up Ollama model, checking if it's available and falling back if needed.

    Args:
        model_name: The desired model name
        base_url: The base URL for the Ollama service

    Returns:
        str: The model name to use
    """
    # Check if Ollama is running
    if not check_ollama_service(base_url):
        raise RuntimeError("Ollama service is not running")

    # Get available models
    available_models = get_available_ollama_models(base_url)
    if not available_models:
        raise RuntimeError("No Ollama models available")

    # Check if requested model is available
    if model_name and model_name in available_models:
        logger.info(f"Using requested Ollama model: {model_name}")
        return model_name

    # Fall back to first available model
    fallback_model = available_models[0]
    if model_name:
        logger.warning(f"Requested model '{model_name}' not found, falling back to '{fallback_model}'")
    else:
        logger.info(f"No model specified, using '{fallback_model}'")

    return fallback_model


def get_llm_with_fallback() -> ChatOpenAI | ChatOllama | MockedLLM:
    """
    Get an LLM instance with fallback options.

    Returns:
        An LLM instance (OpenAI, Ollama, or Mocked)
    """
    # Try OpenAI first
    try:
        logger.info("Attempting to use OpenAI LLM")
        llm = get_llm(provider="OPENAI")
        logger.info("Successfully created OpenAI LLM")
        return llm
    except Exception as e:
        logger.warning(f"Failed to create OpenAI LLM: {e}")
        logger.info("Falling back to Ollama")

    # Try Ollama next
    try:
        # Set up Ollama model
        model_name = config.get("ollama_model_name", "mistral")
        base_url = config.get("ollama_base_url", "http://localhost:11434")

        model_name = setup_ollama_model(model_name, base_url)
        os.environ["OLLAMA_MODEL_NAME"] = model_name

        llm = get_llm(provider="OLLAMA")
        logger.info("Successfully created Ollama LLM")
        return llm
    except Exception as e:
        logger.warning(f"Failed to create Ollama LLM: {e}")
        logger.info("Falling back to MockedLLM")

    # Fall back to MockedLLM
    logger.warning("Using MockedLLM as all other options failed")
    return MockedLLM()


async def main():
    """Main function to run the CrewAI LLM test."""
    try:
        # Get LLM with fallback
        llm = get_llm_with_fallback()

        # Test the LLM
        logger.info("Testing LLM with a simple prompt")
        try:
            response = llm.invoke("Hello, this is a test.")
            logger.info(f"LLM Response: {response}")

            # Log the complete response as JSON for debugging
            if hasattr(response, "content"):
                logger.debug(f"Complete LLM Response: {json.dumps({'content': response.content}, indent=2)}")
            else:
                logger.debug(f"Complete LLM Response: {json.dumps({'response': str(response)}, indent=2)}")
        except Exception as e:
            logger.error(f"Error testing LLM: {e}")
            return

        # Create a CrewAI agent using the LLM
        logger.info("Creating a CrewAI agent")
        agent = Agent(
            role="Medical Assistant",
            goal="Assist healthcare professionals with patient information",
            backstory="You are an AI assistant specialized in healthcare.",
            llm=llm,
            verbose=True,
        )

        # Test the agent
        logger.info("Testing agent with a medical text")
        try:
            result = agent.execute("Summarize the following medical text: The patient presents with a 3-day history of headache.")
            logger.info(f"Agent Result: {result}")
        except Exception as e:
            logger.error(f"Error executing agent: {e}")
            return

        # Create a more complex agent with tools
        logger.info("Creating a medical terminology tool")
        medical_tool = MedicalTerminologyTool()

        # Create an agent with the tool
        logger.info("Creating an agent with the medical terminology tool")
        medical_agent = Agent(
            role="Medical Terminology Expert",
            goal="Explain medical terminology in simple terms",
            backstory="You are an expert in medical terminology and can explain complex terms in simple language.",
            tools=[medical_tool],
            llm=llm,
            verbose=True,
        )

        # Test the agent with a tool
        logger.info("Testing agent with a medical terminology question")
        try:
            result = medical_agent.execute("Explain the term 'hypertension' in simple terms.")
            logger.info(f"Medical Agent Result: {result}")
        except Exception as e:
            logger.error(f"Error executing medical agent: {e}")

    except Exception as e:
        logger.error(f"Unexpected error in main function: {e}")


if __name__ == "__main__":
    asyncio.run(main())
