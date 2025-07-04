"""Defines the QualityControlAgent for the healthcare system.

This module creates an agent responsible for verifying the accuracy,
completeness, and overall quality of the information processed by the other agents.
"""

from crewai import Agent

from src.tools.medical_tools import MedicalTerminologyTool
from src.tools.web_tools import WebSearchTool


class QualityControlAgent(Agent):
    """An agent that ensures the quality of the final medical summary.

    This final agent in the crew reviews the outputs from the previous agents,
    including the clinical extraction and summary, to check for inconsistencies,
    inaccuracies, or omissions. It acts as a final validation step.

    Attributes:
        agent (Agent): The crewAI agent configured for this role.
    """

    def __init__(self, llm: any):
        """Initializes the QualityControlAgent.

        Args:
            llm: The language model instance to be used by the agent.
        """
        super().__init__(
            role="Quality Control Specialist",
            goal="Ensure accuracy and completeness of medical information",
            backstory="Expert in medical quality assurance and data validation",
            llm=llm,
            tools=[MedicalTerminologyTool(), WebSearchTool()],
            allow_delegation=False,
            verbose=True,
        )
