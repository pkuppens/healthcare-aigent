# Swappable LLM Adapters

This project supports runtime selection of LLM adapters via `config/llm_profiles.yml`.
Profile selection has no environment-variable path by design.

Profiles:
- gpu: full model using Hugging Face transformers with GPU support (fp16/bf16/float32);
  requires the `healthcare-aigent[gpu]` extra (torch + transformers)
- edge: quantized / ggml / local runtime

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
- The GPUAdapter implementation will attempt to load models via the Hugging Face
  transformers library. Set `LLM_SKIP_REAL_LOAD=1` in CI or unit tests to avoid
  downloading large model artifacts during automated runs.
- The EdgeAdapter is a lightweight placeholder that should be extended to call a
  local runtime (ggml/gguf binary, Ollama, or an onnxruntime quantized model).
