"""Initializes the agents package and provides a factory for creating medical agent crews.

This module aggregates all specialized agent classes from the `agents` package and
exports them for easy access. It also includes the `create_medical_crew` function,
which assembles a list of all agent instances required for the healthcare
conversation analysis workflow.
"""

"""Initializes the agents package and provides a factory for creating medical agent crews.

This module aggregates all specialized agent classes from the `agents` package and
exports them for easy access. It also includes the `create_medical_crew` function,
which assembles a list of all agent instances required for the healthcare
conversation analysis workflow.
"""

from crewai import Agent

from .clinical_extractor import ClinicalExtractionAgent
from .language_assessor import LanguageAssessmentAgent
from .preprocessing_agent import PreprocessingAgent
from .quality_control_agent import QualityControlAgent
from .summarization_agent import SummarizationAgent


def create_medical_crew(llm: any) -> list[Agent]:
    """Creates and returns a list of all medical agents for the conversation analysis crew.

    This factory function instantiates each specialized agent with the provided
    language model and assembles them into a list, ready to be used by a CrewAI crew.

    Args:
        llm: The language model instance to be used by all agents.

    Returns:
        A list of configured Agent instances.
    """
    return [
        PreprocessingAgent(llm),
        LanguageAssessmentAgent(llm),
        ClinicalExtractionAgent(llm),
        SummarizationAgent(llm),
        QualityControlAgent(llm),
    ]
