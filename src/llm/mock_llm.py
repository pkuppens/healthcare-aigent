"""Test double LLM: no runtime, echoes the prompt. Selected via the `mock` profile."""

from typing import Any

from langchain_core.callbacks import CallbackManagerForLLMRun

from src.llm.base import BaseLLM


class MockLLM(BaseLLM):
    """BaseLLM that returns `[mock] <prompt>` without calling any model."""

    def __init__(self, model_name: str = "mock-model", temperature: float = 0.7, **kwargs: Any):
        super().__init__(model_name=model_name, temperature=temperature, **kwargs)

    def _call(
        self,
        prompt: str,
        stop: list[str] | None = None,
        run_manager: CallbackManagerForLLMRun | None = None,
        **kwargs: Any,
    ) -> str:
        return f"[mock] {prompt[:200]}"

    def _llm_type(self) -> str:
        return "mock"

    @property
    def provider(self) -> str:
        return "mock"
