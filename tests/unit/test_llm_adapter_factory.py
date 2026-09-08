import pytest

from src.llm.edge_adapter import EdgeAdapter
from src.llm.gpu_adapter import GPUAdapter
from src.llm.llm_adapter_factory import create_adapter_instance
from src.llm.mock_adapter import MockAdapter


def test_create_adapter_instance_uses_default_profile_from_config():
    # config/llm_profiles.yml sets default_profile: edge
    adapter = create_adapter_instance()
    assert isinstance(adapter, EdgeAdapter)
    assert adapter.artifact_path == "/opt/models/j1-gguf.jl"


def test_create_adapter_instance_explicit_profile_uses_config_kwargs():
    adapter = create_adapter_instance("gpu")
    assert isinstance(adapter, GPUAdapter)
    assert adapter.model_id == "Juvoly/J1-Llama-8B-exp"
    assert adapter.torch_dtype == "float16"


def test_create_adapter_instance_explicit_kwargs_override_config():
    adapter = create_adapter_instance("gpu", model_id="other/model", torch_dtype="float32")
    assert isinstance(adapter, GPUAdapter)
    assert adapter.model_id == "other/model"
    assert adapter.torch_dtype == "float32"


def test_create_adapter_instance_mock_profile():
    adapter = create_adapter_instance("mock")
    assert isinstance(adapter, MockAdapter)


def test_create_adapter_instance_unknown_profile_raises_keyerror():
    with pytest.raises(KeyError):
        create_adapter_instance("does-not-exist")
