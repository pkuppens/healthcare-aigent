"""Task definitions for healthcare system."""

import json
import logging
from typing import Any

from crewai import Task

logger = logging.getLogger(__name__)


class PreprocessMedicalTextTask(Task):
    """Task for preprocessing medical text."""

    def __init__(self):
        """Initialize the task."""
        super().__init__(
            description="Preprocess medical text for analysis",
            expected_output="Preprocessed medical text",
        )

    async def execute(self, text: str, llm) -> str:
        """Execute the preprocessing task.

        Args:
            text: The medical text to preprocess
            llm: The language model to use for preprocessing

        Returns:
            The preprocessed text

        Raises:
            ValueError: If the input text is empty or invalid
            RuntimeError: If the LLM fails to process the text
        """
        if not text or not isinstance(text, str):
            raise ValueError("Input text must be a non-empty string")

        try:
            prompt = f"""Preprocess this medical text for further analysis.
            Remove any irrelevant information, standardize medical terms,
            and ensure the text is well-structured.

            Text: {text}

            Return only the preprocessed text without any additional comments."""

            result = await llm.ainvoke(prompt)
            if not result or not isinstance(result, str):
                raise RuntimeError("LLM returned invalid response")

            return result.strip()
        except Exception as e:
            logger.error(f"Failed to preprocess medical text: {e}")
            raise RuntimeError(f"Failed to preprocess medical text: {e}") from e


class AssessPatientLanguageTask(Task):
    """Task for assessing patient language proficiency."""

    def __init__(self):
        """Initialize the task."""
        super().__init__(
            description="Assess patient language proficiency",
            expected_output="Language assessment results",
        )

    async def execute(self, text: str, llm) -> dict[str, Any]:
        """Execute the language assessment task.

        Args:
            text: The text to assess for language proficiency
            llm: The language model to use for assessment

        Returns:
            A dictionary containing language assessment results

        Raises:
            ValueError: If the input text is empty or invalid
            RuntimeError: If the LLM fails to assess the text
        """
        if not text or not isinstance(text, str):
            raise ValueError("Input text must be a non-empty string")

        try:
            prompt = f"""Assess the language proficiency in this text.
            Consider grammar, vocabulary, and medical terminology usage.
            Return a JSON object with these fields:
            - proficiency: string (basic, intermediate, advanced)
            - needs_interpreter: boolean
            - language_proficiency: string (CEFR level, e.g., A1, B2, C1)

            Text: {text}

            Return only the JSON object without any additional text."""

            result = await llm.ainvoke(prompt)
            if not result or not isinstance(result, str):
                raise RuntimeError("LLM returned invalid response")

            try:
                assessment = json.loads(result)
                required_keys = {"proficiency", "needs_interpreter", "language_proficiency"}
                if not all(key in assessment for key in required_keys):
                    raise ValueError("Missing required keys in assessment")
                return assessment
            except json.JSONDecodeError as e:
                raise RuntimeError("Failed to parse LLM response as JSON") from e

        except Exception as e:
            logger.error(f"Failed to assess patient language: {e}")
            raise RuntimeError(f"Failed to assess patient language: {e}") from e


class ExtractClinicalInfoTask(Task):
    """Task for extracting clinical information."""

    def __init__(self):
        """Initialize the task."""
        super().__init__(
            description="Extract clinical information from text",
            expected_output="Extracted clinical information",
        )

    async def execute(self, text: str, llm) -> dict[str, Any]:
        """Execute the clinical extraction task.

        Args:
            text: The text to extract clinical information from
            llm: The language model to use for extraction

        Returns:
            A dictionary containing extracted clinical information

        Raises:
            ValueError: If the input text is empty or invalid
            RuntimeError: If the LLM fails to extract information
        """
        if not text or not isinstance(text, str):
            raise ValueError("Input text must be a non-empty string")

        try:
            prompt = f"""Extract clinical information from this text.
            Return a JSON object with these fields:
            - symptoms: list of strings
            - conditions: list of strings
            - medications: list of strings
            - diagnosis: string

            Text: {text}

            Return only the JSON object without any additional text."""

            result = await llm.ainvoke(prompt)
            if not result or not isinstance(result, str):
                raise RuntimeError("LLM returned invalid response")

            try:
                info = json.loads(result)
                required_keys = {"symptoms", "conditions", "medications", "diagnosis"}
                if not all(key in info for key in required_keys):
                    raise ValueError("Missing required keys in clinical info")
                return info
            except json.JSONDecodeError as e:
                raise RuntimeError("Failed to parse LLM response as JSON") from e

        except Exception as e:
            logger.error(f"Failed to extract clinical information: {e}")
            raise RuntimeError(f"Failed to extract clinical information: {e}") from e


class GenerateSummaryTask(Task):
    """Task for generating medical summaries."""

    def __init__(self):
        """Initialize the task."""
        super().__init__(
            description="Generate medical summary",
            expected_output="Medical summary",
        )

    async def execute(self, text: str, llm) -> str:
        """Execute the summarization task.

        Args:
            text: The text to summarize
            llm: The language model to use for summarization

        Returns:
            The generated summary

        Raises:
            ValueError: If the input text is empty or invalid
            RuntimeError: If the LLM fails to generate a summary
        """
        if not text or not isinstance(text, str):
            raise ValueError("Input text must be a non-empty string")

        try:
            prompt = f"""Generate a concise medical summary of this text.
            Focus on key clinical findings, diagnoses, and recommendations.
            Use clear and professional medical language.

            Text: {text}

            Return only the summary without any additional text."""

            result = await llm.ainvoke(prompt)
            if not result or not isinstance(result, str):
                raise RuntimeError("LLM returned invalid response")

            return result.strip()
        except Exception as e:
            logger.error(f"Failed to generate summary: {e}")
            raise RuntimeError(f"Failed to generate summary: {e}") from e


class QualityControlTask(Task):
    """Task for quality control of medical information."""

    def __init__(self):
        """Initialize the task."""
        super().__init__(
            description="Perform quality control on medical information",
            expected_output="Quality control results",
        )

    async def execute(self, text: str, llm, db, logger) -> dict[str, Any]:
        """Execute the quality control task.

        Args:
            text: The text to perform quality control on
            llm: The language model to use for quality control
            db: The database to use for verification
            logger: The logger to use for audit events

        Returns:
            A dictionary containing quality control results

        Raises:
            ValueError: If the input text is empty or invalid
            RuntimeError: If the quality control process fails
        """
        if not text or not isinstance(text, str):
            raise ValueError("Input text must be a non-empty string")

        try:
            # Get patient data for verification
            patient_data = await db.read_patient_data()

            prompt = f"""Perform quality control on this medical text.
            Verify accuracy, completeness, and consistency with patient history.
            Return a JSON object with these fields:
            - accuracy: float (0.0 to 1.0)
            - needs_review: boolean
            - quality_score: integer (0 to 100)

            Text: {text}
            Patient History: {patient_data["history"]}
            Known Allergies: {patient_data["allergies"]}

            Return only the JSON object without any additional text."""

            result = await llm.ainvoke(prompt)
            if not result or not isinstance(result, str):
                raise RuntimeError("LLM returned invalid response")

            try:
                qc_results = json.loads(result)
                required_keys = {"accuracy", "needs_review", "quality_score"}
                if not all(key in qc_results for key in required_keys):
                    raise ValueError("Missing required keys in quality control results")

                # Log the quality control event
                await logger.log_audit_event({"event_type": "quality_control", "text_id": hash(text), "results": qc_results})

                return qc_results
            except json.JSONDecodeError as e:
                raise RuntimeError("Failed to parse LLM response as JSON") from e

        except Exception as e:
            logger.error(f"Failed to perform quality control: {e}")
            raise RuntimeError(f"Failed to perform quality control: {e}") from e
