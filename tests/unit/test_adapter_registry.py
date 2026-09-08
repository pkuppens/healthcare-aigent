import pytest

from src.llm.adapter_registry import get_adapter, register_adapter
from src.llm.model_adapter import ModelAdapter


def test_get_adapter_unregistered_raises_keyerror():
    with pytest.raises(KeyError):
        get_adapter("does-not-exist")


def test_register_and_get_adapter_roundtrip():
    class DummyAdapter(ModelAdapter):
        def load(self, *args, **kwargs) -> None: ...

        def infer(self, prompt: str, **options) -> dict:
            return {"text": prompt}

        def health_check(self) -> bool:
            return True

        def metadata(self) -> dict:
            return {}

    register_adapter("dummy-for-test", DummyAdapter)
    assert get_adapter("dummy-for-test") is DummyAdapter
