"""Unit tests for Ollama GPU residency, reload and eviction reporting, and preload (issue #26).

Ollama's HTTP API (/api/ps, /api/tags, /api/generate) is mocked with requests-mock.
"""

from datetime import UTC, datetime, timedelta
from unittest.mock import MagicMock, patch

import pytest

from src.llm.ollama_llm import OllamaLLM
from src.llm.ollama_residency import (
    GPUResidencyError,
    ResidencyMonitor,
    parse_expires_at,
    plan_preload,
    preload_profiles,
)


OLLAMA_URL = "http://ollama.test:11434"
PS_URL = f"{OLLAMA_URL}/api/ps"
GENERATE_URL = f"{OLLAMA_URL}/api/generate"
GB = 1_000_000_000
EDGE_LOAD = {"num_ctx": 4096}


def ps_entry(name, size_gb, vram_gb, context_length=4096, expires_in=timedelta(minutes=30)):
    expires = (datetime.now(UTC) + expires_in).isoformat()
    return {
        "name": name,
        "model": name,
        "size": int(size_gb * GB),
        "size_vram": int(vram_gb * GB),
        "context_length": context_length,
        "expires_at": expires,
    }


def mock_ps(requests_mock, *snapshots):
    """Serve each snapshot (a list of ps entries) for one /api/ps call, repeating the last one."""
    requests_mock.get(PS_URL, [{"json": {"models": list(entries)}} for entries in snapshots])


@pytest.fixture
def monitor():
    return ResidencyMonitor(OLLAMA_URL)


@pytest.fixture
def generate(requests_mock):
    return requests_mock.post(GENERATE_URL, json={"done": True, "done_reason": "load"})


def test_parse_expires_at_handles_nanoseconds_and_offsets():
    """Ollama's nanosecond timestamps with a UTC offset parse on every supported Python version."""
    parsed = parse_expires_at("2319-01-30T09:25:23.992670607+01:00")

    assert parsed == datetime(2319, 1, 30, 8, 25, 23, 992670, tzinfo=UTC)


def test_ensure_loaded_loads_a_missing_model_without_inference(monitor, requests_mock, generate):
    """A model that isn't resident is loaded with an empty-prompt request carrying its load options and keep_alive."""
    mock_ps(requests_mock, [], [ps_entry("medgemma1.5:4b", 2.9, 2.9)])

    monitor.ensure_loaded("medgemma1.5:4b", EDGE_LOAD, "30m", require_gpu=True)

    assert generate.call_count == 1
    assert generate.last_request.json() == {"model": "medgemma1.5:4b", "options": EDGE_LOAD, "keep_alive": "30m"}


def test_ensure_loaded_skips_a_model_it_already_loaded_with_the_same_options(monitor, requests_mock, generate):
    """Once loaded with these options, later calls only check /api/ps and don't reload."""
    mock_ps(requests_mock, [], [ps_entry("medgemma1.5:4b", 2.9, 2.9)])
    monitor.ensure_loaded("medgemma1.5:4b", EDGE_LOAD, "30m", require_gpu=True)

    monitor.ensure_loaded("medgemma1.5:4b", EDGE_LOAD, "30m", require_gpu=True)

    assert generate.call_count == 1


def test_ensure_loaded_warns_when_other_load_options_force_a_reload(monitor, requests_mock, generate, caplog):
    """Alternating profiles that share a model (edge, then cpu) reloads it, and says so."""
    mock_ps(requests_mock, [], [ps_entry("medgemma1.5:4b", 2.9, 2.9)], [ps_entry("medgemma1.5:4b", 2.9, 0.0)])
    monitor.ensure_loaded("medgemma1.5:4b", EDGE_LOAD, "30m", require_gpu=True)

    monitor.ensure_loaded("medgemma1.5:4b", {"num_ctx": 4096, "num_gpu": 0}, "30m", require_gpu=False)

    assert generate.call_count == 2
    assert "Reloading Ollama model 'medgemma1.5:4b'" in caplog.text


def test_ensure_loaded_adopts_a_matching_instance_loaded_elsewhere(monitor, requests_mock, generate):
    """A resident instance with the same context and GPU placement (e.g. from preload in another process) is reused."""
    mock_ps(requests_mock, [ps_entry("medgemma1.5:4b", 2.9, 2.9, context_length=4096)])

    monitor.ensure_loaded("medgemma1.5:4b", EDGE_LOAD, "30m", require_gpu=True)

    assert generate.call_count == 0


def test_ensure_loaded_reloads_a_cpu_instance_for_a_gpu_profile(monitor, requests_mock, generate, caplog):
    """A CPU-only instance (left by the cpu profile) is replaced for a GPU profile instead of failing require_gpu."""
    mock_ps(requests_mock, [ps_entry("medgemma1.5:4b", 2.9, 0.0)], [ps_entry("medgemma1.5:4b", 2.9, 2.9)])

    monitor.ensure_loaded("medgemma1.5:4b", EDGE_LOAD, "30m", require_gpu=True)

    assert generate.call_count == 1
    assert "Reloading" in caplog.text


def test_ensure_loaded_raises_when_the_loaded_model_is_not_on_the_gpu(monitor, requests_mock, generate):
    """With require_gpu, a model that lands partly on the CPU fails, naming the other resident models."""
    mock_ps(requests_mock, [], [ps_entry("medgemma1.5:4b", 2.9, 1.0), ps_entry("medgemma:27b", 17.5, 17.5, 8192)])

    with pytest.raises(GPUResidencyError, match=r"only 34% on the GPU.*medgemma:27b"):
        monitor.ensure_loaded("medgemma1.5:4b", EDGE_LOAD, "30m", require_gpu=True)


def test_ensure_loaded_warns_on_partial_offload_when_gpu_not_required(monitor, requests_mock, generate, caplog):
    """Without require_gpu, a partial offload is logged as a warning and the call proceeds."""
    mock_ps(requests_mock, [], [ps_entry("medgemma1.5:4b", 2.9, 1.45)])

    monitor.ensure_loaded("medgemma1.5:4b", EDGE_LOAD, "30m", require_gpu=False)

    assert "only 50% on the GPU" in caplog.text


def test_check_gpu_matches_untagged_model_names(monitor):
    """An untagged model name ("llama3") is checked against Ollama's "llama3:latest" entry."""
    with pytest.raises(GPUResidencyError):
        monitor.check_gpu("llama3", True, {"llama3:latest": ps_entry("llama3:latest", 4.7, 1.0)})


def test_early_eviction_is_reported_as_warning(monitor, requests_mock, generate, caplog):
    """A model that disappears well before its keep_alive expiry is reported as evicted, with what replaced it."""
    mock_ps(requests_mock, [], [ps_entry("medgemma:27b", 17.5, 17.5, 8192)])
    monitor.ensure_loaded("medgemma:27b", {"num_ctx": 8192}, "30m", require_gpu=True)

    evicted = monitor.check_evictions({"llama3.1:8b": ps_entry("llama3.1:8b", 5.3, 5.3)})

    assert evicted == ["medgemma:27b"]
    assert "evicted 'medgemma:27b'" in caplog.text
    assert "Resident now: llama3.1:8b" in caplog.text


def test_normal_expiry_is_reported_as_info(monitor, caplog):
    """A model that leaves at its keep_alive expiry is reported at info level, not as an eviction."""
    caplog.set_level("INFO")
    expired = ps_entry("medgemma1.5:4b", 2.9, 2.9, expires_in=timedelta(seconds=-1))
    monitor.remember_loaded("medgemma1.5:4b", EDGE_LOAD, {"medgemma1.5:4b": expired})

    assert monitor.check_evictions({}) == []
    assert "expired from the cache" in caplog.text
    assert not [r for r in caplog.records if r.levelname == "WARNING"]


def test_eviction_is_reported_once(monitor):
    """An eviction is reported on the first check after it happens, not on every later call."""
    monitor.remember_loaded("medgemma:27b", {"num_ctx": 8192}, {"medgemma:27b": ps_entry("medgemma:27b", 17.5, 17.5)})

    assert monitor.check_evictions({}) == ["medgemma:27b"]
    assert monitor.check_evictions({}) == []


def test_after_call_refreshes_the_keep_alive_expiry(monitor, requests_mock):
    """Each call extends keep_alive, so the tracked expiry follows what /api/ps reports after the call."""
    monitor.remember_loaded("medgemma1.5:4b", EDGE_LOAD, {"medgemma1.5:4b": ps_entry("medgemma1.5:4b", 2.9, 2.9)})
    later = ps_entry("medgemma1.5:4b", 2.9, 2.9, expires_in=timedelta(minutes=45))
    mock_ps(requests_mock, [later])

    monitor.after_call("medgemma1.5:4b")

    assert monitor._loaded["medgemma1.5:4b"].expires_at == parse_expires_at(later["expires_at"])


def test_residency_checks_never_break_a_call_when_ollama_ps_fails(monitor, requests_mock, generate):
    """If /api/ps errors, the checks are skipped (logged at debug) and nothing is loaded or raised."""
    requests_mock.get(PS_URL, status_code=500)

    monitor.ensure_loaded("medgemma:27b", {"num_ctx": 8192}, "30m", require_gpu=True)
    monitor.after_call("medgemma:27b")

    assert generate.call_count == 0


@patch("src.llm.ollama_llm.ChatOllama")
def test_ollama_llm_runs_residency_checks_around_each_call(mock_chat_ollama):
    """OllamaLLM asks the monitor to ensure residency (with its load options) before invoking, and refreshes after."""
    mock_chat_ollama.return_value.invoke.return_value.content = "answer"
    mock_chat_ollama.return_value.invoke.return_value.usage_metadata = None
    monitor = MagicMock(spec=ResidencyMonitor)
    llm = OllamaLLM(model_name="medgemma:27b", residency_monitor=monitor, require_gpu=True, num_ctx=8192, keep_alive="30m")

    assert llm.invoke("q") == "answer"
    monitor.ensure_loaded.assert_called_once_with("medgemma:27b", {"num_ctx": 8192}, "30m", True)
    monitor.after_call.assert_called_once_with("medgemma:27b")


@patch("src.llm.ollama_llm.ChatOllama")
def test_gpu_check_fails_before_any_inference_is_spent(mock_chat_ollama, requests_mock, generate):
    """When a GPU-required model lands on the CPU, the call fails before ChatOllama generates anything."""
    mock_ps(requests_mock, [], [ps_entry("medgemma:27b", 17.5, 10.0, 8192)])
    llm = OllamaLLM(model_name="medgemma:27b", residency_monitor=ResidencyMonitor(OLLAMA_URL), require_gpu=True, num_ctx=8192)

    with pytest.raises(GPUResidencyError):
        llm.invoke("q")
    mock_chat_ollama.return_value.invoke.assert_not_called()


def test_plan_preload_rejects_profiles_sharing_a_model_with_different_load_options():
    """edge and cpu share medgemma1.5:4b with different num_gpu, so they can't both be preloaded."""
    with pytest.raises(ValueError, match=r"'edge' and 'cpu'.*one instance per model"):
        plan_preload(["edge", "cpu"])


def test_plan_preload_rejects_non_ollama_profiles():
    """Only Ollama profiles have anything to preload."""
    with pytest.raises(ValueError, match="only ollama profiles"):
        plan_preload(["mock"])


@pytest.fixture
def ollama_with_medgemma(requests_mock, generate):
    requests_mock.get(
        f"{OLLAMA_URL}/api/tags",
        json={"models": [{"name": "medgemma1.5:4b", "size": int(3.3 * GB)}, {"name": "medgemma:27b", "size": int(17 * GB)}]},
    )
    return generate


def test_preload_loads_largest_first_with_profile_options(monitor, requests_mock, ollama_with_medgemma):
    """Preload sorts by model size (27B before 4B, whatever the requested order) and sends each profile's load options."""
    mock_ps(requests_mock, [ps_entry("medgemma:27b", 17.5, 17.5, 8192), ps_entry("medgemma1.5:4b", 2.9, 2.9)])

    loaded = preload_profiles(["edge", "gpu"], monitor=monitor)

    assert loaded == ["gpu", "edge"]
    bodies = [call.json() for call in ollama_with_medgemma.request_history]
    assert [b["model"] for b in bodies] == ["medgemma:27b", "medgemma1.5:4b"]
    assert bodies[0] == {"model": "medgemma:27b", "options": {"num_ctx": 8192}, "keep_alive": "30m"}


def test_preloaded_models_are_not_reloaded_by_the_first_call(monitor, requests_mock, ollama_with_medgemma):
    """After preload, a call with the profile's load options finds the tracked instance and loads nothing."""
    mock_ps(requests_mock, [ps_entry("medgemma1.5:4b", 2.9, 2.9)])
    preload_profiles(["edge"], monitor=monitor)

    monitor.ensure_loaded("medgemma1.5:4b", EDGE_LOAD, "30m", require_gpu=True)

    assert ollama_with_medgemma.call_count == 1


def test_preload_raises_when_a_model_was_evicted_by_the_next(monitor, requests_mock, ollama_with_medgemma):
    """If loading one profile pushed out another, the set doesn't fit, and preload says so."""
    mock_ps(requests_mock, [ps_entry("medgemma1.5:4b", 2.9, 2.9)])

    with pytest.raises(GPUResidencyError, match="evicted while loading.*medgemma:27b"):
        preload_profiles(["edge", "gpu"], monitor=monitor)


def test_preload_raises_when_required_gpu_is_missing(monitor, requests_mock, ollama_with_medgemma):
    """A preloaded model that isn't fully on the GPU fails preload when its profile requires the GPU."""
    mock_ps(requests_mock, [ps_entry("medgemma:27b", 17.5, 12.0, 8192)])

    with pytest.raises(GPUResidencyError, match="medgemma:27b"):
        preload_profiles(["gpu"], monitor=monitor)


def test_preload_rejects_models_that_are_not_pulled(monitor, requests_mock):
    """Preloading a model that was never pulled fails up front with the model name."""
    requests_mock.get(f"{OLLAMA_URL}/api/tags", json={"models": []})

    with pytest.raises(ValueError, match="not pulled: medgemma:27b"):
        preload_profiles(["gpu"], monitor=monitor)


def test_preload_defaults_to_empty_config_list(monitor):
    """The shipped config preloads nothing, so startup needs no Ollama at all."""
    assert preload_profiles(monitor=monitor) == []


def test_cpu_by_design_profile_is_not_reported_as_off_the_gpu(monitor, requests_mock, generate, caplog):
    """num_gpu: 0 (the cpu profile) puts the model on the CPU on purpose, so no GPU warning is logged."""
    mock_ps(requests_mock, [], [ps_entry("medgemma1.5:4b", 2.9, 0.0)])

    monitor.ensure_loaded("medgemma1.5:4b", {"num_ctx": 4096, "num_gpu": 0}, "30m", require_gpu=True)

    assert "on the GPU" not in caplog.text
