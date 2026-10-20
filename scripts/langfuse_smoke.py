"""Send one prompt through LLMFactory and, if Langfuse is enabled, print the resulting trace (issue #13).

Usage (with the local stack from docker-compose.langfuse.yml running; see docs/langfuse.md):

    LANGFUSE_ENABLED=true LANGFUSE_PUBLIC_KEY=pk-lf-local-dev LANGFUSE_SECRET_KEY=sk-lf-local-dev \\
        uv run python scripts/langfuse_smoke.py                    # default profile (edge: medgemma1.5:4b)
        uv run python scripts/langfuse_smoke.py --profile gpu      # any profile in config/llm_profiles.yml
        uv run python scripts/langfuse_smoke.py --provider ollama --model llama3.1:8b   # explicit model

With LANGFUSE_ENABLED unset the LLM call still runs, but no trace is sent and `langfuse` is
not imported. The prompt is synthetic: never point this at real patient text.
"""

import argparse
import sys

import httpx

from src.llm.llm_factory import LLMFactory
from src.llm.observability import get_langfuse_client, get_last_trace_id


SMOKE_PROMPT = "In one sentence: what is a beta blocker such as metoprolol commonly prescribed for?"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--profile", help="Profile from config/llm_profiles.yml (default: its default_profile)")
    parser.add_argument("--provider", choices=["ollama", "openai"], help="With --model: bypass the profiles")
    parser.add_argument("--model", help="With --provider: explicit model name")
    args = parser.parse_args()
    if bool(args.provider) != bool(args.model):
        parser.error("--provider and --model go together")

    if args.model:
        llm = LLMFactory.create_llm_by_provider(args.provider, args.model, temperature=0.0)
    else:
        llm = LLMFactory.create_from_profile(args.profile, temperature=0.0)
    try:
        output = llm.invoke(SMOKE_PROMPT)
    except httpx.ConnectError as exc:
        if llm.provider != "ollama":
            raise
        print(
            f"error: cannot reach Ollama ({exc}).\n"
            "Start it first: launch the Ollama app, or run `ollama serve` in another terminal.\n"
            "Check with: curl http://localhost:11434/api/version (or your OLLAMA_BASE_URL)",
            file=sys.stderr,
        )
        return 1
    print(f"provider={llm.provider} model={llm.model_name}")
    print(f"usage={llm.last_usage}")
    print(f"output={output!r}")

    client = get_langfuse_client()
    if client is None:
        print("langfuse=disabled (no trace sent)")
        return 0

    client.flush()
    trace_id = get_last_trace_id()
    print(f"trace_id={trace_id}")
    print(f"trace_url={client.get_trace_url(trace_id=trace_id)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
