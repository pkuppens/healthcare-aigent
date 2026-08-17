# Swappable LLM Adapters

This project supports runtime selection of LLM adapters via environment or configuration.

Profiles:
- gpu: full model using Hugging Face transformers with GPU support (fp16/bf16)
- edge: quantized / ggml / local runtime

Select profile:

```bash
export LLM_PROFILE=gpu
# or
export LLM_PROFILE=edge
```

See config/llm_profiles.yml for example profile configuration.

Notes:
- The GPUAdapter implementation will attempt to load models via the Hugging Face
  transformers library. Set `LLM_SKIP_REAL_LOAD=1` in CI or unit tests to avoid
  downloading large model artifacts during automated runs.
- The EdgeAdapter is a lightweight placeholder that should be extended to call a
  local runtime (ggml/gguf binary, Ollama, or an onnxruntime quantized model).
