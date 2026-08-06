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
