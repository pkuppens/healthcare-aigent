"""Defines the PreprocessingAgent for the healthcare system.

This module is responsible for creating an agent that specializes in analyzing
and preparing medical conversations for further processing. It standardizes
terminology and formats the text to be suitable for other agents.
"""

from crewai import Agent

from src.tools.medical_tools import MedicalTerminologyTool
from src.tools.web_tools import WebSearchTool


class PreprocessingAgent(Agent):
    """An agent that preprocesses medical text for analysis.

    The PreprocessingAgent is the first step in the AI crew, responsible for
    taking raw conversation text and cleaning it up. It leverages tools to
    standardize medical terms and perform general text processing.

    Attributes:
        agent (Agent): The crewAI agent configured for this role.
    """

    def __init__(self, llm: any):
        """Initializes the PreprocessingAgent.

        Args:
            llm: The language model instance to be used by the agent.
        """
        super().__init__(
            role="Medical Preprocessor",
            goal="Analyze and prepare medical conversations for processing",
            backstory="Expert in medical terminology and conversation analysis",
            llm=llm,
            tools=[MedicalTerminologyTool(), WebSearchTool()],
            allow_delegation=False,
            verbose=True,
        )
