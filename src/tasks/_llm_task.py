"""Shared LLM-call sequence for the task pipeline.

Every task in this package follows the same shape: validate the input text,
call the LLM with a prompt, validate the response, and (for most tasks)
parse it as JSON against a set of required keys. This module centralizes
that sequence so each task configures it with a prompt and required keys
instead of re-implementing validate/call/parse/wrap from scratch.
"""

import json
import logging
from typing import Any


logger = logging.getLogger(__name__)


def require_text(text: str) -> None:
    """Raise ValueError unless `text` is a non-empty string."""
    if not text or not isinstance(text, str):
        raise ValueError("Input text must be a non-empty string.")


async def run_llm_text(llm: Any, prompt: str, action: str) -> str:
    """Call `llm.ainvoke(prompt)`, validate the response, and return it.

    Any failure (the LLM call itself, or an empty/non-string response) is
    wrapped as a RuntimeError describing `action`, so every task in the
    pipeline fails the same way instead of each reimplementing its own
    try/except around the LLM call.
    """
    try:
        result = await llm.ainvoke(prompt)
        if not result or not isinstance(result, str):
            raise RuntimeError("LLM returned an invalid or empty response.")
        return result.strip()
    except Exception as e:
        logger.error(f"Failed to {action}: {e}")
        raise RuntimeError(f"An error occurred during {action}: {e}") from e


async def run_llm_json(llm: Any, prompt: str, required_keys: set[str], action: str) -> dict[str, Any]:
    """Like `run_llm_text`, but parses the response as JSON and checks `required_keys`."""
    raw = await run_llm_text(llm, prompt, action)

    try:
        data = json.loads(raw)
    except json.JSONDecodeError as e:
        logger.error(f"Failed to {action}: could not parse LLM response as JSON")
        raise RuntimeError(f"An error occurred during {action}: failed to parse LLM response as JSON: {raw}") from e

    missing = required_keys - set(data.keys())
    if missing:
        logger.error(f"Failed to {action}: LLM response missing required keys: {missing}")
        raise RuntimeError(f"An error occurred during {action}: LLM response is missing required keys: {missing}")

    return data
