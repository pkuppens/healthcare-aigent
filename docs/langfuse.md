# Langfuse (local, self-hosted) — LLM observability

Exploration tracked in epic #10. This page covers what has landed so far:

- **#11** — a local Langfuse stack via Docker Compose
- **#12** — optional, default-off Langfuse settings in the LLM config layer
- **#13** — every `BaseLLM` call recorded as one Langfuse *generation* (model, prompt, completion, tokens, latency)
- **#16** — client-side PII masking of everything sent to Langfuse (section 4)

Tracing the full pipeline as one trace (#14) and cost dashboards (#15) are not built yet.

> **Privacy.** Prompts and model output are masked before they leave the process (section 4), but
> the masking is best-effort. Keep the stack local (the compose file binds every port to
> `127.0.0.1`) and use synthetic conversations only. Tracing is off unless you turn it on.

## 1. Run Langfuse locally (#11)

Prerequisites: Docker with Compose v2. The stack is Langfuse web + worker, Postgres,
ClickHouse, Redis and MinIO (S3). It uses about **2.8 GiB RAM** when idle, plus about 2 GB of images on first pull.

```bash
docker compose -f docker-compose.langfuse.yml up -d      # start (first boot ~1 min, later ~20 s)
docker compose -f docker-compose.langfuse.yml ps         # all services should be healthy
curl http://localhost:3000/api/public/health             # -> {"status":"OK","version":"4.63.0"}
```

Open <http://localhost:3000> and log in. On first boot the stack bootstraps an org, a
project and API keys, so there is no sign-up step:

| What | Value (local-dev default) |
|---|---|
| Login | `admin@langfuse.local` / `langfuse-local-dev` |
| Project | `healthcare-aigent (local)` (id `healthcare-aigent-local`) |
| Public key | `pk-lf-local-dev` |
| Secret key | `sk-lf-local-dev` |

The keys are also visible under *Project settings → API keys*. To check them from a shell:

```bash
curl -u pk-lf-local-dev:sk-lf-local-dev http://localhost:3000/api/public/projects
```

Stop and reset:

```bash
docker compose -f docker-compose.langfuse.yml down      # stop, keep traces
docker compose -f docker-compose.langfuse.yml down -v   # reset: delete all data; keys are re-created on next up
```

To change ports, login or secrets, copy `.env.langfuse.example` to `.env.langfuse` (gitignored)
and add `--env-file .env.langfuse` to the commands above. Bootstrap values only apply to an
empty database, so run `down -v` after changing them.

Ports: UI on `127.0.0.1:3000`, MinIO on `127.0.0.1:9190`. MinIO is only used for media
attachments. Postgres, ClickHouse and Redis are not published, so they cannot clash with
another stack that uses 5432/6379.

**Scope:** this is a local exploration stack. The secrets are well-known defaults, and there
is no TLS, backups or SSO. A real deployment would go through `ansible/` and is out of scope for #10.

## 2. Turn tracing on (#12)

Install the optional extra, then set the env vars (see `.env.example`):

```bash
uv sync --extra observability
```

| Env var | Default | Meaning |
|---|---|---|
| `LANGFUSE_ENABLED` | `false` | Master switch. When false nothing is traced and `langfuse` is never imported. |
| `LANGFUSE_HOST` | `http://localhost:3000` | Langfuse base URL |
| `LANGFUSE_PUBLIC_KEY` / `LANGFUSE_SECRET_KEY` | unset | Project API keys. If either is missing, tracing stays off with one warning. |
| `LANGFUSE_SAMPLE_RATE` | `1.0` | Fraction of traces to keep |
| `LANGFUSE_DEBUG` | `false` | SDK debug logging |
| `LANGFUSE_MASK_PII` | `true` | Mask PII in every observation before export (section 4). Set `false` only for debugging with synthetic text. |

The same keys can be set in `config/llm_config.json` under `"langfuse"`, like the `openai`/`ollama`
sections. In code, `src.llm.observability.get_langfuse_client()` returns the shared client, or
`None` when tracing is off, keys are missing, or the extra is not installed. It never raises.

> `langfuse` and `langflow` cannot be installed together: `langflow` pins `langfuse==2.53.9`.
> `langflow` is therefore an optional extra too (`uv sync --extra langflow`, only needed for
> `src/langflow_poc/`), and the two extras are declared as conflicting in `pyproject.toml`.

## 3. Your first trace (#13)

Start Ollama first (the Ollama app, or `ollama serve`); check it with
`curl http://localhost:11434/api/version`. Then pull the default profile's model:

```bash
ollama pull medgemma1.5:4b
```

Without arguments the script uses the default profile from `config/llm_profiles.yml` (`edge`,
MedGemma 1.5 4B; see [models.md](models.md)). Use `--profile gpu` for MedGemma 27B, or
`--provider ollama --model <tag>` for any other model.

```bash
LANGFUSE_ENABLED=true LANGFUSE_PUBLIC_KEY=pk-lf-local-dev LANGFUSE_SECRET_KEY=sk-lf-local-dev \
  uv run python scripts/langfuse_smoke.py
```

PowerShell:

```powershell
$env:LANGFUSE_ENABLED="true"; $env:LANGFUSE_PUBLIC_KEY="pk-lf-local-dev"; $env:LANGFUSE_SECRET_KEY="sk-lf-local-dev"
uv run python scripts/langfuse_smoke.py
```

Windows cmd:

```bat
set LANGFUSE_ENABLED=true
set LANGFUSE_PUBLIC_KEY=pk-lf-local-dev
set LANGFUSE_SECRET_KEY=sk-lf-local-dev
uv run python scripts/langfuse_smoke.py
```

It prints the token usage, the answer, and a `trace_url=` you can open. Without
`LANGFUSE_ENABLED` the same command still calls the LLM and prints `langfuse=disabled (no trace sent)`.

![First trace: one ollama.generate generation, 77 tokens, 2.66 s](langfuse/first-trace.png)

What is recorded per call:

| Field | Source |
|---|---|
| name | `<provider>.generate`, e.g. `ollama.generate` |
| model, temperature | the `BaseLLM` instance |
| input / output | prompt / completion text |
| usage (input/output tokens) | LangChain `usage_metadata` from the provider response (Ollama and OpenAI) |
| latency | measured by the SDK |
| level ERROR + message | when the provider call raises (the exception is re-raised unchanged) |

How it hooks in: `BaseLLM.invoke`, `ainvoke`, `generate` and `__call__` all go through
`BaseLLM._traced_call`, which hands off to `src.llm.observability.observe_llm_call`. Every
provider, including the adapter-backed ones, is covered without provider-specific tracing code.

**Cost:** local models show *no cost*, because Langfuse has no price for `llama3.1:8b`. OpenAI models
should get a cost from Langfuse's built-in price list, but this has not been verified here (no
OpenAI key was available). Adding custom prices for local models is #15.

### Reading traces from the API (Langfuse v4)

Langfuse v4 runs in *events_only* mode, and the classic `GET /api/public/traces/{id}` returns
"not available". Use the Observations API v2 instead:

```bash
curl -u pk-lf-local-dev:sk-lf-local-dev \
  "http://localhost:3000/api/public/v2/observations?traceId=<trace_id>&fields=core,basic,usage,io,model&limit=10"
```

## 4. PII masking (#16)

The Langfuse client gets a `mask` callback (`src.llm.observability.langfuse_mask`), so the SDK
masks the input, output and metadata of every observation **before** export. The application
itself still sees the unmasked text; only what is sent to Langfuse is masked. The rules live in
`src/privacy/pii.py` (`mask_pii`, `mask_pii_data`) so a future cloud-LLM path can reuse them.

| Placeholder | What it matches |
|---|---|
| `[EMAIL]` | email addresses |
| `[PHONE]` | Dutch and international phone numbers (`06-12345678`, `+31 20 123 4567`) |
| `[BSN]` | nine digits that pass the BSN eleven-test (other nine-digit numbers are kept) |
| `[SSN]` | US SSN `123-45-6789` |
| `[IBAN]` | IBAN account numbers |
| `[DATE]` | full dates: `12-03-1958`, `1958-03-12`, `3 maart 1975`; this includes clinical dates, not only dates of birth |
| `[POSTCODE]` | Dutch postcodes `1234 AB` |
| `[ADDRESS]` | `Kerkstraat 12a`, `221 Baker Street` |
| `[NAME]` | a capitalised name after a cue: `Naam:`, `Name:`, `patiënt`, `patient`, `Dhr.`, `Mevr.`, `Mw.`, `Mr.`, `Mrs.`, `Ms.`, `Dr.` |

Check it against the local stack with a prompt that contains planted PII (the `mock` profile needs no Ollama):

```bash
uv run python scripts/langfuse_smoke.py --profile mock --prompt "Naam: Jan de Vries, BSN 111222333, tel 06-12345678"
```

Langfuse then stores `Naam: [NAME], BSN [BSN], tel [PHONE]` for both input and output, while
the script prints the unmasked answer.

**Limitations.** This is best-effort masking with regular expressions, not de-identification:

- names without a cue ("Jan had pain") are missed;
- city names and free-text identifiers are not masked;
- four digits followed by two capitals (`1500 MG`) can be masked as a postcode.

Server-side masking and data-retention policies are Langfuse Enterprise features. A real PHI
deployment would need them, or an NER-based de-identifier in front of `mask_pii`.
