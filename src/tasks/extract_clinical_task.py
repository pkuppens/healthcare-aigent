"""Defines the task for extracting structured clinical information.

This module contains the ExtractClinicalInfoTask class, which is designed
to parse medical conversations and extract key clinical entities like
symptoms, conditions, and medications.
"""

import json
import logging
from typing import Any

from crewai import Task


logger = logging.getLogger(__name__)


class ExtractClinicalInfoTask(Task):
    """A task for extracting structured clinical information from text.

    This task instructs an agent to identify and pull out key clinical data
    from a piece of text. The output is a structured JSON object, making it
    easy to use for record-keeping or further analysis.

    Attributes:
        description (str): A brief description of the task's purpose.
        expected_output (str): A description of what the task is expected to return.
    """

    def __init__(self):
        """Initializes the ExtractClinicalInfoTask."""
        super().__init__(
            description="Extract key clinical information (symptoms, medications, etc.) from the conversation.",
            expected_output="A structured JSON object containing the extracted clinical data.",
        )

    async def execute(self, text: str, llm: any) -> dict[str, Any]:
        """Executes the clinical information extraction task.

        This method uses a language model to parse the text and extract
        pre-defined clinical fields. It ensures the output is a valid JSON
        object with all the required keys.

        Args:
            text: The medical text to extract information from.
            llm: The language model instance to be used for extraction.

        Returns:
            A dictionary containing the structured clinical information.

        Raises:
            ValueError: If the input text is empty or not a string.
            RuntimeError: If the LLM response is invalid, cannot be parsed, or is missing required keys.
        """
        if not text or not isinstance(text, str):
            raise ValueError("Input text must be a non-empty string.")

        try:
            prompt = f'''Extract clinical information from this text.
            Return a JSON object with these fields:
            - "symptoms": list of strings
            - "conditions": list of strings
            - "medications": list of strings
            - "diagnosis": string

            Text: """{text}"""

            Return only the JSON object without any additional text or explanations.'''

            result = await llm.ainvoke(prompt)
            if not result or not isinstance(result, str):
                raise RuntimeError("LLM returned an invalid or empty response.")

            try:
                info = json.loads(result)
                required_keys = {"symptoms", "conditions", "medications", "diagnosis"}
                if not all(key in info for key in required_keys):
                    raise ValueError(f"LLM response is missing required keys: {required_keys - set(info.keys())}")
                return info
            except json.JSONDecodeError as e:
                raise RuntimeError(f"Failed to parse LLM response as JSON: {result}") from e

        except Exception as e:
            logger.error(f"Failed to extract clinical information: {e}")
            raise RuntimeError(f"An error occurred during clinical information extraction: {e}") from e
