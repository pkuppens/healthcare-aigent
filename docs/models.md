# Swappable LLM Adapters

This project supports runtime selection of LLM adapters via `config/llm_profiles.yml`.
Profile selection has no environment-variable path by design.

Profiles:
- gpu: full model using Hugging Face transformers with GPU support (fp16/bf16/float32);
  requires the `healthcare-aigent[gpu]` extra (torch + transformers)
- edge: quantized / ggml / local runtime
- mock: test double with no real backend; use this in tests instead of
  skipping GPUAdapter/EdgeAdapter's real load

Select profile:

```python
from src.llm.llm_adapter_factory import create_adapter_instance

adapter = create_adapter_instance()        # uses default_profile from config/llm_profiles.yml
adapter = create_adapter_instance("gpu")   # explicit override, kwargs from config/llm_profiles.yml
adapter = create_adapter_instance("gpu", model_id="Juvoly/J1-Llama-8B-exp")  # explicit kwargs
```

`config/llm_profiles.yml` sets both the default profile and each profile's constructor
kwargs:

```yaml
default_profile: edge

profiles:
  gpu:
    model_id: "Juvoly/J1-Llama-8B-exp"
    torch_dtype: "float16"
  edge:
    artifact_path: "/opt/models/j1-gguf.jl"
```

Notes:
- The GPUAdapter implementation always performs a real load via the Hugging Face
  transformers library; it has no test/CI escape hatch. Use MockAdapter in tests
  instead of skipping the real load.
- The EdgeAdapter is a lightweight placeholder that should be extended to call a
  local runtime (ggml/gguf binary, Ollama, or an onnxruntime quantized model).
  Its `infer()` is pure simulation (`[edge-simulated] ...`) and current test/CI
  coverage of it is interface-conformance only (it implements the ModelAdapter
  ABC, and health_check() reflects whether load() ran) - not real inference
  correctness on any CPU/edge runtime. See
  [issue #9](https://github.com/pkuppens/healthcare-aigent/issues/9) for adding
  a dedicated CPUAdapter for CI/lightweight verification.

## Relationship to BaseLLM / LLMFactory

This adapter stack is deliberately standalone for now: it is not referenced from
`LLMFactory`, `ConfigManager`, or `src/llm/__init__.py`, and nothing in the app
(`api_server`, agents, `src/main.py`) constructs a `ModelAdapter`. The existing
`BaseLLM`/`LLMFactory` path (`src/llm/base.py`, `llm_factory.py`) is what
`src/main.py` hands to CrewAI's `Agent(llm=...)`, which requires LangChain's
`_call(prompt) -> str` shape - different from `ModelAdapter.infer(prompt) ->
dict`. See [issue #8](https://github.com/pkuppens/healthcare-aigent/issues/8)
for wiring a `ModelAdapter`-backed `BaseLLM` implementation into `LLMFactory`.
