"""Defines the FastAPI server for the healthcare AI agent system.

This module creates a FastAPI application that exposes an endpoint for
processing medical conversations. It serves as the API gateway for the system.
"""

import tempfile
from pathlib import Path

from fastapi import FastAPI, UploadFile
from pydantic import BaseModel

from src.main import process_audio_conversation_async, process_medical_conversation_async


app = FastAPI(
    title="Healthcare AI Agent API",
    description="An API for processing medical conversations with a multi-agent system.",
    version="0.1.0",
)


class ConversationRequest(BaseModel):
    """Request model for a medical conversation."""

    text: str


@app.post("/process_conversation/", summary="Process a medical conversation")
async def process_conversation_endpoint(request: ConversationRequest) -> dict:
    """Processes a medical conversation and returns the structured results.

    This endpoint takes a raw medical conversation as input, processes it
    through the multi-agent crew, and returns a dictionary containing the
    structured analysis from each agent.

    Args:
        request: A request object containing the conversation text.

    Returns:
        A dictionary with the processed results.

    Example:
        Request Body:
        ```json
        {
            "text": "Doctor: Good morning. Patient: I have a bad headache."
        }
        ```

        Response Body:
        ```json
        {
            "preprocessed_text": "Patient has a bad headache.",
            "language_assessment": {
                "proficiency": "intermediate",
                "needs_interpreter": false,
                "language_proficiency_scale": "B1"
            },
            "clinical_info": {
                "symptoms": ["headache"],
                "conditions": [],
                "medications": [],
                "diagnosis": "Headache"
            },
            "summary": "The patient reports a primary symptom of a bad headache.",
            "quality_check": {
                "accuracy_score": 0.95,
                "requires_human_review": false,
                "quality_rating": 95
            }
        }
        ```
    """
    return await process_medical_conversation_async(request.text)


@app.post("/transcribe_and_process/", summary="Transcribe a recorded consultation and process it")
async def transcribe_and_process_endpoint(audio: UploadFile, language: str = "nl") -> dict:
    """Transcribes an uploaded consultation recording and runs it through the pipeline.

    This is the entry point that matches the real GGZ workflow: a recorded
    consult in, a structured concept report out — still gated by
    `quality_check.requires_human_review` before it can be used.

    Note: this is a showcase implementation. Audio is written to a local temp
    file and sent to whichever transcription provider is configured (OpenAI's
    Whisper API by default — see `TRANSCRIPTION_PROVIDER` in
    `src/transcription/factory.py` for how to change it); none of the
    supported providers today are routed through a signed
    subverwerkersovereenkomst, so this must not be used with real patient
    data regardless of provider. See docs/agents/domain.md for the
    compliance context.

    Args:
        audio: The uploaded audio file (recorded consultation).
        language: ISO 639-1 language hint for the transcriber (default "nl").

    Returns:
        A dictionary with the transcript plus the same structured results as
        `/process_conversation/`.
    """
    suffix = Path(audio.filename or "").suffix or ".wav"
    with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp:
        tmp.write(await audio.read())
        tmp_path = tmp.name

    try:
        return await process_audio_conversation_async(tmp_path, language=language)
    finally:
        Path(tmp_path).unlink(missing_ok=True)
