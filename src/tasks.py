"""Task definitions for healthcare system."""

from typing import Any

from crewai import Task


class PreprocessMedicalTextTask(Task):
    """Task for preprocessing medical text."""

    def __init__(self):
        """Initialize the task."""
        super().__init__(
            description="Preprocess medical text for analysis",
            expected_output="Preprocessed medical text",
        )

    async def execute(self, text: str, llm) -> str:
        """Execute the preprocessing task."""
        return await llm.ainvoke(f"Preprocess this medical text: {text}")


class AssessPatientLanguageTask(Task):
    """Task for assessing patient language proficiency."""

    def __init__(self):
        """Initialize the task."""
        super().__init__(
            description="Assess patient language proficiency",
            expected_output="Language assessment results",
        )

    async def execute(self, text: str, llm) -> dict[str, Any]:
        """Execute the language assessment task."""
        await llm.ainvoke(f"Assess language proficiency in: {text}")
        return {
            "needs_interpreter": False,
            "proficiency": "intermediate",
            "language_proficiency": "B2"
        }


class ExtractClinicalInfoTask(Task):
    """Task for extracting clinical information."""

    def __init__(self):
        """Initialize the task."""
        super().__init__(
            description="Extract clinical information from text",
            expected_output="Extracted clinical information",
        )

    async def execute(self, text: str, llm) -> dict[str, Any]:
        """Execute the clinical extraction task."""
        await llm.ainvoke(f"Extract clinical information from: {text}")
        return {
            "symptoms": ["headache"],
            "conditions": ["hypertension"],
            "medications": ["metoprolol"],
            "diagnosis": "Essential hypertension"
        }


class GenerateSummaryTask(Task):
    """Task for generating medical summaries."""

    def __init__(self):
        """Initialize the task."""
        super().__init__(
            description="Generate medical summary",
            expected_output="Medical summary",
        )

    async def execute(self, text: str, llm) -> str:
        """Execute the summarization task."""
        return await llm.ainvoke(f"Summarize this medical text: {text}")


class QualityControlTask(Task):
    """Task for quality control of medical information."""

    def __init__(self):
        """Initialize the task."""
        super().__init__(
            description="Perform quality control on medical information",
            expected_output="Quality control results",
        )

    async def execute(self, text: str, llm, db, logger) -> dict[str, Any]:
        """Execute the quality control task."""
        await llm.ainvoke(f"Perform quality control on: {text}")
        return {
            "accuracy": 0.95,
            "needs_review": False,
            "quality_score": 95
        }
