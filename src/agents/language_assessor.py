"""Defines the LanguageAssessmentAgent for the healthcare system.

This module creates an agent responsible for assessing the patient's language
proficiency, sentiment, and communication needs based on the conversation.
"""

from crewai import Agent

from src.tools.medical_tools import PatientLanguageTool
from src.tools.web_tools import WebSearchTool


class LanguageAssessmentAgent(Agent):
    """An agent that assesses patient language and communication.

    This agent analyzes the patient's portion of the conversation to determine
    their language complexity, sentiment, and potential communication barriers.
    This assessment helps tailor subsequent interactions and summaries.

    Attributes:
        agent (Agent): The crewAI agent configured for this role.
    """

    def __init__(self, llm: any):
        """Initializes the LanguageAssessmentAgent.

        Args:
            llm: The language model instance to be used by the agent.
        """
        super().__init__(
            role="Language Assessment Specialist",
            goal="Assess patient language proficiency and needs",
            backstory="Expert in language assessment and medical communication",
            llm=llm,
            tools=[PatientLanguageTool(), WebSearchTool()],
            allow_delegation=False,
            verbose=True,
        )
