from .adapter_registry import get_adapter, register_adapter
from .edge_adapter import EdgeAdapter
from .gpu_adapter import GPUAdapter
from .model_adapter import ModelAdapter
from .profile_config import get_default_profile, get_profile_kwargs


# Register known adapters
register_adapter("gpu", GPUAdapter)
register_adapter("edge", EdgeAdapter)


def create_adapter_instance(profile: str | None = None, **kwargs) -> ModelAdapter:
    """Create an adapter instance for the given profile.

    profile defaults to config/llm_profiles.yml's `default_profile` when not
    given explicitly. If no kwargs are passed, the profile's kwargs are read
    from that same config file; explicit **kwargs override the config file
    entirely rather than merging with it.

    Example usage:
        adapter = create_adapter_instance()  # default_profile from config file
        adapter = create_adapter_instance("gpu", model_id="Juvoly/J1-Llama-8B-exp")
    """
    if profile is None:
        profile = get_default_profile()
    adapter_cls = get_adapter(profile)
    if not kwargs:
        kwargs = get_profile_kwargs(profile)
    return adapter_cls(**kwargs)
