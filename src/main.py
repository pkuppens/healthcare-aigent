"""Main module for healthcare multi-agent system."""

from crewai import Crew, Process

from .agents import create_medical_crew
from .llm_config import get_llm
from .tasks import (
    AssessPatientLanguageTask,
    ExtractClinicalInfoTask,
    GenerateSummaryTask,
    PreprocessMedicalTextTask,
    QualityControlTask,
)


async def process_medical_conversation(conversation: str) -> dict:
    """Process a medical conversation using the healthcare crew.

    Args:
        conversation: The medical conversation to process

    Returns:
        Dict containing the processed results
    """
    # Initialize LLM
    llm = get_llm()

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

    # Create crew
    crew = Crew(agents=agents, tasks=tasks, process=Process.sequential, verbose=True)

    # Execute crew tasks
    result = await crew.kickoff()

    return {
        "preprocessed_text": result[0],
        "language_assessment": result[1],
        "clinical_info": result[2],
        "summary": result[3],
        "quality_check": result[4],
    }


async def main():
    """Main entry point."""
    conversation = """
    Doctor: Good morning, how are you feeling today?
    Patient: Not so well, I've been having headaches.
    Doctor: How long have you been experiencing these headaches?
    Patient: About a week now. They come and go.
    Doctor: Are you taking any medications?
    Patient: Yes, I take metoprolol for my blood pressure.
    """

    result = await process_medical_conversation(conversation)
    print("Processing complete:", result)


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
