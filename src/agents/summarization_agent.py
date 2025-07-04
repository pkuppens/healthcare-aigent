"""Defines the SummarizationAgent for the healthcare system.

This module creates an agent that generates a clear, concise, and accurate
summary of the medical conversation, suitable for patient records or handoffs.
"""

from crewai import Agent

from src.tools.medical_tools import MedicalTerminologyTool
from src.tools.web_tools import WebSearchTool


class SummarizationAgent(Agent):
    """An agent that creates medical summaries from conversation data.

    This agent synthesizes the information gathered by other agents to produce
    a comprehensive summary. It focuses on clarity, accuracy, and adherence
    to medical documentation standards.

    Attributes:
        agent (Agent): The crewAI agent configured for this role.
    """

    def __init__(self, llm: any):
        """Initializes the SummarizationAgent.

        Args:
            llm: The language model instance to be used by the agent.
        """
        super().__init__(
            role="Medical Summarization Specialist",
            goal="Create clear and accurate medical summaries",
            backstory="Expert in medical documentation and patient communication",
            llm=llm,
            tools=[MedicalTerminologyTool(), WebSearchTool()],
            allow_delegation=False,
            verbose=True,
        )
