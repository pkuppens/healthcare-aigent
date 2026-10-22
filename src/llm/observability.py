"""Optional Langfuse tracing for LLM calls (issues #12, #13), PII-masked before export (#16).

Everything here is default-off: with `LANGFUSE_ENABLED` unset, `get_langfuse_client()`
returns None, `observe_llm_call()` just runs the call, and the `langfuse` package is never
imported (it lives in the optional `observability` extra). See docs/langfuse.md.
"""

import logging
from collections.abc import Callable
from typing import TYPE_CHECKING, Any

from src.llm.config import ConfigManager
from src.privacy.pii import mask_pii_data


if TYPE_CHECKING:
    from src.llm.base import BaseLLM


logger = logging.getLogger(__name__)

_client: Any | None = None
_client_initialised = False
_last_trace_id: str | None = None


def get_langfuse_client() -> Any | None:
    """Return a shared Langfuse client, or None when tracing is disabled or unavailable.

    None is returned (never raised) when Langfuse is disabled, its keys are missing, the
    `langfuse` package is not installed, or the client fails to construct. The result is
    cached for the process; call `reset_langfuse_client()` to re-read the config.
    """
    global _client, _client_initialised
    if _client_initialised:
        return _client
    _client_initialised = True

    config = ConfigManager().get_config().langfuse
    if not config.enabled:
        return None
    if not config.public_key or not config.secret_key:
        logger.warning("LANGFUSE_ENABLED is true but LANGFUSE_PUBLIC_KEY/LANGFUSE_SECRET_KEY are not set; tracing disabled")
        return None

    try:
        from langfuse import Langfuse
    except ImportError:
        logger.warning("LANGFUSE_ENABLED is true but langfuse is not installed (uv sync --extra observability); tracing disabled")
        return None

    try:
        _client = Langfuse(
            public_key=config.public_key,
            secret_key=config.secret_key,
            host=config.host,
            sample_rate=config.sample_rate,
            debug=config.debug,
            mask=langfuse_mask if config.mask_pii else None,
        )
    except Exception as e:
        logger.warning(f"Failed to initialise Langfuse client, tracing disabled: {e}")
        _client = None
    return _client


def langfuse_mask(*, data: Any, **kwargs: Any) -> Any:
    """Langfuse `mask` callback: scrub PII from every observation's input, output and metadata (#16)."""
    return mask_pii_data(data)


def reset_langfuse_client() -> None:
    """Forget the cached client so the next `get_langfuse_client()` re-reads the config."""
    global _client, _client_initialised, _last_trace_id
    _client = None
    _client_initialised = False
    _last_trace_id = None


def get_last_trace_id() -> str | None:
    """Return the trace id of the most recent traced LLM call in this process, if any."""
    return _last_trace_id


def observe_llm_call(llm: "BaseLLM", prompt: str, call: Callable[[], str]) -> str:
    """Run `call()` and, when Langfuse is enabled, record it as a generation.

    The generation carries the model, provider, temperature, prompt, completion and token
    usage (taken from `llm.last_usage`, which providers fill from their API response).
    """
    global _last_trace_id
    client = get_langfuse_client()
    if client is None:
        return call()

    with client.start_as_current_observation(
        as_type="generation",
        name=f"{llm.provider}.generate",
        model=llm.model_name,
        model_parameters={"temperature": llm.temperature},
        input=prompt,
        metadata={"provider": llm.provider},
    ) as generation:
        _last_trace_id = generation.trace_id
        try:
            output = call()
        except Exception as e:
            generation.update(level="ERROR", status_message=str(e))
            raise
        usage = llm.last_usage
        generation.update(
            output=output,
            usage_details={"input": usage["input_tokens"], "output": usage["output_tokens"]} if usage else None,
        )
        return output
