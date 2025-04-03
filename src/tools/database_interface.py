"""Database interface for healthcare systems."""

from abc import ABC, abstractmethod


class HealthcareDatabase(ABC):
    """Abstract base class for healthcare database operations."""

    @abstractmethod
    async def read_patient_data(self, patient_id: str) -> dict[str, object]:
        """Read patient data from the database.

        Args:
            patient_id: The ID of the patient

        Returns:
            Dictionary containing patient data
        """
        pass

    @abstractmethod
    async def update_patient_data(self, patient_id: str, update_data: dict[str, object]) -> bool:
        """Update patient data in the database.

        Args:
            patient_id: The ID of the patient
            update_data: Dictionary containing data to update

        Returns:
            True if update was successful, False otherwise
        """
        pass

    @abstractmethod
    async def log_audit_event(
        self,
        event_type: str,
        patient_id: str,
        user_id: str,
        details: dict[str, object] | None = None,
    ) -> bool:
        """Log an audit event for healthcare operations.

        Args:
            event_type: Type of event being logged
            patient_id: ID of the patient involved
            user_id: ID of the user performing the action
            details: Optional additional details about the event

        Returns:
            True if logging was successful, False otherwise
        """
        pass
