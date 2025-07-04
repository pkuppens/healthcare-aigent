"""Defines the ClinicalExtractionAgent for the healthcare system.

This module creates an agent that specializes in extracting structured
clinical information (such as symptoms, medications, and diagnoses) from
the medical conversation.
"""

from crewai import Agent

from src.tools.medical_tools import ClinicalExtractionTool
from src.tools.web_tools import WebSearchTool


class ClinicalExtractionAgent(Agent):
    """An agent that extracts structured clinical data from text.

    This agent is tasked with identifying and structuring key clinical entities
    mentioned in the conversation. It uses specialized tools to ensure accuracy
    in recognizing medical terminology.

    Attributes:
        agent (Agent): The crewAI agent configured for this role.
    """

    def __init__(self, llm: any):
        """Initializes the ClinicalExtractionAgent.

        Args:
            llm: The language model instance to be used by the agent.
        """
        super().__init__(
            role="Clinical Information Extractor",
            goal="Extract and structure clinical information from conversations",
            backstory="Expert in clinical data extraction and medical knowledge",
            llm=llm,
            tools=[ClinicalExtractionTool(), WebSearchTool()],
            allow_delegation=False,
            verbose=True,
        )
