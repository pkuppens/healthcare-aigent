"""Main module for the healthcare multi-agent system.

This module serves as the primary entry point for running the healthcare AI agent
pipeline. It defines the main workflow for processing a medical conversation, from
initializing the language model to executing each task in sequence and returning
the final, structured results.
"""

import asyncio

from src.llm.llm_factory import LLMFactory
from src.tasks import (
    AssessPatientLanguageTask,
    ExtractClinicalInfoTask,
    GenerateSummaryTask,
    PreprocessMedicalTextTask,
    QualityControlTask,
)
from src.tools.logging_tools import Logger
from src.tools.mock_database import MockHealthcareDatabase


class _QualityControlDataSource:
    """Adapts the patient-keyed `HealthcareDatabase` interface to the no-arg
    `db.read_patient_data()` call `QualityControlTask` makes, and fills in
    defaults for demo patients with no history on file.
    """

    def __init__(self, db: MockHealthcareDatabase, patient_id: str):
        self._db = db
        self._patient_id = patient_id

    async def read_patient_data(self) -> dict:
        """Return the patient history/allergies used to verify the summary."""
        data = await self._db.read_patient_data(self._patient_id)
        return {
            "history": data.get("history", "No prior history on file."),
            "allergies": data.get("allergies", []),
        }


async def process_medical_conversation_async(conversation: str, patient_id: str = "demo-patient") -> dict:
    """Processes a medical conversation using the healthcare agent task pipeline.

    Runs the conversation through each task in sequence: preprocessing, language
    assessment, clinical extraction, summarization, and quality control (which
    flags whether a human reviewer must sign off before the output is used).

    Use this directly from async callers (e.g. the FastAPI endpoint); use
    `process_medical_conversation` from sync code such as the CLI entry point.

    Args:
        conversation: A string containing the medical conversation to be processed.
        patient_id: The patient to verify the summary against. Defaults to a demo
            patient with no history on file in the mock database.

    Returns:
        A dictionary containing the structured results from each task in the workflow.
    """
    llm = LLMFactory.get_llm_for_task("summarization")
    db = _QualityControlDataSource(MockHealthcareDatabase(), patient_id)
    logger = Logger()

    preprocessed_text = await PreprocessMedicalTextTask().execute(conversation, llm)
    language_assessment = await AssessPatientLanguageTask().execute(preprocessed_text, llm)
    clinical_info = await ExtractClinicalInfoTask().execute(preprocessed_text, llm)
    summary = await GenerateSummaryTask().execute(preprocessed_text, llm)
    quality_check = await QualityControlTask().execute(summary, llm, db, logger)

    return {
        "preprocessed_text": preprocessed_text,
        "language_assessment": language_assessment,
        "clinical_info": clinical_info,
        "summary": summary,
        "quality_check": quality_check,
    }


def process_medical_conversation(conversation: str, patient_id: str = "demo-patient") -> dict:
    """Synchronous wrapper around `process_medical_conversation_async` for CLI/script use.

    Do not call this from within an already-running event loop (e.g. inside a
    FastAPI async endpoint) — `asyncio.run` will raise. Use
    `process_medical_conversation_async` there instead.

    Args:
        conversation: A string containing the medical conversation to be processed.
        patient_id: The patient to verify the summary against.

    Returns:
        A dictionary containing the structured results from each task in the workflow.
    """
    return asyncio.run(process_medical_conversation_async(conversation, patient_id))


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
