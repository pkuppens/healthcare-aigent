from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any

from .model_adapter import ModelAdapter


if TYPE_CHECKING:
    import torch

logger = logging.getLogger(__name__)

_SUPPORTED_DTYPES = {"float16", "float32", "bfloat16"}


class GPUAdapter(ModelAdapter):
    """GPU-backed adapter using Hugging Face transformers.

    Notes:
    - This adapter lazily imports torch and transformers so that importing this
      module (and llm_adapter_factory/adapter_registry, which import it eagerly)
      does not require the GPU stack to be installed. Constructing or calling
      load()/infer() on a GPUAdapter does require the `healthcare-aigent[gpu]`
      extra (torch + transformers) and will attempt to download model artifacts.
    - This adapter always performs a real load; it has no test/CI escape hatch.
      Use MockAdapter (src/llm/mock_adapter.py) in tests instead of skipping
      the real load from inside this class.
    """

    def __init__(self, model_id: str, torch_dtype: str = "float16"):
        if torch_dtype not in _SUPPORTED_DTYPES:
            raise ValueError(f"Unsupported torch_dtype {torch_dtype!r}; expected one of {sorted(_SUPPORTED_DTYPES)}")
        self.model_id = model_id
        self.torch_dtype = torch_dtype
        self.tokenizer: Any = None
        self.model: Any = None
        self.device: torch.device | None = None

    def load(self, **kwargs) -> None:
        import torch
        from transformers import AutoModelForCausalLM, AutoTokenizer

        logger.info("Loading model %s on GPU (device_map=auto)", self.model_id)
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_id, use_fast=True)
        dtype = getattr(torch, self.torch_dtype)
        self.model = AutoModelForCausalLM.from_pretrained(
            self.model_id,
            torch_dtype=dtype,
            device_map="auto",
            low_cpu_mem_usage=True,
        )
        # pick device of first parameter
        self.device = next(self.model.parameters()).device

    def infer(self, prompt: str, max_tokens: int = 128, **options) -> dict[str, Any]:
        if self.model is None:
            self.load()
        inputs = self.tokenizer(prompt, return_tensors="pt")
        inputs = {k: v.to(self.device) for k, v in inputs.items()}
        outputs = self.model.generate(**inputs, max_new_tokens=max_tokens, **options)
        text = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        return {"text": text}

    def health_check(self) -> bool:
        try:
            return self.model is not None and self.device is not None
        except Exception:
            return False

    def metadata(self) -> dict[str, Any]:
        return {"model_id": self.model_id, "profile": "gpu"}
