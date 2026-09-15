"""Defines the task for assessing patient language proficiency.

This module contains the AssessPatientLanguageTask class, which is responsible
for analyzing the patient's language to determine proficiency, sentiment, and
potential communication needs.
"""

from typing import Any

from crewai import Task

from src.tasks._llm_task import require_text, run_llm_json


REQUIRED_KEYS = {"proficiency", "needs_interpreter", "language_proficiency_scale"}


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

        Args:
            text: The text to be assessed for language proficiency.
            llm: The language model instance to be used for the assessment.

        Returns:
            A dictionary containing the structured language assessment.

        Raises:
            ValueError: If the input text is empty or not a string.
            RuntimeError: If the LLM response is invalid, cannot be parsed, or is missing required keys.
        """
        require_text(text)

        prompt = f'''Assess the language proficiency in this text.
        Consider grammar, vocabulary, and medical terminology usage.
        Return a JSON object with these fields:
        - "proficiency": string (e.g., "basic", "intermediate", "advanced")
        - "needs_interpreter": boolean
        - "language_proficiency_scale": string (e.g., CEFR level like "A1", "B2", "C1")

        Text: """{text}"""

        Return only the JSON object without any additional text or explanations.'''

        return await run_llm_json(llm, prompt, REQUIRED_KEYS, action="language assessment")
