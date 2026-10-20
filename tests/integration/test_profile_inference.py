"""Real inference and Ollama cache behaviour for the local model profiles (issues #2, #26).

Runs short synthetic clinical prompts through the Ollama-backed profiles in
config/llm_profiles.yml. A test skips itself when Ollama is not reachable or a model it needs
has not been pulled, so this is safe to run anywhere; CI runs unit tests only.

    uv run pytest -m ollama tests/integration/test_profile_inference.py
"""

import subprocess
import time

import pytest

from src.llm.llm_factory import LLMFactory
from src.llm.ollama_llm import check_ollama_availability, is_model_available
from src.llm.ollama_residency import ollama_base_url, ollama_session, preload_profiles, residency_monitor, running_models
from src.llm.profile_config import get_profile


PROMPT = (
    "Answer with the letter only. Which drug class does metoprolol belong to? "
    "A) ACE inhibitor B) Beta blocker C) Calcium channel blocker D) Diuretic"
)


def _require_models(*profiles: str) -> None:
    if not check_ollama_availability():
        pytest.skip("Ollama is not running")
    for profile in profiles:
        model = get_profile(profile).model
        if not is_model_available(model):
            pytest.skip(f"{model} not pulled: ollama pull {model}")


def _gpu_total_mib() -> int:
    try:
        out = subprocess.run(
            ["nvidia-smi", "--query-gpu=memory.total", "--format=csv,noheader,nounits"], capture_output=True, text=True, check=True
        ).stdout
    except (OSError, subprocess.CalledProcessError):
        return 0
    return max(int(line) for line in out.split())


def _unload_and_wait(model: str) -> None:
    ollama_session.post(f"{ollama_base_url()}/api/generate", json={"model": model, "keep_alive": 0}, timeout=60)
    for _ in range(30):  # unloading is asynchronous
        if model not in running_models():
            return
        time.sleep(1)


@pytest.mark.ollama
@pytest.mark.integration
@pytest.mark.parametrize("profile", ["edge", "cpu", "gpu"])
def test_profile_answers_clinical_question(profile):
    """Each Ollama profile answers a short clinical question correctly, with reasoning stripped and token usage reported."""
    _require_models(profile)

    llm = LLMFactory.create_from_profile(profile, temperature=0.0)
    answer = llm.invoke(PROMPT)

    assert "<unused9" not in answer and "<think>" not in answer
    assert answer.strip().upper().startswith("B") or "beta blocker" in answer.lower()
    assert llm.last_usage and llm.last_usage["output_tokens"] > 0


@pytest.mark.ollama
@pytest.mark.integration
def test_preload_gpu_and_edge_fit_together_on_24gb():
    """medgemma:27b + medgemma1.5:4b are co-resident and 100% on a 24 GB GPU when preloaded largest first."""
    _require_models("gpu", "edge")
    if _gpu_total_mib() < 24000:
        pytest.skip("needs a GPU with 24 GB VRAM")

    loaded = preload_profiles(["edge", "gpu"])

    assert loaded == ["gpu", "edge"]  # largest first, whatever the requested order
    running = running_models()
    for profile in loaded:
        entry = running[get_profile(profile).model]
        assert entry["size_vram"] == entry["size"]


@pytest.mark.ollama
@pytest.mark.integration
def test_unloading_a_preloaded_model_early_is_reported_as_eviction():
    """A preloaded model removed before its keep_alive expiry (here: by another client) is reported as evicted."""
    _require_models("edge")
    model = get_profile("edge").model
    preload_profiles(["edge"])

    _unload_and_wait(model)

    assert residency_monitor.check_evictions(running_models()) == [model]


@pytest.mark.ollama
@pytest.mark.integration
def test_alternating_profiles_that_share_a_model_warns_about_reloads(caplog):
    """edge then cpu (same model, different num_gpu) reloads medgemma1.5:4b, and the reload is logged as a warning."""
    _require_models("edge", "cpu")
    edge, cpu = LLMFactory.create_from_profile("edge", temperature=0.0), LLMFactory.create_from_profile("cpu", temperature=0.0)

    edge.invoke(PROMPT)
    caplog.clear()
    cpu.invoke(PROMPT)

    assert "Reloading Ollama model 'medgemma1.5:4b'" in caplog.text
    assert running_models()["medgemma1.5:4b"]["size_vram"] == 0  # now the CPU instance
