"""Defines the task for quality control of medical information.

This module contains the QualityControlTask class, which is responsible for
verifying the accuracy and completeness of the processed medical information
against patient history and other data.
"""

import json
import logging
from typing import Any

from crewai import Task


logger = logging.getLogger(__name__)


class QualityControlTask(Task):
    """A task for performing quality control on processed medical information.

    This task instructs an agent to review a given medical text and compare it
    against known patient data to ensure accuracy, completeness, and consistency.
    It produces a structured quality score and logs an audit event.

    Attributes:
        description (str): A brief description of the task's purpose.
        expected_output (str): A description of what the task is expected to return.
    """

    def __init__(self):
        """Initializes the QualityControlTask."""
        super().__init__(
            description="Perform quality control on the processed medical information.",
            expected_output="A structured JSON object with quality control metrics.",
        )

    async def execute(self, text: str, llm: any, db: any, logger: any) -> dict[str, Any]:
        """Executes the quality control task.

        This method prompts a language model to perform a quality check on the
        text, using additional patient data for verification. It ensures the
        output is a valid JSON object and logs the results.

        Args:
            text: The medical text to perform quality control on.
            llm: The language model instance to be used for quality control.
            db: The database interface to use for retrieving patient data.
            logger: The logger instance to use for logging audit events.

        Returns:
            A dictionary containing the structured quality control results.

        Raises:
            ValueError: If the input text is empty or not a string.
            RuntimeError: If the quality control process fails, the LLM response is invalid,
                          or the database/logging fails.
        """
        if not text or not isinstance(text, str):
            raise ValueError("Input text must be a non-empty string.")

        try:
            # Get patient data for verification
            patient_data = await db.read_patient_data()

            prompt = f'''Perform quality control on this medical text.
            Verify its accuracy, completeness, and consistency against the patient's history.
            Return a JSON object with these fields:
            - "accuracy_score": float (a score from 0.0 to 1.0 representing factual accuracy)
            - "requires_human_review": boolean (true if a human needs to review it)
            - "quality_rating": integer (an overall quality rating from 0 to 100)

            Text: """{text}"""
            Patient History: """{patient_data["history"]}"""
            Known Allergies: """{patient_data["allergies"]}"""

            Return only the JSON object without any additional text or explanations.'''

            result = await llm.ainvoke(prompt)
            if not result or not isinstance(result, str):
                raise RuntimeError("LLM returned an invalid or empty response.")

            try:
                qc_results = json.loads(result)
                required_keys = {"accuracy_score", "requires_human_review", "quality_rating"}
                if not all(key in qc_results for key in required_keys):
                    raise ValueError(f"LLM response is missing required keys: {required_keys - set(qc_results.keys())}")

                # Log the quality control event
                await logger.log_audit_event({"event_type": "quality_control", "text_id": hash(text), "results": qc_results})

                return qc_results
            except json.JSONDecodeError as e:
                raise RuntimeError(f"Failed to parse LLM response as JSON: {result}") from e

        except Exception as e:
            logger.error(f"Failed to perform quality control: {e}")
            raise RuntimeError(f"An error occurred during quality control: {e}") from e
