"""Defines the FastAPI server for the healthcare AI agent system.

This module creates a FastAPI application that exposes an endpoint for
processing medical conversations. It serves as the API gateway for the system.
"""

from fastapi import FastAPI
from pydantic import BaseModel

from src.main import process_medical_conversation


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
    """
    return process_medical_conversation(request.text)
