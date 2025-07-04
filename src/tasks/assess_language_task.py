"""Defines the task for assessing patient language proficiency.

This module contains the AssessPatientLanguageTask class, which is responsible
for analyzing the patient's language to determine proficiency, sentiment, and
potential communication needs.
"""

import json
import logging
from typing import Any

from crewai import Task


logger = logging.getLogger(__name__)


class AssessPatientLanguageTask(Task):
    """A task for assessing patient language proficiency from text.

    This task directs an agent to analyze a piece of text (typically a patient's
    side of a conversation) and evaluate their language skills. The goal is to
    produce a structured assessment that can inform communication strategies.

    Attributes:
        description (str): A brief description of the task's purpose.
        expected_output (str): A description of what the task is expected to return.
    """

    def __init__(self):
        """Initializes the AssessPatientLanguageTask."""
        super().__init__(
            description="Assess the patient's language proficiency, sentiment, and communication needs.",
            expected_output="A structured JSON object with language assessment details.",
        )

    async def execute(self, text: str, llm: any) -> dict[str, Any]:
        """Executes the language assessment task.

        This method prompts the language model to perform a language assessment
        and return the results in a structured JSON format. It includes error
        handling for the LLM interaction and JSON parsing.

        Args:
            text: The text to be assessed for language proficiency.
            llm: The language model instance to be used for the assessment.

        Returns:
            A dictionary containing the structured language assessment.

        Raises:
            ValueError: If the input text is empty or not a string.
            RuntimeError: If the LLM response is invalid, cannot be parsed, or is missing required keys.
        """
        if not text or not isinstance(text, str):
            raise ValueError("Input text must be a non-empty string.")

        try:
            prompt = f'''Assess the language proficiency in this text.
            Consider grammar, vocabulary, and medical terminology usage.
            Return a JSON object with these fields:
            - "proficiency": string (e.g., "basic", "intermediate", "advanced")
            - "needs_interpreter": boolean
            - "language_proficiency_scale": string (e.g., CEFR level like "A1", "B2", "C1")

            Text: """{text}"""

            Return only the JSON object without any additional text or explanations.'''

            result = await llm.ainvoke(prompt)
            if not result or not isinstance(result, str):
                raise RuntimeError("LLM returned an invalid or empty response.")

            try:
                assessment = json.loads(result)
                required_keys = {"proficiency", "needs_interpreter", "language_proficiency_scale"}
                if not all(key in assessment for key in required_keys):
                    raise ValueError(f"LLM response is missing required keys: {required_keys - set(assessment.keys())}")
                return assessment
            except json.JSONDecodeError as e:
                raise RuntimeError(f"Failed to parse LLM response as JSON: {result}") from e

        except Exception as e:
            logger.error(f"Failed to assess patient language: {e}")
            raise RuntimeError(f"An error occurred during language assessment: {e}") from e
