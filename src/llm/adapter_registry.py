from .model_adapter import ModelAdapter


_REGISTRY: dict[str, type[ModelAdapter]] = {}


def register_adapter(name: str, adapter_cls: type[ModelAdapter]) -> None:
    _REGISTRY[name] = adapter_cls


def get_adapter(name: str) -> type[ModelAdapter]:
    if name not in _REGISTRY:
        raise KeyError(f"Adapter '{name}' not registered")
    return _REGISTRY[name]
