import logging
from typing import Dict, Any

from .model_adapter import ModelAdapter

logger = logging.getLogger(__name__)


class EdgeAdapter(ModelAdapter):
    """Edge adapter: simple wrapper for calling a lightweight runtime or a quantized model.

    This is a minimal, testable implementation that should be replaced or extended
    to call a real local runtime (ggml/gguf binary, Ollama, onnxruntime quantized, etc.).
    """

    def __init__(self, artifact_path: str = None):
        self.artifact_path = artifact_path
        self.client = None

    def load(self, **kwargs) -> None:
        # Example: If using a subprocess runner (ggml) or local server, init client here.
        logger.info("EdgeAdapter load called; artifact_path=%s", self.artifact_path)

    def infer(self, prompt: str, max_tokens: int = 128, **options) -> Dict[str, Any]:
        # Placeholder inference: in production, call the local runtime (e.g., ggml binary, Ollama API).
        # Return a stub for tests and quick verification; implement real runtime later.
        return {"text": f"[edge-simulated] {prompt[:200]}"}

    def health_check(self) -> bool:
        # If a runtime client exists, call its health. Here return True as placeholder.
        return True

    def metadata(self) -> Dict[str, Any]:
        return {"artifact_path": self.artifact_path, "profile": "edge"}
