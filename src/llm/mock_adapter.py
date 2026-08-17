from typing import Any

from .model_adapter import ModelAdapter


class MockAdapter(ModelAdapter):
    """Test double implementing the ModelAdapter interface with no real backend.

    Selected explicitly (profile="mock") rather than branched into from
    inside GPUAdapter/EdgeAdapter production code, so a "was this ever really
    called" gap (e.g. a skipped load reporting healthy) can't hide inside a
    production adapter.
    """

    def __init__(self, model_id: str = "mock-model", **kwargs: Any):
        self.model_id = model_id
        self._loaded = False

    def load(self, **kwargs) -> None:
        self._loaded = True

    def infer(self, prompt: str, **options) -> dict[str, Any]:
        if not self._loaded:
            self.load()
        return {"text": f"[mock] {prompt[:200]}"}

    def health_check(self) -> bool:
        return self._loaded

    def metadata(self) -> dict[str, Any]:
        return {"model_id": self.model_id, "profile": "mock"}
