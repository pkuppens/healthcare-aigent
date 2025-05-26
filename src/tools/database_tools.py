"""Database tools for healthcare system."""

from typing import Any

from src.tools.database_interface import HealthcareDatabase


# Mock patient database
MOCK_PATIENT_DB = {
    "patient_123": {
        "history": "Bekend met hypertensie en diabetes type 2.",
        "allergies": ["penicilline", "aspirine"],
        "medications": ["metoprolol", "metformine"],
        "last_visit": "2024-01-15",
    },
    "patient_456": {
        "history": "Gezonde volwassene, regelmatige controle.",
        "allergies": [],
        "medications": [],
        "last_visit": "2024-02-01",
    },
}


async def read_patient_data(patient_id: str, db: HealthcareDatabase) -> dict[str, Any]:
    """Read patient data from the database.

    Args:
        patient_id: ID of the patient
        db: Database instance

    Returns:
        Patient data dictionary
    """
    return await db.get_patient_data(patient_id)


async def propose_database_update(patient_id: str, data: dict[str, Any], db: HealthcareDatabase) -> bool:
    """Propose an update to patient data.

    Args:
        patient_id: ID of the patient
        data: Data to update
        db: Database instance

    Returns:
        True if update was successful
    """
    return await db.update_patient_data(patient_id, data)
