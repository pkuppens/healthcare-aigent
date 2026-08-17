import os
from typing import Dict, Type

from .model_adapter import ModelAdapter

_REGISTRY: Dict[str, Type[ModelAdapter]] = {}


def register_adapter(name: str, adapter_cls: Type[ModelAdapter]) -> None:
    _REGISTRY[name] = adapter_cls


def get_adapter(name: str) -> Type[ModelAdapter]:
    if name not in _REGISTRY:
        raise KeyError(f"Adapter '{name}' not registered")
    return _REGISTRY[name]


def select_adapter_from_env(default: str = "gpu"):
    """Select adapter by env var LLM_PROFILE or default."""
    profile = os.environ.get("LLM_PROFILE", default)
    return get_adapter(profile)
