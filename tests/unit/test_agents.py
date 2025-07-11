"""Unit tests for agent definitions.

This module contains tests for the various agent types used in the healthcare system.
It verifies that agents are correctly created with the appropriate roles, goals, and tools.
"""

from unittest.mock import AsyncMock

import pytest

from src.agents import (
    ClinicalExtractionAgent,
    LanguageAssessmentAgent,
    PreprocessingAgent,
    QualityControlAgent,
    SummarizationAgent,
    create_medical_crew,
)


# Constants
NUM_TOOLS_PER_AGENT = 2
NUM_AGENTS_IN_CREW = 5


@pytest.fixture
def mock_llm():
    """Create a mock LLM for testing.

    Returns:
        An AsyncMock object that simulates an LLM for testing agent creation
    """
    mock = AsyncMock()
    mock.supports_stop_words = lambda: False
    mock.model = "gpt-4"
    mock.temperature = 0.7
    mock.max_tokens = 1000
    mock.tools = []
    return mock


@pytest.mark.asyncio
async def test_medical_preprocessor_creation(mock_llm):
    """Test medical preprocessor agent creation.

    Verifies that:
    1. The agent has the correct role and goal
    2. The agent has the expected number of tools
    3. The agent has the required medical_terminology and web_search tools
    """
    agent = PreprocessingAgent(mock_llm)
    assert agent.role == "Medical Preprocessor"
    assert agent.goal == "Analyze and prepare medical conversations for processing"
    assert agent.tools is not None
    assert len(agent.tools) == NUM_TOOLS_PER_AGENT
    assert any(tool.name == "medical_terminology" for tool in agent.tools)
    assert any(tool.name == "web_search" for tool in agent.tools)


@pytest.mark.asyncio
async def test_language_assessor_creation(mock_llm):
    """Test language assessor agent creation.

    Verifies that:
    1. The agent has the correct role and goal
    2. The agent has the expected number of tools
    3. The agent has the required patient_language and web_search tools
    """
    agent = LanguageAssessmentAgent(mock_llm)
    assert agent.role == "Language Assessment Specialist"
    assert agent.goal == "Assess patient language proficiency and needs"
    assert agent.tools is not None
    assert len(agent.tools) == NUM_TOOLS_PER_AGENT
    assert any(tool.name == "patient_language" for tool in agent.tools)
    assert any(tool.name == "web_search" for tool in agent.tools)


@pytest.mark.asyncio
async def test_clinical_extractor_creation(mock_llm):
    """Test clinical extractor agent creation.

    Verifies that:
    1. The agent has the correct role and goal
    2. The agent has the expected number of tools
    3. The agent has the required clinical_extraction and web_search tools
    """
    agent = ClinicalExtractionAgent(mock_llm)
    assert agent.role == "Clinical Information Extractor"
    assert agent.goal == "Extract and structure clinical information from conversations"
    assert agent.tools is not None
    assert len(agent.tools) == NUM_TOOLS_PER_AGENT
    assert any(tool.name == "clinical_extraction" for tool in agent.tools)
    assert any(tool.name == "web_search" for tool in agent.tools)


@pytest.mark.asyncio
async def test_summarization_agent_creation(mock_llm):
    """Test summarization agent creation.

    Verifies that:
    1. The agent has the correct role and goal
    2. The agent has the expected number of tools
    3. The agent has the required medical_terminology and web_search tools
    """
    agent = SummarizationAgent(mock_llm)
    assert agent.role == "Medical Summarization Specialist"
    assert agent.goal == "Create clear and accurate medical summaries"
    assert agent.tools is not None
    assert len(agent.tools) == NUM_TOOLS_PER_AGENT
    assert any(tool.name == "medical_terminology" for tool in agent.tools)
    assert any(tool.name == "web_search" for tool in agent.tools)


@pytest.mark.asyncio
async def test_quality_control_agent_creation(mock_llm):
    """Test quality control agent creation.

    Verifies that:
    1. The agent has the correct role and goal
    2. The agent has the expected number of tools
    3. The agent has the required medical_terminology and web_search tools
    """
    agent = QualityControlAgent(mock_llm)
    assert agent.role == "Quality Control Specialist"
    assert agent.goal == "Ensure accuracy and completeness of medical information"
    assert agent.tools is not None
    assert len(agent.tools) == NUM_TOOLS_PER_AGENT
    assert any(tool.name == "medical_terminology" for tool in agent.tools)
    assert any(tool.name == "web_search" for tool in agent.tools)


@pytest.mark.asyncio
async def test_medical_crew_creation(mock_llm):
    """Test medical crew creation.

    Verifies that:
    1. The crew contains the expected number of agents
    2. The agents are created in the correct order
    3. Each agent has the correct role
    """
    crew = create_medical_crew(mock_llm)
    assert len(crew) == NUM_AGENTS_IN_CREW
    assert crew[0].role == "Medical Preprocessor"
    assert crew[1].role == "Language Assessment Specialist"
    assert crew[2].role == "Clinical Information Extractor"
    assert crew[3].role == "Medical Summarization Specialist"
    assert crew[4].role == "Quality Control Specialist"
