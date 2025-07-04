"""Main module for the healthcare multi-agent system.

This module serves as the primary entry point for running the healthcare AI agent crew.
It defines the main workflow for processing a medical conversation, from initializing
the language model and agents to executing the tasks and returning the final results.
"""

from crewai import Crew, Process

from src.agents import create_medical_crew
from src.llm.llm_factory import LLMFactory, LLMType
from src.tasks import (
    AssessPatientLanguageTask,
    ExtractClinicalInfoTask,
    GenerateSummaryTask,
    PreprocessMedicalTextTask,
    QualityControlTask,
)


def process_medical_conversation(conversation: str) -> dict:
    """Processes a medical conversation using the healthcare agent crew.

    This function orchestrates the entire workflow. It initializes the language model
    using the LLMFactory, creates the specialized agents, defines the sequence of tasks,
    and runs the crew to get the processed results.

    Args:
        conversation: A string containing the medical conversation to be processed.

    Returns:
        A dictionary containing the structured results from each task in the workflow.
    """
    # Initialize the appropriate LLM using the factory
    # We choose CLOUD_FAST as a default for general-purpose conversation processing.
    llm = LLMFactory.create_llm(LLMType.CLOUD_FAST)

    # Create agents
    agents = create_medical_crew(llm)

    # Create tasks
    tasks = [
        PreprocessMedicalTextTask(),
        AssessPatientLanguageTask(),
        ExtractClinicalInfoTask(),
        GenerateSummaryTask(),
        QualityControlTask(),
    ]

    # Create and run the crew
    crew = Crew(agents=agents, tasks=tasks, process=Process.sequential, verbose=True)
    result = crew.kickoff()

    return {
        "preprocessed_text": result[0],
        "language_assessment": result[1],
        "clinical_info": result[2],
        "summary": result[3],
        "quality_check": result[4],
    }


def main():
    """Defines the main entry point for the application.

    This function provides a sample conversation and calls the processing function
    to demonstrate the system's functionality. It then prints the final results.
    """
    conversation = """
    Doctor: Good morning, how are you feeling today?
    Patient: Not so well, I've been having headaches.
    Doctor: How long have you been experiencing these headaches?
    Patient: About a week now. They come and go.
    Doctor: Are you taking any medications?
    Patient: Yes, I take metoprolol for my blood pressure.
    """

    result = process_medical_conversation(conversation)
    print("Processing complete:", result)


if __name__ == "__main__":
    main()
