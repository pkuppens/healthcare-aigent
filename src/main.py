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
from src.transcription.base import TranscriptionService


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


async def process_audio_conversation_async(
    audio_path: str,
    transcription_service: TranscriptionService | None = None,
    patient_id: str = "demo-patient",
    language: str | None = "nl",
) -> dict:
    """Transcribes a recorded consultation, then runs it through the task pipeline.

    This is the entry point closest to the real GGZ use case: a recorded
    consult goes in, a structured concept report (still requiring human
    review — see `quality_check.requires_human_review`) comes out.

    Args:
        audio_path: Path to the recorded consultation audio file.
        transcription_service: The provider to transcribe with. Defaults to
            `OpenAIWhisperTranscription` (requires OPENAI_API_KEY).
        patient_id: The patient to verify the summary against.
        language: Optional ISO 639-1 language hint passed to the transcriber.

    Returns:
        A dictionary with the transcript plus the same structured results as
        `process_medical_conversation_async`.
    """
    if transcription_service is None:
        from src.transcription.openai_whisper import OpenAIWhisperTranscription

        transcription_service = OpenAIWhisperTranscription()

    transcript = await transcription_service.transcribe(audio_path, language=language)
    result = await process_medical_conversation_async(transcript, patient_id)
    return {"transcript": transcript, **result}


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
