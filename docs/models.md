# Local Clinical Models

The local model is chosen by **profile** in `config/llm_profiles.yml`. Ollama is the single
runtime for all of them; a profile is just a provider, an Ollama model tag and a few options.
`LLMFactory.create_from_profile()` turns a profile into an ordinary `BaseLLM`, so every profile
gets token usage and (optional) Langfuse tracing, and the task pipeline can use any of them.

Selection is config-file-only by design: there is no environment variable for it.

## Profiles

| Profile | Model (Ollama tag) | Weights | Runs on | Use it for |
|---|---|---|---|---|
| `edge` (default) | `medgemma1.5:4b` (Q4_K_M) | 3.3 GB | GPU with ≥ 6 GB VRAM, or CPU with ≥ 6 GB free RAM | Laptops; the default everywhere |
| `cpu` | `medgemma1.5:4b` (Q4_K_M), `num_gpu: 0` | 3.3 GB | CPU only | Laptops with no usable GPU; measuring the worst case |
| `gpu` | `medgemma:27b` (Q4_K_M) | 17 GB | GPU with ≥ 24 GB VRAM | Workstations; best answer quality |
| `mock` | none | 0 | anywhere | Tests |

Measured speed, memory and answer quality per profile: [model_eval.md](model_eval.md).

```bash
ollama pull medgemma1.5:4b    # edge, cpu
ollama pull medgemma:27b      # gpu
```

```python
from src.llm.llm_factory import LLMFactory, LLMType

llm = LLMFactory.create_from_profile()              # default_profile (edge)
llm = LLMFactory.create_from_profile("gpu")         # a named profile
llm = LLMFactory.create_from_profile("edge", num_ctx=2048)   # override a profile option
llm = LLMFactory.create_llm(LLMType.LOCAL_FAST)     # pipeline type -> edge profile
llm = LLMFactory.create_llm(LLMType.LOCAL_ACCURATE) # pipeline type -> gpu profile
```

If a profile's model has not been pulled, `create_from_profile` logs
`... run 'ollama pull <model>'` and the first call fails with Ollama's error.

### Small machines (about 6 GB)

- Use `edge` on a GPU with at least 6 GB of VRAM, otherwise `cpu`. `require_gpu: true` (the default)
  makes `edge` raise rather than run slowly when it doesn't fit on the GPU; set it to `false` in
  `config/llm_profiles.yml` to accept a partial offload with a warning instead.
- Keep `num_ctx` at 4096 or lower: the KV cache grows with context and is what pushes a 4B model
  past 6 GB.
- Close other models first. When VRAM is taken, Ollama falls back to the CPU or a partial
  offload without saying so. In the eval that cost about a factor 10 in speed (18 vs about 200
  tokens/s). Profile LLMs now detect this; see [GPU residency, cache and preload](#gpu-residency-cache-and-preload).
  You can also check with `ollama ps` (the `PROCESSOR` column).
- MedGemma 1.5 often writes a long reasoning block before its answer (see below). On a CPU that is
  most of the latency.

### GPU residency, cache and preload

This project is a single application that sometimes switches models, so it treats Ollama's model
cache as its own (`src/llm/ollama_residency.py`, #26). Every LLM built by `create_from_profile`
checks Ollama's `/api/ps` around each call:

- **`require_gpu`** (top-level default `true`, can be overridden per profile; `cpu` sets `false`).
  If the model is not 100% in VRAM after a call, the app raises `GPUResidencyError` with the
  model, its GPU share and the other resident models. With `false` it logs a warning instead.
- **`keep_alive`** (per profile, `30m` for the shipped profiles) is how long Ollama keeps an idle
  model loaded. A model that disappears *before* that expiry is logged as a warning ("Ollama
  evicted ... min before its keep_alive expiry"); a normal expiry is logged at info level. Ollama
  evicts idle models without notice to make room for another one.
- **Preload** loads profiles at a moment you choose, instead of on the first request (5–12 s on
  a GPU, about 20 s cold on a CPU). It loads the largest model first, with each profile's own
  options and keep_alive. It fails when two listed profiles share a model with different load
  options, when a model isn't pulled, or when the models don't all stay resident.

```python
from src.llm.ollama_residency import preload_profiles

preload_profiles()                 # the `preload:` list in config/llm_profiles.yml
preload_profiles(["gpu", "edge"])  # explicit; loads medgemma:27b first
```

Tested on an RTX 4090 (24 GB, about 1.5 GB already used by the desktop):

| Resident together | VRAM used | Result |
|---|---|---|
| `gpu` (27B @8K) + `edge` (4B @4K), 27B loaded first | 23.9 GB | Both 100% on the GPU through the full eval. Speed alone vs together: 27B 0.37 s vs 0.37 s, 4B 205 vs 194 tok/s |
| `edge` loaded first, then `gpu` | — | Ollama evicts the 4B: **load order matters**, so preload sorts largest first |
| `gpu` + `llama3.1:8b` | — | The 27B is evicted without notice; the app now logs this |
| `edge` + `cpu` | — | Impossible: Ollama keeps one instance per model name, so different `num_gpu`/`num_ctx` replaces it |

Headroom with `gpu` + `edge` is under 1 GB. A browser or other GPU app that grows can still
force an eviction, and you will see it as a warning on the next call. For the same reason,
overriding `num_ctx`/`num_gpu` per call (`create_from_profile("edge", num_ctx=2048)`) logs a
warning: it reloads the model.

**Windows:** `localhost` tries IPv6 first while Ollama listens on IPv4 only, so every new HTTP
connection to `http://localhost:11434` waits about 2 s. The residency checks reuse one pooled
session to avoid that. Setting `OLLAMA_BASE_URL=http://127.0.0.1:11434` avoids it everywhere.

### Adding or changing a profile

Add an entry under `profiles:` with `provider: ollama`, an Ollama `model` tag and optional
`options` (anything `ChatOllama` accepts: `num_ctx`, `num_gpu`, `num_predict`, ...), plus optional
`keep_alive` and `require_gpu` next to them.
Set `default_profile` to change the default. Run the eval on it before relying on it:

```bash
uv run python scripts/eval_models.py --profile <name>
```

## Models

### MedGemma 1.5 4B (`edge`, `cpu`)

- Hugging Face: <https://huggingface.co/google/medgemma-1.5-4b-it>; Ollama: <https://ollama.com/library/medgemma1.5>
- Gemma 3 architecture, 4.3B parameters, multimodal (text and medical images), 128K context.
  Released 2026-01 as a medical update of MedGemma 4B.
- Other tags: `4b-it-q8_0` (5.0 GB) and `4b-it-bf16` (8.6 GB). The eval compares bf16 with the
  default Q4_K_M.
- **Inline reasoning.** It often starts with `<unused94>thought ... <unused95>` before the answer.
  `OllamaLLM` strips that block (`strip_reasoning` in `src/llm/base.py`), so callers and the JSON
  tasks only see the answer, but the tokens are still generated and paid for in latency.

### MedGemma 27B (`gpu`)

- Hugging Face: <https://huggingface.co/google/medgemma-27b-it>; Ollama: <https://ollama.com/library/medgemma>
- Gemma 3, 27.4B parameters. The Ollama `medgemma:27b` tag is the **multimodal** 27B, not the
  text-only `medgemma-27b-text-it` whose MedQA score is usually quoted (86.2 in the MedGemma paper).
- 17 GB at Q4_K_M: fits a 24 GB GPU with an 8K context. Higher precision (q8, ~29 GB) does not.

### License: Health AI Developer Foundations terms

Both MedGemma models are under the [HAI-DEF terms of use](https://developers.google.com/health-ai-developer-foundations/terms),
not an open-source license. The parts that matter here:

- They exclude **Clinical Use** ("any use in diagnosis or treatment of patients, including as part
  of a research study") unless the user has the regulatory authorisations for it. This project is a
  development and evaluation environment. Its output is never a clinical decision, and the pipeline
  always sets `requires_human_review: true` (#23).
- Distribution, including offering the model as a hosted service, passes the terms on to recipients.
- Pulling from Ollama does not ask you to accept the gate that Hugging Face shows, but the terms apply all the same.

### Juvoly J1 (not used)

Issue #2 originally targeted `Juvoly/J1-Llama-8B-exp`. As of 2026-10 it is still `-exp`, last
updated 2025-05, has 0 downloads, and is published only as fp16 safetensors (~16 GB, gated,
Llama 3.1 Community License). It has no GGUF or Ollama build. Using it would mean a manual 16 GB
conversion. It was dropped in favour of MedGemma. Its base model `llama3.1:8b` is in the eval
as a general-model baseline. Rationale and reopen conditions: #24.

## Tests

- Unit tests (`tests/unit/test_llm_profiles.py`): profile parsing, factory wiring, option
  passthrough, and reasoning stripping. No Ollama needed; these run in CI.
- Real inference (`tests/integration/test_profile_inference.py`, marker `ollama`): one clinical
  question per profile. A profile's test skips itself when Ollama isn't running or its model isn't pulled.

```bash
uv run pytest -m ollama tests/integration/test_profile_inference.py
```
