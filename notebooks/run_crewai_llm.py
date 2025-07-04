import asyncio
import json
import logging
import os
import sys

import requests
from crewai import Agent
from langchain_community.chat_models import ChatOllama
from langchain_openai import ChatOpenAI

from src.llm.base import BaseLLM
from src.llm.llm_factory import LLMFactory
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


def get_llm_with_fallback() -> BaseLLM:
    """
    Get an LLM instance with fallback options using the LLMFactory.

    Returns:
        An LLM instance.
    """
    try:
        logger.info("Attempting to create LLM using the factory")
        # Using get_llm_for_task to leverage the factory's fallback logic
        llm = LLMFactory.get_llm_for_task("summarization")
        logger.info("Successfully created LLM from factory")
        return llm
    except Exception as e:
        logger.warning(f"Failed to create any LLM from factory: {e}")
        logger.info("Falling back to MockedLLM")
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
