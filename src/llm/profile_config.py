"""Config-file-driven model profiles (issue #2).

Deliberately no environment-variable path: which profile is the default, and
which provider/model/options each profile uses, live in
config/llm_profiles.yml. Callers that need a specific profile pass its name to
LLMFactory.create_from_profile(); this module only reads and validates the file.
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


def get_preload_profiles(config_path: Path | str = DEFAULT_CONFIG_PATH) -> list[str]:
    """Return the profiles to load at startup (`preload`, empty when unset)."""
    preload = load_profile_config(config_path).get("preload") or []
    if not isinstance(preload, list):
        raise ValueError(f"{config_path}: 'preload' must be a list of profile names")
    return preload


def get_profile(profile: str, config_path: Path | str = DEFAULT_CONFIG_PATH) -> dict[str, Any]:
    """Return the profile as {"provider", "model", "options", "require_gpu", "keep_alive"}.

    `require_gpu` comes from the profile, else the top-level `require_gpu`, else True.
    `keep_alive` (how long Ollama keeps the model loaded, e.g. "30m" or -1) is None when unset,
    which leaves Ollama's default (5 minutes).
    """
    config = load_profile_config(config_path)
    profiles = config.get("profiles", {})
    if profile not in profiles:
        raise KeyError(f"Profile '{profile}' not found in {config_path}")
    entry = profiles[profile] or {}
    for key in ("provider", "model"):
        if not entry.get(key):
            raise ValueError(f"Profile '{profile}' in {config_path} must set '{key}'")
    options = entry.get("options") or {}
    if not isinstance(options, dict):
        raise ValueError(f"Profile '{profile}' in {config_path}: 'options' must be a mapping")
    require_gpu = entry.get("require_gpu", config.get("require_gpu", True))
    if not isinstance(require_gpu, bool):
        raise ValueError(f"Profile '{profile}' in {config_path}: 'require_gpu' must be true or false")
    return {
        "provider": entry["provider"],
        "model": entry["model"],
        "options": options,
        "require_gpu": require_gpu,
        "keep_alive": entry.get("keep_alive"),
    }
