from src.llm.adapter_backed_llm import AdapterBackedLLM
from src.llm.llm_factory import LLMFactory
from src.llm.mock_adapter import MockAdapter


def test_adapter_backed_llm_calls_through_to_adapter():
    llm = AdapterBackedLLM(MockAdapter(), model_name="mock-model")

    result = llm.invoke("hello")

    assert result == "[mock] hello"
    assert llm.provider == "mock"
    assert llm._llm_type() == "adapter:mock"


def test_adapter_backed_llm_loads_lazily():
    adapter = MockAdapter()
    llm = AdapterBackedLLM(adapter, model_name="mock-model")

    assert adapter.health_check() is False
    llm.invoke("hello")
    assert adapter.health_check() is True


def test_llm_factory_create_from_adapter_profile_uses_mock_registry():
    llm = LLMFactory.create_from_adapter_profile("mock")

    assert isinstance(llm, AdapterBackedLLM)
    assert llm.provider == "mock"
    assert llm.invoke("hi") == "[mock] hi"
