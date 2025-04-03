"""Medical tools for healthcare system."""

from typing import Any

from crewai.tools import BaseTool


class MedicalTerminologyTool(BaseTool):
    """Tool for simplifying medical terminology."""

    name: str = "simplify_medical_terms"
    description: str = "Simplify complex medical terminology for patients"

    async def _run(self, text: str) -> str:
        """Run the terminology simplification tool."""
        return f"Simplified: {text}"


class PatientLanguageTool(BaseTool):
    """Tool for assessing patient language proficiency."""

    name: str = "assess_patient_language"
    description: str = "Assess patient language proficiency and needs"

    async def _run(self, conversation: str) -> dict[str, Any]:
        """Run the language assessment tool."""
        return {
            "needs_interpreter": False,
            "proficiency": "intermediate",
            "language_proficiency": "B2"
        }


class ClinicalExtractionTool(BaseTool):
    """Tool for extracting clinical information."""

    name: str = "extract_clinical_info"
    description: str = "Extract clinical information from patient conversations"

    async def _run(self, conversation: str) -> dict[str, Any]:
        """Run the clinical extraction tool."""
        return {
            "symptoms": ["headache"],
            "conditions": ["hypertension"],
            "medications": ["metoprolol"],
            "diagnosis": "Essential hypertension"
        }
