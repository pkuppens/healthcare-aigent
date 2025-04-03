"""Logging tools for healthcare system."""

from datetime import datetime


async def log_audit_event(
    event_type: str,
    patient_id: str,
    user_id: str,
    logger: object,
) -> bool:
    """Log an audit event.

    Args:
        event_type: Type of event being logged
        patient_id: ID of the patient involved
        user_id: ID of the user performing the action
        logger: Logger instance to use

    Returns:
        True if logging was successful, False otherwise
    """
    event = {
        "timestamp": datetime.now().isoformat(),
        "event_type": event_type,
        "patient_id": patient_id,
        "user_id": user_id,
    }
    await logger.log(event)
    return True
