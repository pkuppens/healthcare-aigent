"""Mock patient data structure with preferences."""

from dataclasses import dataclass


@dataclass
class PatientPreferences:
    """Patient communication preferences."""

    language: str = "nl"
    literacy_level: str = "B1"  # basic, standard, advanced
    medical_terminology: bool = True
    include_explanations: bool = True
    preferred_format: str = "text"  # text, bullet_points, detailed


@dataclass
class PatientRecord:
    """Mock patient record with medical information and preferences."""

    patient_id: str
    name: str
    age: int
    diagnosis: str
    treatment_plan: list[str]
    preferences: PatientPreferences
    notes: str | None = None


# Mock patient database
MOCK_PATIENTS: dict[str, PatientRecord] = {
    "P001": PatientRecord(
        patient_id="P001",
        name="John Smith",
        age=45,
        diagnosis="Type 2 Diabetes",
        treatment_plan=[
            "Metformin 500mg twice daily",
            "Blood glucose monitoring 3 times daily",
            "Low-carb diet",
            "30 minutes daily exercise",
        ],
        preferences=PatientPreferences(
            language="en",
            literacy_level="advanced",
            medical_terminology=True,
            include_explanations=False,
            preferred_format="detailed",
        ),
        notes="Patient has background in healthcare",
    ),
    "P002": PatientRecord(
        patient_id="P002",
        name="Maria Garcia",
        age=62,
        diagnosis="Type 2 Diabetes",
        treatment_plan=[
            "Metformin 500mg twice daily",
            "Blood glucose monitoring 3 times daily",
            "Low-carb diet",
            "30 minutes daily exercise",
        ],
        preferences=PatientPreferences(
            language="es",
            literacy_level="basic",
            medical_terminology=False,
            include_explanations=True,
            preferred_format="bullet_points",
        ),
        notes="Patient prefers Spanish language and simple explanations",
    ),
}
