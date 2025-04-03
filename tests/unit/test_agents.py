"""Unit tests for agent definitions."""

from unittest.mock import AsyncMock

import pytest

from src.agents import (
    create_clinical_extractor,
    create_language_assessor,
    create_medical_crew,
    create_medical_preprocessor,
    create_quality_control_agent,
    create_summarization_agent,
)

# Constants
NUM_TOOLS_PER_AGENT = 2
NUM_AGENTS_IN_CREW = 5

@pytest.fixture
def mock_llm():
    """Create a mock LLM for testing."""
    return AsyncMock()

@pytest.mark.asyncio
async def test_medical_preprocessor_creation(mock_llm):
    """Test medical preprocessor agent creation."""
    agent = create_medical_preprocessor(mock_llm)
    assert agent.role == "Medical Preprocessor"
    assert agent.goal == "Analyze and prepare medical conversations for processing"
    assert len(agent.tools) == NUM_TOOLS_PER_AGENT
    assert any(tool.name == "medical_terminology" for tool in agent.tools)
    assert any(tool.name == "web_search" for tool in agent.tools)

@pytest.mark.asyncio
async def test_language_assessor_creation(mock_llm):
    """Test language assessor agent creation."""
    agent = create_language_assessor(mock_llm)
    assert agent.role == "Language Assessment Specialist"
    assert agent.goal == "Assess patient language proficiency and needs"
    assert len(agent.tools) == NUM_TOOLS_PER_AGENT
    assert any(tool.name == "patient_language" for tool in agent.tools)
    assert any(tool.name == "web_search" for tool in agent.tools)

@pytest.mark.asyncio
async def test_clinical_extractor_creation(mock_llm):
    """Test clinical extractor agent creation."""
    agent = create_clinical_extractor(mock_llm)
    assert agent.role == "Clinical Information Extractor"
    assert agent.goal == "Extract and structure clinical information from conversations"
    assert len(agent.tools) == NUM_TOOLS_PER_AGENT
    assert any(tool.name == "clinical_extraction" for tool in agent.tools)
    assert any(tool.name == "web_search" for tool in agent.tools)

@pytest.mark.asyncio
async def test_summarization_agent_creation(mock_llm):
    """Test summarization agent creation."""
    agent = create_summarization_agent(mock_llm)
    assert agent.role == "Medical Summarization Specialist"
    assert agent.goal == "Create clear and accurate medical summaries"
    assert len(agent.tools) == NUM_TOOLS_PER_AGENT
    assert any(tool.name == "medical_terminology" for tool in agent.tools)
    assert any(tool.name == "web_search" for tool in agent.tools)

@pytest.mark.asyncio
async def test_quality_control_agent_creation(mock_llm):
    """Test quality control agent creation."""
    agent = create_quality_control_agent(mock_llm)
    assert agent.role == "Quality Control Specialist"
    assert agent.goal == "Ensure accuracy and completeness of medical information"
    assert len(agent.tools) == NUM_TOOLS_PER_AGENT
    assert any(tool.name == "medical_terminology" for tool in agent.tools)
    assert any(tool.name == "web_search" for tool in agent.tools)

@pytest.mark.asyncio
async def test_medical_crew_creation(mock_llm):
    """Test medical crew creation."""
    crew = create_medical_crew(mock_llm)
    assert len(crew) == NUM_AGENTS_IN_CREW
    assert crew[0].role == "Medical Preprocessor"
    assert crew[1].role == "Language Assessment Specialist"
    assert crew[2].role == "Clinical Information Extractor"
    assert crew[3].role == "Medical Summarization Specialist"
    assert crew[4].role == "Quality Control Specialist"
