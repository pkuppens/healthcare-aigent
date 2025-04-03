"""Main execution script for the healthcare multi-agent system."""

from crewai import Crew, Process

from .agents import (
    clinical_extractor_agent,
    patient_language_agent,
    preprocessing_agent,
    quality_control_agent,
    summarization_agent,
)
from .tasks import (
    task_assess_language,
    task_extract_info,
    task_preprocess,
    task_quality_check_and_propose_update,
    task_summarize_patient,
    task_summarize_soap,
)


def main():
    """Main execution function."""
    # Example transcript with speaker labels
    mock_transcript = """
    Spreker A: Goedemorgen, mevrouw Jansen. Hoe gaat het met u?
    Spreker B: Goedemorgen dokter. Het gaat wel, maar ik heb de laatste tijd veel last van hoofdpijn.
    Spreker A: Kunt u daar wat meer over vertellen? Wanneer begon dit?
    Spreker B: Het begon ongeveer twee weken geleden. Het is vooral 's ochtends erg.
    Spreker A: Gebruikt u nog steeds de metoprolol voor uw bloeddruk?
    Spreker B: Ja, elke ochtend één tablet.
    Spreker A: Heeft u nog andere klachten?
    Spreker B: Ik voel me soms wat duizelig, vooral als ik snel opsta.
    """

    # Example patient ID
    mock_patient_id = "patient_123"

    # Create crew
    consult_review_crew = Crew(
        agents=[preprocessing_agent, patient_language_agent, clinical_extractor_agent, summarization_agent, quality_control_agent],
        tasks=[
            task_preprocess,
            task_assess_language,
            task_extract_info,
            task_summarize_soap,
            task_summarize_patient,
            task_quality_check_and_propose_update,
        ],
        process=Process.sequential,
        verbose=2,
    )

    # Run crew with inputs
    inputs = {"transcript": mock_transcript, "patient_id": mock_patient_id}

    print("\nStarting healthcare multi-agent system...")
    result = consult_review_crew.kickoff(inputs=inputs)

    print("\n\n## Crew Uitkomst:")
    print(result)


if __name__ == "__main__":
    main()
