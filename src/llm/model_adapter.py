from typing import Any


class ModelAdapter:
    """Abstract ModelAdapter interface for swappable LLM backends."""

    def load(self, *args, **kwargs) -> None:
        """Load model artifacts / runtime resources."""
        raise NotImplementedError

    def infer(self, prompt: str, **options) -> dict[str, Any]:
        """Run inference given a prompt. Return a dict with at least 'text'."""
        raise NotImplementedError

    def health_check(self) -> bool:
        """Return True if the adapter/runtime is healthy and ready."""
        raise NotImplementedError

    def metadata(self) -> dict[str, Any]:
        """Return adapter metadata (model_id, size, quantized, profile)."""
        raise NotImplementedError
