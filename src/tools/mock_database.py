"""Mock database implementation for testing."""

from datetime import datetime

from src.tools.database_interface import HealthcareDatabase


class MockHealthcareDatabase(HealthcareDatabase):
    """Mock implementation of healthcare database for testing."""

    def __init__(self):
        """Initialize the mock database."""
        self._patient_data = {}
        self._audit_log = []

    async def read_patient_data(self, patient_id: str) -> dict[str, object]:
        """Read patient data from mock database.

        Args:
            patient_id: The ID of the patient

        Returns:
            Dictionary containing patient data
        """
        if patient_id in self._patient_data:
            return self._patient_data[patient_id]
        return {}

    async def update_patient_data(self, patient_id: str, update_data: dict[str, object]) -> bool:
        """Update patient data in mock database.

        Args:
            patient_id: The ID of the patient
            update_data: Dictionary containing data to update

        Returns:
            True if update was successful, False otherwise
        """
        if patient_id in self._patient_data:
            self._patient_data[patient_id].update(update_data)
        else:
            self._patient_data[patient_id] = update_data
        return True

    async def log_audit_event(
        self,
        event_type: str,
        patient_id: str,
        user_id: str,
        details: dict[str, object] | None = None,
    ) -> bool:
        """Log audit event in mock database.

        Args:
            event_type: Type of event being logged
            patient_id: ID of the patient involved
            user_id: ID of the user performing the action
            details: Optional additional details about the event

        Returns:
            True if logging was successful, False otherwise
        """
        event = {
            "timestamp": datetime.now().isoformat(),
            "event_type": event_type,
            "patient_id": patient_id,
            "user_id": user_id,
        }
        if details:
            event["details"] = details
        self._audit_log.append(event)
        return True

    def get_audit_log(self) -> list:
        """Get the audit log for testing."""
        return self._audit_log
