"""Fetch a handful of reference audio clips for manually exercising the
transcription stage (`src/transcription`).

Source: Mozilla Common Voice, Dutch config ("nl"), validated split.
  https://commonvoice.mozilla.org/en/datasets
  https://huggingface.co/datasets/mozilla-foundation/common_voice_17_0

Common Voice is released under CC0 (public domain) — free to use, no
attribution required, no ToS/scraping concerns. It isn't healthcare-specific
(general read speech), which is a known gap: see the HoMed project
(https://aclanthology.org/2022.lrec-1.110/) for the closest published work on
open Dutch medical-domain ASR, and docs/agents/domain.md / docs/transcription.md
for how this repo's transcription stage should evolve if real clinical audio
becomes available.

Usage:
    uv sync --extra audio
    uv run python scripts/fetch_sample_audio.py

Downloaded clips are written to data/samples/ (git-ignored) and are NOT
committed to the repository.

Note: Hugging Face gates some Common Voice releases behind a click-through
license acceptance. If this script errors with a 401/403, accept the dataset
terms at the URL above while logged in, then run `huggingface-cli login`
(from the `huggingface_hub` package) and retry.
"""

import sys
from pathlib import Path


SAMPLE_COUNT = 3
OUTPUT_DIR = Path(__file__).resolve().parent.parent / "data" / "samples"


def main() -> None:
    try:
        import soundfile as sf
        from datasets import load_dataset
    except ImportError:
        print(
            "Missing optional dependencies. Install them with:\n    uv sync --extra audio",
            file=sys.stderr,
        )
        sys.exit(1)

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    print("Streaming Dutch validated clips from mozilla-foundation/common_voice_17_0 ...")
    try:
        dataset = load_dataset(
            "mozilla-foundation/common_voice_17_0",
            "nl",
            split="validated",
            streaming=True,
            trust_remote_code=True,
        )
    except Exception as e:
        print(
            f"Failed to open the dataset: {e}\n\n"
            "If this is an authentication/gating error, accept the dataset terms at\n"
            "https://huggingface.co/datasets/mozilla-foundation/common_voice_17_0\n"
            "then run `huggingface-cli login` and retry.",
            file=sys.stderr,
        )
        sys.exit(1)

    for i, example in enumerate(dataset.take(SAMPLE_COUNT)):
        audio = example["audio"]
        out_path = OUTPUT_DIR / f"common_voice_nl_{i:02d}.wav"
        sf.write(out_path, audio["array"], audio["sampling_rate"])
        sentence = example.get("sentence", "<no transcript in dataset>")
        print(f"Wrote {out_path} — reference transcript: {sentence!r}")

    print(f"\nDone. {SAMPLE_COUNT} clip(s) written to {OUTPUT_DIR}/")


if __name__ == "__main__":
    main()
