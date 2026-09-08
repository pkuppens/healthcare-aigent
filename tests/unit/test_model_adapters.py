import pytest
import torch

from src.llm.edge_adapter import EdgeAdapter
from src.llm.gpu_adapter import GPUAdapter
from src.llm.mock_adapter import MockAdapter


def test_edge_adapter_infer():
    a = EdgeAdapter(artifact_path="/tmp/fake")
    a.load()
    resp = a.infer("Hello world")
    assert "text" in resp
    assert isinstance(resp["text"], str)


def test_edge_adapter_health_check_reflects_load():
    a = EdgeAdapter(artifact_path="/tmp/fake")
    assert a.health_check() is False
    a.load()
    assert a.health_check() is True


def test_gpu_adapter_rejects_unknown_dtype():
    with pytest.raises(ValueError):
        GPUAdapter(model_id="some/model", torch_dtype="int8")


def test_gpu_adapter_load_and_infer(monkeypatch):
    # GPUAdapter always performs a real load (no test/CI escape hatch), so we
    # stand in for the transformers backend rather than skipping the load.
    import transformers

    class FakeTokenizer:
        def __call__(self, prompt, return_tensors="pt"):
            return {"input_ids": torch.tensor([[1, 2, 3]])}

        def decode(self, ids, skip_special_tokens=True):
            return "fake output"

    class FakeModel:
        def parameters(self):
            return iter([torch.nn.Parameter(torch.zeros(1))])

        def generate(self, **kwargs):
            return torch.tensor([[1, 2, 3, 4]])

    monkeypatch.setattr(transformers.AutoTokenizer, "from_pretrained", lambda *a, **k: FakeTokenizer())
    monkeypatch.setattr(transformers.AutoModelForCausalLM, "from_pretrained", lambda *a, **k: FakeModel())

    a = GPUAdapter(model_id="some/model")
    meta = a.metadata()
    assert meta["profile"] == "gpu"
    assert a.health_check() is False

    resp = a.infer("Test prompt for GPU")
    assert resp["text"] == "fake output"
    assert a.health_check() is True


def test_mock_adapter_infer_and_health_check():
    a = MockAdapter()
    assert a.metadata()["profile"] == "mock"
    assert a.health_check() is False

    resp = a.infer("hello")
    assert resp["text"] == "[mock] hello"
    assert a.health_check() is True
