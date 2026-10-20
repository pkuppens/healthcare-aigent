"""Unit tests for config-driven model profiles (issue #2): config/llm_profiles.yml -> LLMFactory."""

from unittest.mock import patch

import pytest
import requests

from src.llm.base import strip_reasoning
from src.llm.llm_factory import LLMFactory, LLMType
from src.llm.mock_llm import MockLLM
from src.llm.ollama_llm import OllamaLLM, is_model_available
from src.llm.profile_config import get_default_profile, get_profile


OLLAMA_URL = "http://ollama.test:11434"
OLLAMA_TAGS_URL = f"{OLLAMA_URL}/api/tags"


@pytest.fixture
def profiles_file(tmp_path):
    path = tmp_path / "llm_profiles.yml"
    path.write_text(
        "default_profile: small\n"
        "profiles:\n"
        "  small: {provider: ollama, model: 'tiny:1b', options: {num_ctx: 2048}}\n"
        "  no_model: {provider: ollama}\n"
        "  bad_options: {provider: ollama, model: 'x', options: [1, 2]}\n"
    )
    return path


def test_shipped_config_defaults_to_edge_medgemma():
    assert get_default_profile() == "edge"
    assert get_profile("edge") == {"provider": "ollama", "model": "medgemma1.5:4b", "options": {"num_ctx": 4096}}


def test_shipped_config_gpu_and_cpu_profiles():
    assert get_profile("gpu")["model"] == "medgemma:27b"
    cpu = get_profile("cpu")
    assert cpu["model"] == "medgemma1.5:4b"
    assert cpu["options"]["num_gpu"] == 0


def test_get_profile_reads_custom_file(profiles_file):
    assert get_default_profile(profiles_file) == "small"
    assert get_profile("small", profiles_file) == {"provider": "ollama", "model": "tiny:1b", "options": {"num_ctx": 2048}}


def test_get_profile_unknown_raises_keyerror(profiles_file):
    with pytest.raises(KeyError):
        get_profile("does-not-exist", profiles_file)


def test_get_profile_requires_model(profiles_file):
    with pytest.raises(ValueError, match="model"):
        get_profile("no_model", profiles_file)


def test_get_profile_rejects_non_mapping_options(profiles_file):
    with pytest.raises(ValueError, match="options"):
        get_profile("bad_options", profiles_file)


@patch("src.llm.llm_factory.is_model_available", return_value=True)
@patch("src.llm.ollama_llm.ChatOllama")
def test_create_from_profile_passes_model_and_options_to_ollama(mock_chat_ollama, _available):
    llm = LLMFactory.create_from_profile("cpu", temperature=0.1)

    assert isinstance(llm, OllamaLLM)
    assert llm.model_name == "medgemma1.5:4b"
    kwargs = mock_chat_ollama.call_args.kwargs
    assert kwargs["model"] == "medgemma1.5:4b"
    assert kwargs["temperature"] == 0.1
    assert kwargs["num_ctx"] == 4096
    assert kwargs["num_gpu"] == 0


@patch("src.llm.llm_factory.is_model_available", return_value=True)
@patch("src.llm.ollama_llm.ChatOllama")
def test_create_from_profile_kwargs_override_options(mock_chat_ollama, _available):
    LLMFactory.create_from_profile("edge", num_ctx=1024)

    assert mock_chat_ollama.call_args.kwargs["num_ctx"] == 1024


@patch("src.llm.llm_factory.is_model_available", return_value=True)
@patch("src.llm.ollama_llm.ChatOllama")
def test_create_from_profile_defaults_to_default_profile(mock_chat_ollama, _available):
    llm = LLMFactory.create_from_profile()

    assert llm.model_name == "medgemma1.5:4b"


@patch("src.llm.llm_factory.is_model_available", return_value=False)
@patch("src.llm.ollama_llm.ChatOllama")
def test_create_from_profile_warns_when_model_missing(mock_chat_ollama, _available, caplog):
    LLMFactory.create_from_profile("gpu")

    assert "ollama pull medgemma:27b" in caplog.text


def test_create_from_profile_mock_needs_no_runtime():
    llm = LLMFactory.create_from_profile("mock")

    assert isinstance(llm, MockLLM)
    assert llm.provider == "mock"
    assert llm.invoke("hi") == "[mock] hi"


@pytest.mark.parametrize(
    ("llm_type", "model", "temperature"),
    [(LLMType.LOCAL_FAST, "medgemma1.5:4b", 0.7), (LLMType.LOCAL_ACCURATE, "medgemma:27b", 0.5)],
)
@patch("src.llm.llm_factory.is_model_available", return_value=True)
@patch("src.llm.ollama_llm.ChatOllama")
def test_local_llm_types_resolve_from_profiles(mock_chat_ollama, _available, llm_type, model, temperature):
    llm = LLMFactory.create_llm(llm_type)

    assert llm.model_name == model
    assert llm.temperature == temperature


def test_is_model_available_matches_pulled_tags(requests_mock):
    requests_mock.get(OLLAMA_TAGS_URL, json={"models": [{"name": "medgemma1.5:4b"}, {"name": "llama3:latest"}]})

    assert is_model_available("medgemma1.5:4b", OLLAMA_URL) is True
    assert is_model_available("llama3", OLLAMA_URL) is True
    assert is_model_available("medgemma:27b", OLLAMA_URL) is False


def test_is_model_available_false_when_ollama_unreachable(requests_mock):
    requests_mock.get(OLLAMA_TAGS_URL, exc=requests.exceptions.ConnectionError)

    assert is_model_available("medgemma1.5:4b", OLLAMA_URL) is False


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        ("<unused94>thought\nLet me reason.<unused95>B", "B"),
        ("<unused94> thought\nstill thinking, no close", "still thinking, no close"),
        ('<think>hmm</think>\n{"a": 1}', '{"a": 1}'),
        ("plain answer", "plain answer"),
    ],
)
def test_strip_reasoning(raw, expected):
    assert strip_reasoning(raw) == expected


@patch("src.llm.ollama_llm.ChatOllama")
def test_ollama_llm_returns_answer_without_medgemma_thinking(mock_chat_ollama):
    mock_chat_ollama.return_value.invoke.return_value.content = "<unused94>thought\nreasoning<unused95>Amlodipine"
    mock_chat_ollama.return_value.invoke.return_value.usage_metadata = None

    assert OllamaLLM(model_name="medgemma1.5:4b").invoke("q") == "Amlodipine"
