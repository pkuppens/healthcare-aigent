"""Defines the task for generating a medical summary.

This module contains the GenerateSummaryTask class, which is responsible for
creating a concise and accurate summary of a medical conversation.
"""

import logging

from crewai import Task


logger = logging.getLogger(__name__)


class GenerateSummaryTask(Task):
    """A task for generating a medical summary from text.

    This task directs an agent to synthesize the key information from a medical
    text into a clear and professional summary. The summary is intended to be
    useful for clinical documentation and patient handoffs.

    Attributes:
        description (str): A brief description of the task's purpose.
        expected_output (str): A description of what the task is expected to return.
    """

    def __init__(self):
        """Initializes the GenerateSummaryTask."""
        super().__init__(
            description="Generate a concise, professional medical summary of the conversation.",
            expected_output="A well-structured string containing the medical summary.",
        )

    async def execute(self, text: str, llm: any) -> str:
        """Executes the summarization task.

        This method prompts a language model to generate a summary of the provided
        text, focusing on clinical relevance and clarity.

        Args:
            text: The medical text to be summarized.
            llm: The language model instance to be used for summarization.

        Returns:
            The generated medical summary as a string.

        Raises:
            ValueError: If the input text is empty or not a string.
            RuntimeError: If the language model fails to generate a summary or returns an invalid response.
        """
        if not text or not isinstance(text, str):
            raise ValueError("Input text must be a non-empty string.")

        try:
            prompt = f'''Generate a concise medical summary of this text.
            Focus on key clinical findings, diagnoses, and recommendations.
            Use clear and professional medical language.

            Text: """{text}"""

            Return only the summary without any additional text or explanations.'''

            result = await llm.ainvoke(prompt)
            if not result or not isinstance(result, str):
                raise RuntimeError("LLM returned an invalid or empty response.")

            return result.strip()
        except Exception as e:
            logger.error(f"Failed to generate summary: {e}")
            raise RuntimeError(f"An error occurred during summary generation: {e}") from e
