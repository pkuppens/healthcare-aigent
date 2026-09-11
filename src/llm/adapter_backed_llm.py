"""Adapts a ModelAdapter (src/llm/model_adapter.py) to the BaseLLM interface.

This is the seam where GPUAdapter/EdgeAdapter/MockAdapter connect to
LLMFactory. Without it those adapters exist but nothing outside src/llm/
can ever construct or call one (see issue #8).
"""

from typing import Any

from langchain.callbacks.manager import CallbackManagerForLLMRun

from src.llm.base import BaseLLM
from src.llm.model_adapter import ModelAdapter


class AdapterBackedLLM(BaseLLM):
    """BaseLLM implementation backed by a ModelAdapter (GPU/Edge/Mock)."""

    def __init__(self, adapter: ModelAdapter, model_name: str, temperature: float = 0.7, **kwargs: Any):
        super().__init__(model_name=model_name, temperature=temperature, **kwargs)
        self._adapter = adapter

    def _call(
        self,
        prompt: str,
        stop: list[str] | None = None,
        run_manager: CallbackManagerForLLMRun | None = None,
        **kwargs: Any,
    ) -> str:
        if not self._adapter.health_check():
            self._adapter.load()
        result = self._adapter.infer(prompt, **kwargs)
        return result["text"]

    def _llm_type(self) -> str:
        return f"adapter:{self._adapter.metadata().get('profile', 'unknown')}"

    @property
    def provider(self) -> str:
        return self._adapter.metadata().get("profile", "adapter")
