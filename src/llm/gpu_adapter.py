import logging
import os
from typing import Any

import torch

from .model_adapter import ModelAdapter


logger = logging.getLogger(__name__)

_TORCH_DTYPES = {"float16": torch.float16, "float32": torch.float32, "bfloat16": torch.bfloat16}


class GPUAdapter(ModelAdapter):
    """GPU-backed adapter using Hugging Face transformers (lazy-load).

    Notes:
    - This adapter lazily imports transformers and will attempt to download
      model artifacts unless the environment variable LLM_SKIP_REAL_LOAD=1 is set.
    - In CI/tests we recommend setting LLM_SKIP_REAL_LOAD=1 to avoid heavy downloads.
    """

    def __init__(self, model_id: str, torch_dtype: str = "float16"):
        if torch_dtype not in _TORCH_DTYPES:
            raise ValueError(f"Unsupported torch_dtype {torch_dtype!r}; expected one of {sorted(_TORCH_DTYPES)}")
        self.model_id = model_id
        self.torch_dtype = torch_dtype
        self.tokenizer: Any = None
        self.model: Any = None
        self.device: torch.device | None = None

    def load(self, **kwargs) -> None:
        # Allow tests / CI to skip heavy model downloads
        if os.environ.get("LLM_SKIP_REAL_LOAD") == "1":
            logger.info("LLM_SKIP_REAL_LOAD=1: skipping real model load for %s", self.model_id)
            self.model = object()
            self.device = torch.device("cpu")
            return

        # Import inside function so tests can run without transformers installed
        from transformers import AutoModelForCausalLM, AutoTokenizer

        logger.info("Loading model %s on GPU (device_map=auto)", self.model_id)
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_id, use_fast=True)
        dtype = _TORCH_DTYPES[self.torch_dtype]
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
        # If model is a stub (from LLM_SKIP_REAL_LOAD), return a predictable stub response
        if not hasattr(self.model, "parameters"):
            return {"text": f"[gpu-stub] {prompt[:200]}"}

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
