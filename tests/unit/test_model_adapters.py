import os

import pytest

from src.llm.gpu_adapter import GPUAdapter
from src.llm.edge_adapter import EdgeAdapter


def test_edge_adapter_infer():
    a = EdgeAdapter(artifact_path="/tmp/fake")
    a.load()
    resp = a.infer("Hello world")
    assert "text" in resp
    assert isinstance(resp["text"], str)


def test_gpu_adapter_metadata_and_lazy_load(monkeypatch):
    # Ensure we don't try to download models during tests
    monkeypatch.setenv("LLM_SKIP_REAL_LOAD", "1")
    a = GPUAdapter(model_id="some/model")
    # Do not call load; ensure metadata works and lazy load returns stub
    meta = a.metadata()
    assert meta["profile"] == "gpu"
    # Call infer which will trigger the skip-real-load path and return a stub
    resp = a.infer("Test prompt for GPU")
    assert "text" in resp
    assert resp["text"].startswith("[gpu-stub]")
