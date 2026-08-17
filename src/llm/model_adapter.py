from abc import ABC, abstractmethod
from typing import Any


class ModelAdapter(ABC):
    """Abstract ModelAdapter interface for swappable LLM backends."""

    @abstractmethod
    def load(self, *args, **kwargs) -> None:
        """Load model artifacts / runtime resources."""

    @abstractmethod
    def infer(self, prompt: str, **options) -> dict[str, Any]:
        """Run inference given a prompt. Return a dict with at least 'text'."""

    @abstractmethod
    def health_check(self) -> bool:
        """Return True if the adapter/runtime is healthy and ready."""

    @abstractmethod
    def metadata(self) -> dict[str, Any]:
        """Return adapter metadata (model_id, size, quantized, profile)."""
