"""Config-file-driven profile selection for swappable LLM adapters.

Deliberately no environment-variable path: which adapter profile is the
default, and what kwargs each profile constructs its adapter with, live in
config/llm_profiles.yml. Callers that need a specific profile can still pass
it explicitly to create_adapter_instance(); this module only supplies the
default and each profile's config-file kwargs.
"""

from pathlib import Path
from typing import Any

import yaml


DEFAULT_CONFIG_PATH = Path(__file__).resolve().parents[2] / "config" / "llm_profiles.yml"


def load_profile_config(config_path: Path | str = DEFAULT_CONFIG_PATH) -> dict[str, Any]:
    """Load and parse llm_profiles.yml."""
    with Path(config_path).open() as f:
        return yaml.safe_load(f) or {}


def get_default_profile(config_path: Path | str = DEFAULT_CONFIG_PATH) -> str:
    """Return the configured default profile name."""
    config = load_profile_config(config_path)
    default_profile = config.get("default_profile")
    if not default_profile:
        raise ValueError(f"{config_path} must set 'default_profile'")
    return default_profile


def get_profile_kwargs(profile: str, config_path: Path | str = DEFAULT_CONFIG_PATH) -> dict[str, Any]:
    """Return the constructor kwargs configured for the given profile."""
    config = load_profile_config(config_path)
    profiles = config.get("profiles", {})
    if profile not in profiles:
        raise KeyError(f"Profile '{profile}' not found in {config_path}")
    return profiles[profile]
