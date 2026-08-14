# Transcription Provider Research

Referenced from [transcription.md](transcription.md). `TranscriptionService`
(`src/transcription/base.py`) has one implementation today — OpenAI's hosted
Whisper API. This document is the place to research and record the tradeoffs
between that and the other candidate providers before picking what a real
deployment should use.

**Status: not yet performed.** This is the structure the research should
fill in, not a completed evaluation — the rows below are placeholders.

## Candidate providers

- **OpenAI Whisper API** (`whisper-1`) — implemented today
  (`src/transcription/openai_whisper.py`).
- **Local Whisper** (e.g. `faster-whisper`, `openai-whisper`) — self-hosted,
  no audio leaves the deployment, but needs GPU/CPU capacity planning.
- **AWS Transcribe** — see
  [transcription.md, Option 1.1](transcription.md#option-1--cloud-solutions)
  for why this is the leading cloud candidate for this project's
  eu-central-1 AWS architecture (also does speaker diarization natively).
- **Azure Speech-to-Text** — relevant if the deployment standardizes on
  Azure instead of AWS; EU data-residency options exist and need checking.
- **Google Cloud Speech-to-Text / Gemini audio input** — same category as
  Azure; EU data-residency and healthcare-data terms need checking.

## Evaluation dimensions

For each provider above, this research should record:

| Dimension | Notes |
|---|---|
| Transcription quality (esp. Dutch, medical terminology) | No medical-domain Dutch benchmark audio is freely available — see transcription.md's "Manually testing" section for what's used instead. |
| Speaker diarization support | Native vs. requires a separate pipeline stage (see transcription.md's diarization section). |
| Latency / throughput | Batch (offline) vs. streaming; matters for a live-consult use case vs. after-the-fact processing. |
| Cost | Per-minute pricing, at the volume this project would realistically run at. |
| Data residency / hosting region | EU hosting availability (eu-central-1 or equivalent). |
| Compliance / data processing agreement | Whether a signed verwerkersovereenkomst is available for this provider — see [compliance.md](compliance.md). |
| Local/self-hosted option | Whether a non-cloud path exists, and its infra cost. |

## Recommendation

Not yet made — depends on the results above. `docs/transcription.md`'s
"Swapping providers" section describes the mechanism (a new
`TranscriptionService` implementation, registered in
`src/transcription/factory.py`); this document is where the *choice* of
which one to build next should be justified once the research is done.
