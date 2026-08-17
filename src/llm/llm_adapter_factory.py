from typing import Any

from .adapter_registry import get_adapter, register_adapter, select_adapter_from_env
from .edge_adapter import EdgeAdapter
from .gpu_adapter import GPUAdapter


# Register known adapters
register_adapter("gpu", GPUAdapter)
register_adapter("edge", EdgeAdapter)


def create_adapter_instance(profile: str = None, **kwargs):
    """Create an adapter instance for the given profile or the profile selected via env.

    Example usage:
        factory = create_adapter_instance()  # uses LLM_PROFILE env or defaults to 'gpu'
        adapter = factory(model_id="Juvoly/J1-Llama-8B-exp")
    """
    if profile is None:
        adapter_cls = select_adapter_from_env()
    else:
        adapter_cls = get_adapter(profile)
    return adapter_cls(**kwargs)
