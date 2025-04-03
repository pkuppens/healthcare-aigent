"""Agent definitions for healthcare system."""

from crewai import Agent

from .tools.medical_tools import (
    ClinicalExtractionTool,
    MedicalTerminologyTool,
    PatientLanguageTool,
)
from .tools.web_tools import WebSearchTool


def create_medical_preprocessor(llm) -> Agent:
    """Create a medical preprocessing agent."""
    return Agent(
        role="Medical Preprocessor",
        goal="Analyze and prepare medical conversations for processing",
        backstory="Expert in medical terminology and conversation analysis",
        llm=llm,
        tools=[MedicalTerminologyTool(), WebSearchTool()],
    )


def create_language_assessor(llm) -> Agent:
    """Create a language assessment agent."""
    return Agent(
        role="Language Assessment Specialist",
        goal="Assess patient language proficiency and medical literacy",
        backstory="Expert in language assessment and medical communication",
        llm=llm,
        tools=[PatientLanguageTool()],
    )


def create_clinical_extractor(llm) -> Agent:
    """Create a clinical information extraction agent."""
    return Agent(
        role="Clinical Information Extractor",
        goal="Extract and structure clinical information from conversations",
        backstory="Expert in clinical data extraction and medical knowledge",
        llm=llm,
        tools=[ClinicalExtractionTool(), WebSearchTool()],
    )


def create_summarization_agent(llm) -> Agent:
    """Create a medical summarization agent."""
    return Agent(
        role="Medical Summarization Specialist",
        goal="Create clear and accurate medical summaries",
        backstory="Expert in medical documentation and patient communication",
        llm=llm,
        tools=[MedicalTerminologyTool(), WebSearchTool()],
    )


def create_quality_control_agent(llm) -> Agent:
    """Create a quality control agent."""
    return Agent(
        role="Quality Control Specialist",
        goal="Verify medical information accuracy and propose updates",
        backstory="Expert in medical quality assurance and data validation",
        llm=llm,
        tools=[WebSearchTool()],
    )


def create_medical_crew(llm) -> list[Agent]:
    """Create a crew of medical agents."""
    return [
        create_medical_preprocessor(llm),
        create_language_assessor(llm),
        create_clinical_extractor(llm),
        create_summarization_agent(llm),
        create_quality_control_agent(llm),
    ]
