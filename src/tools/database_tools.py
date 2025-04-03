"""Mocked database tools for the healthcare multi-agent system."""

from typing import Any

from crewai_tools import tool

# Mock patient database
MOCK_PATIENT_DB: dict[str, dict[str, Any]] = {
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


@tool("Mocked Patient Database Reader")
def read_patient_data(patient_id: str) -> str:
    """Read mocked patient data based on ID.

    Args:
        patient_id (str): Patient identifier

    Returns:
        str: Formatted patient information or 'not found' message
    """
    if patient_id in MOCK_PATIENT_DB:
        patient_data = MOCK_PATIENT_DB[patient_id]
        return (
            f"Patient {patient_id}:\n"
            f"Medische historie: {patient_data['history']}\n"
            f"Allergieën: {', '.join(patient_data['allergies']) if patient_data['allergies'] else 'Geen'}\n"
            f"Medicatie: {', '.join(patient_data['medications']) if patient_data['medications'] else 'Geen'}\n"
            f"Laatste bezoek: {patient_data['last_visit']}"
        )
    return f"Patient {patient_id} niet gevonden in de database."


@tool("Mocked Database Update Proposer")
def propose_database_update(patient_id: str, update_data: dict[str, Any]) -> str:
    """Simulate proposing an EPD update. Does not actually write data.

    Args:
        patient_id (str): Patient identifier
        update_data (Dict[str, Any]): Proposed update data

    Returns:
        str: Confirmation message
    """
    print(f"[AUDIT/MOCK_WRITE] Voorstel voor update EPD voor patient {patient_id}: {update_data}")
    return f"Update voorstel voor {patient_id} gelogd voor review."
