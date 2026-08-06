# Transcription Stage

`src/transcription/` turns a recorded consultation into text, as the first
stage ahead of the existing agent/task pipeline (preprocess → assess
language → extract clinical info → summarize → quality control).

## Interface

`TranscriptionService` (`src/transcription/base.py`) is a one-method
interface — `async def transcribe(audio_path, language=None) -> str` —
mirroring the `BaseLLM` provider abstraction in `src/llm/`. The only
implementation today is `OpenAIWhisperTranscription`
(`src/transcription/openai_whisper.py`), which calls OpenAI's hosted
`whisper-1` model.

This is a showcase stub, not a production transcription pipeline. See
[compliance.md](compliance.md) for why sending real patient audio through it
as-is would be a problem.

**Swapping providers**: a real deployment would likely replace this with a
provider that fits the eu-central-1 / multi-tenant AWS setup — e.g. AWS
Transcribe, or a self-hosted Whisper deployment. That's a new
`TranscriptionService` implementation; nothing else in the pipeline changes.

## Entry points

- `process_audio_conversation_async(audio_path, ...)` in `src/main.py` —
  transcribes, then runs the same task pipeline as the text-only entry
  point, returning the transcript alongside the structured results.
- `POST /transcribe_and_process/` in `src/api/api_server.py` — the HTTP
  equivalent, accepting a multipart file upload.

## Manually testing with reference audio

There's no medical-domain Dutch audio that's both public and freely
licensed (see below), so `scripts/fetch_sample_audio.py` pulls general-domain
Dutch speech from Mozilla Common Voice (CC0) for manual testing of the
transcription stage:

```bash
uv sync --extra audio
uv run python scripts/fetch_sample_audio.py
```

This writes a few `.wav` clips to `data/samples/` (git-ignored — not
committed). Then, with `OPENAI_API_KEY` set:

```python
import asyncio
from src.main import process_audio_conversation_async

result = asyncio.run(process_audio_conversation_async("data/samples/common_voice_nl_00.wav"))
print(result["transcript"])
```

**On domain fit**: Common Voice is general read speech, not medical
dialogue — it exercises the transcription *wiring*, not medical-terminology
accuracy. For the closest published work on open Dutch medical-domain ASR,
see the HoMed project (Homo Medicinalis):
<https://aclanthology.org/2022.lrec-1.110/>. Publicly available medical
consultation audio in Dutch is scarce; the datasets that exist
(e.g. FutureBeeAI's healthcare call-center Dutch corpus) are commercial.

## Next step: speaker diarization

**Not implemented.** `OpenAIWhisperTranscription` calls `whisper-1`, which
returns one undifferentiated block of text — no "who said this" information.
That's a real gap here, not a cosmetic one: a GGZ consult report needs to
distinguish behandelaar from patiënt, and `tests/conftest.py`'s
`mock_transcript` fixture already models the target shape
(`Spreker A: ... / Spreker B: ...`) that nothing upstream currently produces.

### Option 1 — AWS Transcribe (most relevant for this job's architecture)

Since the target deployment is AWS eu-central-1, AWS Transcribe is the
natural production choice over a self-managed OSS pipeline: it does
transcription *and* speaker diarization in one call
(`ShowSpeakerLabels=True` / `Settings.ShowSpeakerLabels` in the
`start_transcription_job` API), runs inside the AWS account and region
already in scope, and its data handling is covered by AWS's standard data
processing terms rather than a separate third-party agreement. This would
likely be the right implementation to add as a second `TranscriptionService`
alongside (or instead of) the OpenAI one, returning speaker-labeled segments.

### Option 2 — Open-source, for a self-hosted / non-AWS path

- **[WhisperX](https://github.com/m-bain/whisperX)** — wraps faster-whisper
  with forced word-level alignment and integrates `pyannote.audio` for
  diarization in one pipeline; the most common off-the-shelf combination for
  "Whisper transcript + speaker labels."
- **[pyannote.audio](https://github.com/pyannote/pyannote-audio)** — the
  diarization engine WhisperX (and most others) build on. Can also be run
  standalone and its speaker segments merged with any ASR output's
  timestamps after the fact. Pretrained pipeline:
  `pyannote/speaker-diarization-3.1` on Hugging Face (gated, free to accept).
- **[NVIDIA NeMo](https://github.com/NVIDIA/NeMo)** speaker diarization
  toolkit — more heavyweight (GPU-oriented), relevant if the deployment
  already standardizes on NeMo/Riva for ASR.

### Interface impact

`TranscriptionService.transcribe` currently returns `str`. Diarization
requires returning structured turns instead — e.g. a small
`TranscriptSegment(speaker: str, text: str, start: float, end: float)` list
— which is a breaking change to the interface, not an additive one. Worth
making before wiring a second provider, so both implementations share the
same richer contract from the start rather than retrofitting it.
