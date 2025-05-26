"""Custom LangFlow component for loading patient data."""

from langflow import CustomComponent
from langflow.field_typing import NestedDict

from src.langflow_poc.patient_data import MOCK_PATIENTS, PatientRecord


class PatientLoader(CustomComponent):
    """Custom component for loading patient data based on patient ID."""

    display_name: str = "Patient Data Loader"
    description: str = "Loads patient data and preferences from the mock database"

    def build_config(self):
        """Build the component configuration."""
        return {
            "patient_id": {
                "display_name": "Patient ID",
                "type": "str",
                "required": True,
                "description": "The ID of the patient to load",
            }
        }

    def build(
        self,
        patient_id: str,
    ) -> NestedDict:
        """Build the component with the given configuration."""
        if patient_id not in MOCK_PATIENTS:
            raise ValueError(f"Patient ID {patient_id} not found in database")

        patient: PatientRecord = MOCK_PATIENTS[patient_id]

        return {
            "patient_data": {
                "id": patient.patient_id,
                "name": patient.name,
                "age": patient.age,
                "diagnosis": patient.diagnosis,
                "treatment_plan": patient.treatment_plan,
                "preferences": {
                    "language": patient.preferences.language,
                    "literacy_level": patient.preferences.literacy_level,
                    "medical_terminology": patient.preferences.medical_terminology,
                    "include_explanations": patient.preferences.include_explanations,
                    "preferred_format": patient.preferences.preferred_format,
                },
                "notes": patient.notes,
            }
        }
