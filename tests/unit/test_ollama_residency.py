"""Unit tests for Ollama GPU residency, eviction reporting and preload (issue #26). Ollama's HTTP API is mocked."""

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
GB = 1_000_000_000


def ps_entry(name, size_gb, vram_gb, expires_in=timedelta(minutes=30)):
    expires = (datetime.now(UTC) + expires_in).isoformat()
    return {"name": name, "model": name, "size": int(size_gb * GB), "size_vram": int(vram_gb * GB), "expires_at": expires}


def mock_ps(requests_mock, *entries):
    requests_mock.get(f"{OLLAMA_URL}/api/ps", json={"models": list(entries)})


@pytest.fixture
def monitor():
    return ResidencyMonitor(OLLAMA_URL)


def test_parse_expires_at_handles_nanoseconds_and_offsets():
    parsed = parse_expires_at("2319-01-30T09:25:23.992670607+01:00")

    assert parsed == datetime(2319, 1, 30, 8, 25, 23, 992670, tzinfo=UTC)


def test_check_gpu_passes_when_fully_in_vram(monitor, requests_mock):
    mock_ps(requests_mock, ps_entry("medgemma:27b", 17.5, 17.5))

    monitor.check_gpu("medgemma:27b", require_gpu=True)


def test_check_gpu_raises_on_partial_offload_when_required(monitor, requests_mock):
    mock_ps(requests_mock, ps_entry("medgemma1.5:4b", 2.9, 0.0), ps_entry("medgemma:27b", 17.5, 17.5))

    with pytest.raises(GPUResidencyError, match=r"only 0% on the GPU.*medgemma:27b"):
        monitor.check_gpu("medgemma1.5:4b", require_gpu=True)


def test_check_gpu_warns_on_partial_offload_when_not_required(monitor, requests_mock, caplog):
    mock_ps(requests_mock, ps_entry("medgemma1.5:4b", 2.9, 1.45))

    monitor.check_gpu("medgemma1.5:4b", require_gpu=False)

    assert "only 50% on the GPU" in caplog.text


def test_check_gpu_matches_untagged_model_names(monitor, requests_mock):
    mock_ps(requests_mock, ps_entry("llama3:latest", 4.7, 1.0))

    with pytest.raises(GPUResidencyError):
        monitor.check_gpu("llama3", require_gpu=True)


def test_early_eviction_is_reported_as_warning(monitor, requests_mock, caplog):
    mock_ps(requests_mock, ps_entry("medgemma:27b", 17.5, 17.5))
    monitor.record("medgemma:27b")
    mock_ps(requests_mock, ps_entry("llama3.1:8b", 5.3, 5.3))

    evicted = monitor.check_evictions()

    assert evicted == ["medgemma:27b"]
    assert "evicted 'medgemma:27b'" in caplog.text
    assert "Resident now: llama3.1:8b" in caplog.text


def test_normal_expiry_is_reported_as_info(monitor, requests_mock, caplog):
    caplog.set_level("INFO")
    mock_ps(requests_mock, ps_entry("medgemma1.5:4b", 2.9, 2.9, expires_in=timedelta(seconds=-1)))
    monitor.record("medgemma1.5:4b")
    mock_ps(requests_mock)

    assert monitor.check_evictions() == []
    assert "expired from the cache" in caplog.text
    assert not [r for r in caplog.records if r.levelname == "WARNING"]


def test_eviction_is_reported_once(monitor, requests_mock):
    mock_ps(requests_mock, ps_entry("medgemma:27b", 17.5, 17.5))
    monitor.record("medgemma:27b")
    mock_ps(requests_mock)

    assert monitor.check_evictions() == ["medgemma:27b"]
    assert monitor.check_evictions() == []


@patch("src.llm.ollama_llm.ChatOllama")
def test_ollama_llm_runs_residency_checks_around_each_call(mock_chat_ollama):
    mock_chat_ollama.return_value.invoke.return_value.content = "answer"
    mock_chat_ollama.return_value.invoke.return_value.usage_metadata = None
    monitor = MagicMock(spec=ResidencyMonitor)
    llm = OllamaLLM(model_name="medgemma:27b", residency_monitor=monitor, require_gpu=True)

    assert llm.invoke("q") == "answer"
    monitor.before_call.assert_called_once_with()
    monitor.after_call.assert_called_once_with("medgemma:27b", True)


@patch("src.llm.ollama_llm.ChatOllama")
def test_ollama_llm_call_raises_when_required_gpu_is_missing(mock_chat_ollama, requests_mock):
    mock_chat_ollama.return_value.invoke.return_value.content = "answer"
    mock_ps(requests_mock, ps_entry("medgemma:27b", 17.5, 10.0))
    llm = OllamaLLM(model_name="medgemma:27b", residency_monitor=ResidencyMonitor(OLLAMA_URL), require_gpu=True)

    with pytest.raises(GPUResidencyError):
        llm.invoke("q")


def test_residency_checks_never_break_a_call_when_ollama_ps_fails(monitor, requests_mock):
    requests_mock.get(f"{OLLAMA_URL}/api/ps", status_code=500)

    monitor.before_call()
    monitor.after_call("medgemma:27b", require_gpu=True)


def test_plan_preload_rejects_profiles_sharing_a_model_with_different_load_options():
    with pytest.raises(ValueError, match=r"'edge' and 'cpu'.*one instance per model"):
        plan_preload(["edge", "cpu"])


def test_plan_preload_rejects_non_ollama_profiles():
    with pytest.raises(ValueError, match="only ollama profiles"):
        plan_preload(["mock"])


@pytest.fixture
def ollama_with_medgemma(requests_mock):
    requests_mock.get(
        f"{OLLAMA_URL}/api/tags",
        json={"models": [{"name": "medgemma1.5:4b", "size": int(3.3 * GB)}, {"name": "medgemma:27b", "size": int(17 * GB)}]},
    )
    return requests_mock.post(f"{OLLAMA_URL}/api/generate", json={"done": True, "done_reason": "load"})


def test_preload_loads_largest_first_with_profile_options(requests_mock, ollama_with_medgemma):
    mock_ps(requests_mock, ps_entry("medgemma:27b", 17.5, 17.5), ps_entry("medgemma1.5:4b", 2.9, 2.9))

    loaded = preload_profiles(["edge", "gpu"], base_url=OLLAMA_URL)

    assert loaded == ["gpu", "edge"]
    bodies = [call.json() for call in ollama_with_medgemma.request_history]
    assert [b["model"] for b in bodies] == ["medgemma:27b", "medgemma1.5:4b"]
    assert bodies[0] == {"model": "medgemma:27b", "options": {"num_ctx": 8192}, "keep_alive": "30m"}


def test_preload_raises_when_a_model_was_evicted_by_the_next(requests_mock, ollama_with_medgemma):
    mock_ps(requests_mock, ps_entry("medgemma1.5:4b", 2.9, 2.9))

    with pytest.raises(GPUResidencyError, match="evicted while loading.*medgemma:27b"):
        preload_profiles(["edge", "gpu"], base_url=OLLAMA_URL)


def test_preload_raises_when_required_gpu_is_missing(requests_mock, ollama_with_medgemma):
    mock_ps(requests_mock, ps_entry("medgemma:27b", 17.5, 12.0))

    with pytest.raises(GPUResidencyError, match="medgemma:27b"):
        preload_profiles(["gpu"], base_url=OLLAMA_URL)


def test_preload_rejects_models_that_are_not_pulled(requests_mock):
    requests_mock.get(f"{OLLAMA_URL}/api/tags", json={"models": []})

    with pytest.raises(ValueError, match="not pulled: medgemma:27b"):
        preload_profiles(["gpu"], base_url=OLLAMA_URL)


def test_preload_defaults_to_empty_config_list():
    assert preload_profiles(base_url=OLLAMA_URL) == []
