"""Logging tools for the healthcare multi-agent system."""

from datetime import datetime
from typing import Any

from crewai_tools import tool


@tool("Audit Logging Tool")
def log_audit_event(event_description: str, agent_name: str, data: dict[str, Any] | None = None) -> str:
    """Log important events or decisions for audit purposes.

    Args:
        event_description (str): Description of the event
        agent_name (str): Name of the agent performing the action
        data (Optional[Dict[str, Any]]): Additional data to log

    Returns:
        str: Confirmation message
    """
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    data_str = str(data) if data else "N/A"

    log_entry = f"{timestamp} [AUDIT] Agent: {agent_name} - " f"Event: {event_description} - " f"Data: {data_str}"

    print(log_entry)
    return f"Event '{event_description}' gelogd."
