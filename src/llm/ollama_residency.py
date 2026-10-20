"""Where Ollama models are resident, and when they leave the cache (issue #26).

This project is a single application that occasionally switches models, so it treats Ollama's
cache as its own: a model that runs (partly) off the GPU, or is evicted before its keep_alive
expires, is reported instead of silently costing speed or a reload in the middle of a request.

- `ResidencyMonitor` checks GPU residency after a call (`require_gpu` raises or warns) and
  reports models that disappeared from Ollama before their expiry.
- `preload_profiles()` loads the configured profiles up front, largest model first, because
  Ollama evicts an already-loaded model when a larger one no longer fits next to it.

Measurements behind these choices (RTX 4090, 24 GB) are in issue #26 and docs/models.md.
"""

import logging
import os
import re
from datetime import UTC, datetime
from typing import Any

import requests

from src.llm.circuit_breaker import HTTP_OK
from src.llm.profile_config import get_preload_profiles, get_profile


logger = logging.getLogger(__name__)

# Ollama reloads a resident model when any of these differ, so two profiles that share a model
# but differ here can't be resident at the same time.
LOAD_OPTIONS = ("num_ctx", "num_gpu", "num_batch", "num_thread", "main_gpu", "use_mmap")

# A model that vanishes within this window before its expiry has simply expired.
_EXPIRY_GRACE_SECONDS = 5


# One pooled HTTP session for Ollama's management endpoints. On Windows, "localhost" tries IPv6
# first and Ollama listens on IPv4 only, so every *new* connection costs ~2 s; with per-call
# requests.get() the two residency checks around each LLM call added ~4 s to it.
ollama_session = requests.Session()


class GPUResidencyError(RuntimeError):
    """A profile that requires the GPU is (partly) running on the CPU."""


def _base_url(base_url: str | None) -> str:
    return base_url or os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")


def parse_expires_at(value: str) -> datetime:
    """Parse Ollama's `expires_at`, which can carry nanoseconds (Python < 3.12 only takes 6 digits)."""
    return datetime.fromisoformat(re.sub(r"(\.\d{6})\d+", r"\1", value.replace("Z", "+00:00")))


def running_models(base_url: str | None = None) -> dict[str, dict[str, Any]]:
    """Return Ollama's /api/ps entries keyed by model name."""
    response = ollama_session.get(f"{_base_url(base_url)}/api/ps", timeout=5)
    response.raise_for_status()
    return {entry["name"]: entry for entry in response.json().get("models", [])}


def tagged(model: str) -> str:
    """Ollama lists "llama3" as "llama3:latest"; compare names in that form."""
    return model if ":" in model else f"{model}:latest"


def load_options_of(options: dict[str, Any]) -> dict[str, Any]:
    """The subset of `options` that makes Ollama load a separate model instance."""
    return {key: options[key] for key in LOAD_OPTIONS if key in options}


class ResidencyMonitor:
    """Tracks the models this application loaded, and reports GPU offload and early eviction."""

    def __init__(self, base_url: str | None = None):
        self.base_url = base_url
        self._expected: dict[str, datetime] = {}  # model -> expires_at last seen in /api/ps

    def check_gpu(self, model: str, require_gpu: bool, running: dict[str, dict[str, Any]] | None = None) -> None:
        """Raise (require_gpu) or warn when `model` is resident but not fully in VRAM."""
        running = running if running is not None else running_models(self.base_url)
        model = tagged(model)
        entry = running.get(model)
        if entry is None or not entry.get("size"):
            return
        share = entry.get("size_vram", 0) / entry["size"]
        if share >= 1.0:
            return
        others = ", ".join(name for name in running if name != model) or "none"
        message = (
            f"Ollama model '{model}' is only {share:.0%} on the GPU ({entry['size'] / 1e9:.1f} GB model). "
            f"Other resident models: {others}. Free VRAM (unload other models, or `ollama stop <model>`), "
            "use a smaller profile, or set require_gpu: false for this profile in config/llm_profiles.yml."
        )
        if require_gpu:
            raise GPUResidencyError(message)
        logger.warning(message)

    def record(self, model: str, running: dict[str, dict[str, Any]] | None = None) -> None:
        """Remember `model`'s current expiry, so a later disappearance can be classified."""
        running = running if running is not None else running_models(self.base_url)
        model = tagged(model)
        entry = running.get(model)
        if entry and entry.get("expires_at"):
            self._expected[model] = parse_expires_at(entry["expires_at"])

    def check_evictions(self, running: dict[str, dict[str, Any]] | None = None) -> list[str]:
        """Report tracked models that left Ollama; return those evicted before their expiry."""
        running = running if running is not None else running_models(self.base_url)
        now = datetime.now(UTC)
        evicted = []
        for model, expires_at in list(self._expected.items()):
            if model in running:
                continue
            del self._expected[model]
            remaining = (expires_at - now).total_seconds()
            if remaining > _EXPIRY_GRACE_SECONDS:
                evicted.append(model)
                logger.warning(
                    f"Ollama evicted '{model}' {remaining / 60:.1f} min before its keep_alive expiry "
                    f"({expires_at.isoformat(timespec='seconds')}). Resident now: {', '.join(running) or 'none'}. "
                    "The next call reloads it."
                )
            else:
                logger.info(f"Ollama model '{model}' expired from the cache (keep_alive); the next call reloads it.")
        return evicted

    def before_call(self) -> None:
        self._safely(self.check_evictions)

    def after_call(self, model: str, require_gpu: bool) -> None:
        try:
            running = running_models(self.base_url)
        except requests.RequestException as e:
            logger.debug(f"Skipping residency check for '{model}': {e}")
            return
        self.record(model, running)
        self.check_gpu(model, require_gpu, running)

    def _safely(self, check: Any) -> None:
        # Residency reporting must never break a call because /api/ps is briefly unreachable.
        try:
            check()
        except requests.RequestException as e:
            logger.debug(f"Skipping residency check: {e}")


# One application, one Ollama cache: a module-level monitor shared by all profile-created LLMs.
residency_monitor = ResidencyMonitor()


def _pulled_model_sizes(base_url: str | None) -> dict[str, int]:
    response = ollama_session.get(f"{_base_url(base_url)}/api/tags", timeout=5)
    response.raise_for_status()
    return {m["name"]: m.get("size", 0) for m in response.json().get("models", [])}


def plan_preload(profiles: list[str]) -> list[tuple[str, dict[str, Any]]]:
    """Resolve and validate preload profiles; raise ValueError on conflicting load options."""
    planned: list[tuple[str, dict[str, Any]]] = []
    by_model: dict[str, tuple[str, dict[str, Any]]] = {}
    for name in profiles:
        profile = get_profile(name)
        if profile["provider"] != "ollama":
            raise ValueError(f"Profile '{name}' uses provider '{profile['provider']}'; only ollama profiles can be preloaded")
        load_options = load_options_of(profile["options"])
        model = tagged(profile["model"])
        if model in by_model:
            other, other_options = by_model[model]
            if other_options != load_options:
                raise ValueError(
                    f"Profiles '{other}' and '{name}' both use '{profile['model']}' with different load options "
                    f"({other_options} vs {load_options}); Ollama keeps one instance per model, so they can't both be preloaded"
                )
            continue
        by_model[model] = (name, load_options)
        planned.append((name, profile))
    return planned


def preload_profiles(profiles: list[str] | None = None, base_url: str | None = None) -> list[str]:
    """Load profiles into Ollama now instead of on their first call; return the profiles loaded.

    Defaults to config/llm_profiles.yml's `preload` list. Models load largest first, with each
    profile's own options and keep_alive (a preload without them would load a different
    instance, and the first real call would reload it). Afterwards every preloaded model must
    still be resident, and on the GPU where its profile has require_gpu.
    """
    planned = plan_preload(get_preload_profiles() if profiles is None else profiles)
    if not planned:
        return []
    sizes = _pulled_model_sizes(base_url)
    missing = [p["model"] for _, p in planned if tagged(p["model"]) not in sizes]
    if missing:
        raise ValueError(f"Cannot preload models that are not pulled: {', '.join(missing)} (run `ollama pull <model>`)")
    planned.sort(key=lambda item: sizes[tagged(item[1]["model"])], reverse=True)

    for name, profile in planned:
        payload: dict[str, Any] = {"model": profile["model"], "options": profile["options"]}
        if profile["keep_alive"] is not None:
            payload["keep_alive"] = profile["keep_alive"]
        logger.info(f"Preloading profile '{name}' ({profile['model']})")
        response = ollama_session.post(f"{_base_url(base_url)}/api/generate", json=payload, timeout=600)
        if response.status_code != HTTP_OK:
            raise RuntimeError(f"Ollama could not load '{profile['model']}' for profile '{name}': {response.text}")

    running = running_models(base_url)
    evicted = [p["model"] for _, p in planned if tagged(p["model"]) not in running]
    if evicted:
        raise GPUResidencyError(
            f"Preloaded models were evicted while loading the rest: {', '.join(evicted)}. "
            f"Profiles {[n for n, _ in planned]} do not fit in memory together."
        )
    for name, profile in planned:
        residency_monitor.check_gpu(profile["model"], profile["require_gpu"], running)
        residency_monitor.record(profile["model"], running)
    return [name for name, _ in planned]
