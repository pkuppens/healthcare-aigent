"""Defines the task for generating a medical summary.

This module contains the GenerateSummaryTask class, which is responsible for
creating a concise and accurate summary of a medical conversation.
"""

from crewai import Task

from src.tasks._llm_task import require_text, run_llm_text


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

        Args:
            text: The medical text to be summarized.
            llm: The language model instance to be used for summarization.

        Returns:
            The generated medical summary as a string.

        Raises:
            ValueError: If the input text is empty or not a string.
            RuntimeError: If the language model fails to generate a summary or returns an invalid response.
        """
        require_text(text)

        prompt = f'''Generate a concise medical summary of this text.
        Focus on key clinical findings, diagnoses, and recommendations.
        Use clear and professional medical language.

        Text: """{text}"""

        Return only the summary without any additional text or explanations.'''

        return await run_llm_text(llm, prompt, action="summary generation")
