"""Defines the task for extracting structured clinical information.

This module contains the ExtractClinicalInfoTask class, which is designed
to parse medical conversations and extract key clinical entities like
symptoms, conditions, and medications.
"""

from typing import Any

from crewai import Task

from src.tasks._llm_task import require_text, run_llm_json


REQUIRED_KEYS = {"symptoms", "conditions", "medications", "diagnosis"}


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

        Args:
            text: The medical text to extract information from.
            llm: The language model instance to be used for extraction.

        Returns:
            A dictionary containing the structured clinical information.

        Raises:
            ValueError: If the input text is empty or not a string.
            RuntimeError: If the LLM response is invalid, cannot be parsed, or is missing required keys.
        """
        require_text(text)

        prompt = f'''Extract clinical information from this text.
        Return a JSON object with these fields:
        - "symptoms": list of strings
        - "conditions": list of strings
        - "medications": list of strings
        - "diagnosis": string

        Text: """{text}"""

        Return only the JSON object without any additional text or explanations.'''

        return await run_llm_json(llm, prompt, REQUIRED_KEYS, action="clinical information extraction")
