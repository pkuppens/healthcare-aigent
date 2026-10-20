"""Where Ollama models are resident, and when they leave the cache (issue #26).

This project is a single application that occasionally switches models, so it treats Ollama's
cache as its own: a model that runs (partly) off the GPU, is reloaded because its load options
changed, or is evicted before its keep_alive expires, is reported instead of silently costing
speed or a reload in the middle of a request.

- `ResidencyMonitor.ensure_loaded()` runs before each profile LLM call. It loads the model
  explicitly when it isn't resident with the right load options, then checks GPU residency
  (`require_gpu` raises or warns) before any inference is spent.
- `preload_profiles()` loads the configured profiles up front, largest model first, because
  Ollama evicts an already-loaded model when a larger one no longer fits next to it.

Measurements behind these choices (RTX 4090, 24 GB) are in issue #26 and docs/models.md.
"""

import logging
import os
import re
from collections.abc import Callable
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any

import requests

from src.llm.circuit_breaker import HTTP_OK
from src.llm.profile_config import ModelProfile, get_preload_profiles, get_profile


logger = logging.getLogger(__name__)

DEFAULT_OLLAMA_URL = "http://localhost:11434"

# Ollama reloads a resident model when any of these differ, so two profiles that share a model
# but differ here can't be resident at the same time.
LOAD_OPTIONS = ("num_ctx", "num_gpu", "num_batch", "num_thread", "main_gpu", "use_mmap")

# A model that vanishes within this window before its expiry has simply expired.
_EXPIRY_GRACE_SECONDS = 5

# One pooled HTTP session for Ollama's management endpoints. On Windows, "localhost" tries IPv6
# first and Ollama listens on IPv4 only, so every *new* connection costs ~2 s; per-call
# requests.get() added that to every LLM call.
ollama_session = requests.Session()

RunningModels = dict[str, dict[str, Any]]


class GPUResidencyError(RuntimeError):
    """A profile that requires the GPU is (partly) running on the CPU."""


def ollama_base_url(base_url: str | None = None) -> str:
    """`base_url`, else OLLAMA_BASE_URL, else Ollama's default address."""
    return base_url or os.getenv("OLLAMA_BASE_URL", DEFAULT_OLLAMA_URL)


def with_latest_tag(model: str) -> str:
    """Ollama lists "llama3" as "llama3:latest"; compare names in that form."""
    return model if ":" in model else f"{model}:latest"


def select_load_options(options: dict[str, Any]) -> dict[str, Any]:
    """The subset of `options` that makes Ollama load a separate model instance."""
    return {key: options[key] for key in LOAD_OPTIONS if key in options}


def parse_expires_at(value: str) -> datetime:
    """Parse Ollama's `expires_at`, which can carry nanoseconds (Python < 3.12 only takes 6 digits)."""
    return datetime.fromisoformat(re.sub(r"(\.\d{6})\d+", r"\1", value.replace("Z", "+00:00")))


def running_models(base_url: str | None = None) -> RunningModels:
    """Return Ollama's /api/ps entries keyed by model name."""
    response = ollama_session.get(f"{ollama_base_url(base_url)}/api/ps", timeout=5)
    response.raise_for_status()
    return {entry["name"]: entry for entry in response.json().get("models", [])}


def pulled_models(base_url: str | None = None) -> dict[str, int]:
    """Return the pulled models (/api/tags) as {name: size in bytes}."""
    response = ollama_session.get(f"{ollama_base_url(base_url)}/api/tags", timeout=5)
    response.raise_for_status()
    return {m["name"]: m.get("size", 0) for m in response.json().get("models", [])}


def _instance_matches(entry: dict[str, Any], load_options: dict[str, Any]) -> bool:
    """Whether a resident model, loaded by someone else, looks like it was loaded with `load_options`.

    /api/ps shows the context length and VRAM use, not the options, so this compares what it can:
    num_ctx, and whether the instance is CPU-only exactly when num_gpu is 0.
    """
    if "num_ctx" in load_options and entry.get("context_length") != load_options["num_ctx"]:
        return False
    return (load_options.get("num_gpu") == 0) == (entry.get("size_vram", 0) == 0)


@dataclass
class _LoadedModel:
    load_options: dict[str, Any]
    expires_at: datetime | None = None


class ResidencyMonitor:
    """Tracks the models this application loaded: GPU residency, reloads and early eviction."""

    def __init__(self, base_url: str | None = None):
        self.base_url = base_url
        self._loaded: dict[str, _LoadedModel] = {}

    def ensure_loaded(self, model: str, load_options: dict[str, Any], keep_alive: str | int | None, require_gpu: bool) -> None:
        """Make sure `model` is resident with `load_options` and on the GPU, before a call uses it.

        Reports early evictions first. Loads the model explicitly (no inference) when it is missing
        or resident with other load options, warning when that replaces a resident instance, then
        checks GPU residency. Never fails because /api/ps is briefly unreachable.
        """
        model = with_latest_tag(model)
        running = self._running_or_none()
        if running is None:
            return
        self.check_evictions(running)
        entry, known = running.get(model), self._loaded.get(model)
        if entry is not None and known is not None and known.load_options == load_options:
            return
        if entry is not None and known is None and _instance_matches(entry, load_options):
            self._remember(model, load_options, running)
            self._check_placement(model, load_options, require_gpu, running)
            return
        if entry is not None:
            was = (
                known.load_options
                if known
                else f"context {entry.get('context_length')}, {entry.get('size_vram', 0) / 1e9:.1f} GB VRAM"
            )
            logger.warning(
                f"Reloading Ollama model '{model}' with load options {load_options} (resident instance: {was}). "
                "Ollama keeps one instance per model, so alternating profiles that share a model reloads it each time."
            )
        self.load(model, load_options, keep_alive)
        running = running_models(self.base_url)
        self._remember(model, load_options, running)
        self._check_placement(model, load_options, require_gpu, running)

    def after_call(self, model: str) -> None:
        """Refresh `model`'s keep_alive expiry, which each call extends."""
        model = with_latest_tag(model)
        known = self._loaded.get(model)
        if known is None:
            return
        running = self._running_or_none()
        if running is not None:
            self._remember(model, known.load_options, running)

    def load(self, model: str, load_options: dict[str, Any], keep_alive: str | int | None) -> None:
        """Load `model` into Ollama without generating anything (empty-prompt /api/generate)."""
        payload: dict[str, Any] = {"model": model, "options": load_options}
        if keep_alive is not None:
            payload["keep_alive"] = keep_alive
        logger.info(f"Loading Ollama model '{model}' with {load_options}")
        response = ollama_session.post(f"{ollama_base_url(self.base_url)}/api/generate", json=payload, timeout=600)
        if response.status_code != HTTP_OK:
            raise RuntimeError(f"Ollama could not load '{model}': {response.text}")

    def _check_placement(self, model: str, load_options: dict[str, Any], require_gpu: bool, running: RunningModels) -> None:
        # num_gpu: 0 asks for the CPU on purpose (the cpu profile); only GPU-placed models are checked.
        if load_options.get("num_gpu") != 0:
            self.check_gpu(model, require_gpu, running)

    def check_gpu(self, model: str, require_gpu: bool, running: RunningModels) -> None:
        """Raise (require_gpu) or warn when `model` is resident but not fully in VRAM."""
        model = with_latest_tag(model)
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
            "use a smaller profile (the `cpu` profile on machines without a suitable GPU), "
            "or set require_gpu: false for this profile in config/llm_profiles.yml."
        )
        if require_gpu:
            raise GPUResidencyError(message)
        logger.warning(message)

    def check_evictions(self, running: RunningModels) -> list[str]:
        """Report tracked models that left Ollama; return those evicted before their expiry."""
        now = datetime.now(UTC)
        evicted = []
        for model, known in list(self._loaded.items()):
            if model in running:
                continue
            del self._loaded[model]
            remaining = (known.expires_at - now).total_seconds() if known.expires_at else 0
            if remaining > _EXPIRY_GRACE_SECONDS:
                evicted.append(model)
                logger.warning(
                    f"Ollama evicted '{model}' {remaining / 60:.1f} min before its keep_alive expiry "
                    f"({known.expires_at.isoformat(timespec='seconds')}). Resident now: {', '.join(running) or 'none'}. "
                    "The next call reloads it."
                )
            else:
                logger.info(f"Ollama model '{model}' expired from the cache (keep_alive); the next call reloads it.")
        return evicted

    def remember_loaded(self, model: str, load_options: dict[str, Any], running: RunningModels) -> None:
        """Track `model` as loaded by this application with `load_options`, with its current expiry."""
        self._remember(with_latest_tag(model), load_options, running)

    def _remember(self, model: str, load_options: dict[str, Any], running: RunningModels) -> None:
        entry = running.get(model) or {}
        expires_at = parse_expires_at(entry["expires_at"]) if entry.get("expires_at") else None
        self._loaded[model] = _LoadedModel(load_options, expires_at)

    def _running_or_none(self) -> RunningModels | None:
        return _ignore_unreachable(lambda: running_models(self.base_url))


def _ignore_unreachable(fetch: Callable[[], RunningModels]) -> RunningModels | None:
    # Residency reporting must never break a call because /api/ps is briefly unreachable.
    try:
        return fetch()
    except requests.RequestException as e:
        logger.debug(f"Skipping Ollama residency check: {e}")
        return None


# One application, one Ollama cache: a module-level monitor shared by all profile-created LLMs.
residency_monitor = ResidencyMonitor()


def plan_preload(profiles: list[str]) -> list[ModelProfile]:
    """Resolve and validate preload profiles; raise ValueError on conflicting load options."""
    planned: list[ModelProfile] = []
    by_model: dict[str, ModelProfile] = {}
    for name in profiles:
        profile = get_profile(name)
        if profile.provider != "ollama":
            raise ValueError(f"Profile '{name}' uses provider '{profile.provider}'; only ollama profiles can be preloaded")
        model = with_latest_tag(profile.model)
        other = by_model.get(model)
        if other is not None:
            if select_load_options(other.options) != select_load_options(profile.options):
                raise ValueError(
                    f"Profiles '{other.name}' and '{name}' both use '{profile.model}' with different load options "
                    f"({select_load_options(other.options)} vs {select_load_options(profile.options)}); "
                    "Ollama keeps one instance per model, so they can't both be preloaded"
                )
            continue
        by_model[model] = profile
        planned.append(profile)
    return planned


def preload_profiles(profiles: list[str] | None = None, monitor: ResidencyMonitor | None = None) -> list[str]:
    """Load profiles into Ollama now instead of on their first call; return the profiles loaded.

    Defaults to config/llm_profiles.yml's `preload` list and the shared `residency_monitor`.
    Models load largest first, with each profile's load options and keep_alive (so the first
    real call finds the same instance). Afterwards every preloaded model must still be
    resident, and on the GPU where its profile has require_gpu.
    """
    monitor = monitor or residency_monitor
    planned = plan_preload(get_preload_profiles() if profiles is None else profiles)
    if not planned:
        return []
    sizes = pulled_models(monitor.base_url)
    missing = [p.model for p in planned if with_latest_tag(p.model) not in sizes]
    if missing:
        raise ValueError(f"Cannot preload models that are not pulled: {', '.join(missing)} (run `ollama pull <model>`)")
    planned.sort(key=lambda p: sizes[with_latest_tag(p.model)], reverse=True)

    for profile in planned:
        logger.info(f"Preloading profile '{profile.name}' ({profile.model})")
        monitor.load(profile.model, select_load_options(profile.options), profile.keep_alive)

    running = running_models(monitor.base_url)
    evicted = [p.model for p in planned if with_latest_tag(p.model) not in running]
    if evicted:
        raise GPUResidencyError(
            f"Preloaded models were evicted while loading the rest: {', '.join(evicted)}. "
            f"Profiles {[p.name for p in planned]} do not fit in memory together."
        )
    for profile in planned:
        monitor._check_placement(profile.model, select_load_options(profile.options), profile.require_gpu, running)
        monitor.remember_loaded(profile.model, select_load_options(profile.options), running)
    return [p.name for p in planned]
