"""Defines the task for preprocessing medical text.

This module contains the PreprocessMedicalTextTask class, which is responsible
for taking raw medical conversation text and preparing it for further analysis
by standardizing terminology and structure.
"""

from crewai import Task

from src.tasks._llm_task import require_text, run_llm_text


class PreprocessMedicalTextTask(Task):
    """A task for preprocessing medical text for analysis.

    This task instructs an agent to clean and structure raw medical text.
    It aims to remove irrelevant information, standardize medical terms, and
    format the text in a way that is optimal for downstream AI tasks.

    Attributes:
        description (str): A brief description of the task's purpose.
        expected_output (str): A description of what the task is expected to return.
    """

    def __init__(self):
        """Initializes the PreprocessMedicalTextTask."""
        super().__init__(
            description="Preprocess medical text for analysis, standardizing terms and structure.",
            expected_output="Clean, well-structured medical text ready for further processing.",
        )

    async def execute(self, text: str, llm: any) -> str:
        """Executes the preprocessing task.

        Args:
            text: The raw medical text to be preprocessed.
            llm: The language model instance to be used for the task.

        Returns:
            The preprocessed and cleaned medical text as a string.

        Raises:
            ValueError: If the input text is empty or not a string.
            RuntimeError: If the language model fails to process the text or returns an invalid response.
        """
        require_text(text)

        prompt = f'''Preprocess this medical text for further analysis.
        Remove any irrelevant information, standardize medical terms,
        and ensure the text is well-structured.

        Text: """{text}"""

        Return only the preprocessed text without any additional comments or explanations.'''

        return await run_llm_text(llm, prompt, action="medical text preprocessing")
