"""Unit tests for the optional Langfuse config and tracing (issues #12, #13).

None of these talk to a Langfuse server: the client is faked, so they run in CI with or
without the `observability` extra installed.
"""

import sys
from contextlib import contextmanager
from types import SimpleNamespace
from typing import Any

import pytest

from src.llm import observability
from src.llm.base import BaseLLM, usage_from_response
from src.llm.config import ConfigManager, LangfuseConfig, LLMConfig


LANGFUSE_ENV = [
    "LANGFUSE_ENABLED",
    "LANGFUSE_HOST",
    "LANGFUSE_PUBLIC_KEY",
    "LANGFUSE_SECRET_KEY",
    "LANGFUSE_SAMPLE_RATE",
    "LANGFUSE_DEBUG",
    "LANGFUSE_MASK_PII",
]


@pytest.fixture
def clean_env(monkeypatch, tmp_path):
    """No Langfuse env vars, and no config file on disk."""
    for name in LANGFUSE_ENV:
        monkeypatch.delenv(name, raising=False)
    monkeypatch.setenv("LLM_CONFIG_FILE", str(tmp_path / "missing.json"))


@pytest.fixture
def langfuse_config(monkeypatch):
    """Swap in a fresh LangfuseConfig on the ConfigManager singleton and reset the client cache."""
    config = LLMConfig()
    monkeypatch.setattr(ConfigManager(), "_config", config)
    observability.reset_langfuse_client()
    yield config.langfuse
    observability.reset_langfuse_client()


class FakeGeneration:
    def __init__(self, **kwargs: Any):
        self.start_kwargs = kwargs
        self.updates: list[dict] = []
        self.trace_id = "trace-123"

    def update(self, **kwargs: Any) -> None:
        self.updates.append(kwargs)


class FakeLangfuse:
    def __init__(self):
        self.generations: list[FakeGeneration] = []

    @contextmanager
    def start_as_current_observation(self, **kwargs: Any):
        generation = FakeGeneration(**kwargs)
        self.generations.append(generation)
        yield generation


class EchoLLM(BaseLLM):
    """Minimal BaseLLM that reports usage the way OllamaLLM/OpenAILLM do."""

    def __init__(self, fail: bool = False):
        super().__init__(model_name="echo-model", temperature=0.2)
        self._fail = fail

    def _call(self, prompt: str, stop=None, run_manager=None, **kwargs: Any) -> str:
        if self._fail:
            raise RuntimeError("provider down")
        self.last_usage = {"input_tokens": 3, "output_tokens": 5}
        return f"echo: {prompt}"

    def _llm_type(self) -> str:
        return "echo"

    @property
    def provider(self) -> str:
        return "echo"


# --- config (#12) -------------------------------------------------------------------------


def test_langfuse_is_disabled_by_default(clean_env):
    config = ConfigManager()._load_config()

    assert config.langfuse == LangfuseConfig()
    assert config.langfuse.enabled is False


def test_langfuse_config_is_read_from_env(clean_env, monkeypatch):
    monkeypatch.setenv("LANGFUSE_ENABLED", "TRUE")
    monkeypatch.setenv("LANGFUSE_HOST", "http://langfuse.internal:3000")
    monkeypatch.setenv("LANGFUSE_PUBLIC_KEY", "pk-test")
    monkeypatch.setenv("LANGFUSE_SECRET_KEY", "sk-test")
    monkeypatch.setenv("LANGFUSE_SAMPLE_RATE", "0.25")
    monkeypatch.setenv("LANGFUSE_DEBUG", "true")
    monkeypatch.setenv("LANGFUSE_MASK_PII", "false")

    config = ConfigManager()._load_config().langfuse

    assert config == LangfuseConfig(
        enabled=True,
        host="http://langfuse.internal:3000",
        public_key="pk-test",
        secret_key="sk-test",
        sample_rate=0.25,
        debug=True,
        mask_pii=False,
    )


def test_langfuse_config_is_read_from_config_file(clean_env, monkeypatch, tmp_path):
    config_file = tmp_path / "llm_config.json"
    config_file.write_text('{"langfuse": {"enabled": true, "public_key": "pk-file", "sample_rate": 0.5}}')
    monkeypatch.setenv("LLM_CONFIG_FILE", str(config_file))

    config = ConfigManager()._load_config().langfuse

    assert config.enabled is True
    assert config.public_key == "pk-file"
    assert config.sample_rate == 0.5
    assert config.secret_key is None


# --- client helper (#12) ------------------------------------------------------------------


def test_client_is_none_when_disabled_and_langfuse_is_not_imported(langfuse_config, monkeypatch):
    for name in [m for m in sys.modules if m == "langfuse" or m.startswith("langfuse.")]:
        monkeypatch.delitem(sys.modules, name)

    assert observability.get_langfuse_client() is None
    assert "langfuse" not in sys.modules


def test_client_is_none_when_keys_are_missing(langfuse_config):
    langfuse_config.enabled = True

    assert observability.get_langfuse_client() is None


def test_client_is_none_when_langfuse_is_not_installed(langfuse_config, monkeypatch):
    langfuse_config.enabled = True
    langfuse_config.public_key = "pk-test"
    langfuse_config.secret_key = "sk-test"
    monkeypatch.setitem(sys.modules, "langfuse", None)  # makes `import langfuse` raise ImportError

    assert observability.get_langfuse_client() is None


def test_client_is_built_from_config_when_enabled(langfuse_config, monkeypatch):
    langfuse_config.enabled = True
    langfuse_config.public_key = "pk-test"
    langfuse_config.secret_key = "sk-test"
    langfuse_config.sample_rate = 0.5
    constructed = []
    monkeypatch.setitem(sys.modules, "langfuse", SimpleNamespace(Langfuse=lambda **kw: constructed.append(kw) or "client"))

    assert observability.get_langfuse_client() == "client"
    assert observability.get_langfuse_client() == "client"  # cached, not rebuilt
    assert constructed == [
        {
            "public_key": "pk-test",
            "secret_key": "sk-test",
            "host": "http://localhost:3000",
            "sample_rate": 0.5,
            "debug": False,
            "mask": observability.langfuse_mask,
        }
    ]


def test_client_is_built_without_mask_when_masking_is_off(langfuse_config, monkeypatch):
    """LANGFUSE_MASK_PII=false is an explicit opt-out: the client gets no mask callback."""
    langfuse_config.enabled = True
    langfuse_config.public_key = "pk-test"
    langfuse_config.secret_key = "sk-test"
    langfuse_config.mask_pii = False
    constructed = []
    monkeypatch.setitem(sys.modules, "langfuse", SimpleNamespace(Langfuse=lambda **kw: constructed.append(kw) or "client"))

    observability.get_langfuse_client()

    assert constructed[0]["mask"] is None


# --- tracing a single call (#13) ----------------------------------------------------------


def test_invoke_without_langfuse_just_calls_the_llm(langfuse_config):
    llm = EchoLLM()

    assert llm.invoke("hi") == "echo: hi"
    assert observability.get_last_trace_id() is None


def test_invoke_records_one_generation_with_usage(langfuse_config, monkeypatch):
    fake = FakeLangfuse()
    monkeypatch.setattr(observability, "get_langfuse_client", lambda: fake)

    assert EchoLLM().invoke("hi") == "echo: hi"

    assert len(fake.generations) == 1
    generation = fake.generations[0]
    assert generation.start_kwargs == {
        "as_type": "generation",
        "name": "echo.generate",
        "model": "echo-model",
        "model_parameters": {"temperature": 0.2},
        "input": "hi",
        "metadata": {"provider": "echo"},
    }
    assert generation.updates == [{"output": "echo: hi", "usage_details": {"input": 3, "output": 5}}]
    assert observability.get_last_trace_id() == "trace-123"


@pytest.mark.asyncio
async def test_ainvoke_is_traced_like_invoke(langfuse_config, monkeypatch):
    fake = FakeLangfuse()
    monkeypatch.setattr(observability, "get_langfuse_client", lambda: fake)

    assert await EchoLLM().ainvoke("hi") == "echo: hi"
    assert len(fake.generations) == 1


def test_failed_call_is_recorded_as_error_and_reraised(langfuse_config, monkeypatch):
    fake = FakeLangfuse()
    monkeypatch.setattr(observability, "get_langfuse_client", lambda: fake)

    with pytest.raises(RuntimeError, match="provider down"):
        EchoLLM(fail=True).invoke("hi")

    assert fake.generations[0].updates == [{"level": "ERROR", "status_message": "provider down"}]


def test_usage_from_response_reads_langchain_usage_metadata():
    response = SimpleNamespace(usage_metadata={"input_tokens": 29, "output_tokens": 48, "total_tokens": 77})

    assert usage_from_response(response) == {"input_tokens": 29, "output_tokens": 48}
    assert usage_from_response(SimpleNamespace(usage_metadata=None)) is None
    assert usage_from_response("plain string") is None
