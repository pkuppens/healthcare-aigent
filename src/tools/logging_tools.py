"""Logging tools for healthcare system."""

from datetime import datetime
from typing import Any


class Logger:
    """Logger for healthcare system."""

    async def log_audit_event(self, event: dict[str, Any]) -> bool:
        """Log an audit event.

        Args:
            event: Event data to log

        Returns:
            True if logging was successful
        """
        return True


async def log_audit_event(event_type: str, patient_id: str, user_id: str, logger: Logger) -> bool:
    """Log an audit event.

    Args:
        event_type: Type of event
        patient_id: ID of the patient
        user_id: ID of the user
        logger: Logger instance

    Returns:
        True if logging was successful
    """
    event = {"timestamp": datetime.now().isoformat(), "event_type": event_type, "patient_id": patient_id, "user_id": user_id}
    return await logger.log_audit_event(event)
