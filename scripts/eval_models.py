"""Run the synthetic clinical eval set (eval/clinical_eval.yml) against a model profile or Ollama model (issue #2).

Usage:

    uv run python scripts/eval_models.py --profile edge
    uv run python scripts/eval_models.py --model llama3.1:8b --label llama3.1-8b
    uv run python scripts/eval_models.py --summary     # markdown table from all saved runs

Each run writes tmp/analysis/eval-<label>.json with per-item correctness, latency and token counts,
plus the loaded model's size and VRAM share from Ollama's /api/ps. Calls go through LLMFactory, so
they are traced in Langfuse when LANGFUSE_ENABLED=true. The eval set is synthetic: never add real
patient text to it.
"""

import argparse
import json
import os
import re
import sys
import time
from pathlib import Path
from typing import Any

import requests
import yaml

from src.llm.base import BaseLLM
from src.llm.llm_factory import LLMFactory


ROOT = Path(__file__).resolve().parents[1]
EVAL_SET = ROOT / "eval" / "clinical_eval.yml"
RESULTS_DIR = ROOT / "tmp" / "analysis"

# Tried in order; within a pattern the last match wins (models restate options before concluding).
_LETTER_PATTERNS = (
    r"boxed\{\s*([A-D])\s*\}",  # LaTeX: "The final answer is $\boxed{B}$"
    r"(?:final answer|answer is|answer:|option is)\W*(?:is\W*)?\(?([A-D])\b",  # "The answer is B", "Answer: (B)"
    r"^\W*([A-D])\W*$",  # a line holding just the letter: "B", "**C**", "(A)"
    r"\A\W*([A-D])\b",  # answer starts with the letter: "B) Beta blocker"
)


def extract_letter(answer: str) -> str | None:
    """Return the option letter a model chose, or None if it can't be found."""
    for pattern in _LETTER_PATTERNS:
        matches = re.findall(pattern, answer.strip(), flags=re.IGNORECASE | re.MULTILINE)
        if matches:
            return matches[-1].upper()
    return None


def parse_json_object(answer: str) -> dict[str, Any] | None:
    """Parse the first {...} block in `answer` (models often wrap JSON in ```json fences)."""
    match = re.search(r"\{.*\}", answer, flags=re.DOTALL)
    if not match:
        return None
    try:
        data = json.loads(match.group(0))
    except json.JSONDecodeError:
        return None
    return data if isinstance(data, dict) else None


def build_prompt(item: dict[str, Any], eval_set: dict[str, Any]) -> str:
    if item["kind"] == "mcq":
        options = "\n".join(f"{letter}) {text}" for letter, text in item["options"].items())
        return f"{eval_set['mcq_instruction']}\n\n{item['question']}\n{options}"
    if item["kind"] == "extraction":
        return f"{eval_set['extraction_instruction']}\n\nConsultation:\n{item['text']}"
    return item["prompt"]


def score(item: dict[str, Any], answer: str, eval_set: dict[str, Any]) -> dict[str, Any]:
    if item["kind"] == "mcq":
        letter = extract_letter(answer)
        return {"chosen": letter, "correct": letter == item["answer"]}
    if item["kind"] == "extraction":
        data = parse_json_object(answer)
        text = json.dumps(data, ensure_ascii=False).lower() if data else answer.lower()
        hits = [kw for kw in item["expected_keywords"] if re.search(kw, text, flags=re.IGNORECASE)]
        recall = len(hits) / len(item["expected_keywords"])
        return {"valid_json": data is not None, "keyword_recall": recall, "correct": data is not None and recall == 1.0}
    escalation = item.get("required", eval_set["escalation_pattern"])
    escalates = re.search(escalation, answer, flags=re.IGNORECASE) is not None
    violations = [p for p in item.get("forbidden", []) if re.search(p, answer, flags=re.IGNORECASE)]
    return {"escalates": escalates, "violations": violations, "correct": escalates and not violations}


def unload_all_models() -> None:
    """Unload every model Ollama holds, so a previous run's model can't push this one onto the CPU."""
    base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    try:
        running = requests.get(f"{base_url}/api/ps", timeout=5).json().get("models", [])
        for entry in running:
            requests.post(f"{base_url}/api/generate", json={"model": entry["name"], "keep_alive": 0}, timeout=60)
    except requests.RequestException:
        pass


def loaded_model_memory(model: str) -> dict[str, int] | None:
    """Size and VRAM share of `model` as currently loaded by Ollama, in bytes."""
    base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    try:
        running = requests.get(f"{base_url}/api/ps", timeout=5).json().get("models", [])
    except requests.RequestException:
        return None
    for entry in running:
        if entry.get("name") == model or entry.get("model") == model:
            return {"size": entry.get("size", 0), "size_vram": entry.get("size_vram", 0)}
    return None


def timed_invoke(llm: BaseLLM, prompt: str) -> tuple[str, float]:
    start = time.perf_counter()
    answer = llm.invoke(prompt)
    return answer, time.perf_counter() - start


def run(llm: BaseLLM, label: str, items: list[dict[str, Any]], eval_set: dict[str, Any]) -> dict[str, Any]:
    unload_all_models()
    # Warm-up call: measures cold-load time and keeps it out of the per-item latencies.
    _, load_seconds = timed_invoke(llm, "Reply with OK.")
    memory = loaded_model_memory(llm.model_name)

    results = []
    for item in items:
        answer, seconds = timed_invoke(llm, build_prompt(item, eval_set))
        usage = llm.last_usage or {}
        result = {"id": item["id"], "kind": item["kind"], "seconds": round(seconds, 2), **usage, **score(item, answer, eval_set)}
        result["answer"] = answer
        results.append(result)
        print(
            f"  {item['id']:<28} {'PASS' if result['correct'] else 'FAIL'}  {seconds:6.1f}s  {usage.get('output_tokens', '?')} tok"
        )

    return {"label": label, "model": llm.model_name, "load_seconds": round(load_seconds, 1), "memory": memory, "items": results}


def summarize(run_result: dict[str, Any]) -> dict[str, Any]:
    items = run_result["items"]

    def pass_rate(kind: str) -> str:
        subset = [r for r in items if r["kind"] == kind]
        return f"{sum(r['correct'] for r in subset)}/{len(subset)}"

    seconds = sorted(r["seconds"] for r in items)
    out_tokens = sum(r.get("output_tokens", 0) for r in items)
    memory = run_result.get("memory") or {}
    size_gb = memory.get("size", 0) / 1e9
    gpu_share = memory.get("size_vram", 0) / memory["size"] if memory.get("size") else 0.0
    return {
        "label": run_result["label"],
        "model": run_result["model"],
        "mcq": pass_rate("mcq"),
        "extraction": pass_rate("extraction"),
        "safety": pass_rate("safety"),
        "median_s": seconds[len(seconds) // 2],
        "max_s": seconds[-1],
        "tok_per_s": round(out_tokens / sum(seconds), 1) if sum(seconds) else 0.0,
        "mean_out_tok": round(out_tokens / len(items)),
        "loaded_gb": round(size_gb, 1),
        "gpu_share": f"{gpu_share:.0%}",
        "load_s": run_result["load_seconds"],
    }


def rescore_saved_runs(eval_set: dict[str, Any]) -> None:
    """Re-score saved answers after a scoring change, without calling any model again."""
    items_by_id = {item["id"]: item for item in eval_set["items"]}
    for path in sorted(RESULTS_DIR.glob("eval-*.json")):
        run_result = json.loads(path.read_text(encoding="utf-8"))
        for result in run_result["items"]:
            for key in ("chosen", "valid_json", "keyword_recall", "escalates", "violations"):
                result.pop(key, None)
            result.update(score(items_by_id[result["id"]], result["answer"], eval_set))
        path.write_text(json.dumps(run_result, indent=2, ensure_ascii=False), encoding="utf-8")
        print(f"Rescored {path.name}")


def print_summary_table() -> None:
    rows = [summarize(json.loads(p.read_text(encoding="utf-8"))) for p in sorted(RESULTS_DIR.glob("eval-*.json"))]
    if not rows:
        print(f"No results in {RESULTS_DIR}")
        return
    headers = list(rows[0])
    print("| " + " | ".join(headers) + " |")
    print("|" + "---|" * len(headers))
    for row in rows:
        print("| " + " | ".join(str(row[h]) for h in headers) + " |")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    target = parser.add_mutually_exclusive_group(required=True)
    target.add_argument("--profile", help="Profile name from config/llm_profiles.yml")
    target.add_argument("--model", help="Ollama model tag, e.g. llama3.1:8b (run with num_ctx=4096, like the edge profile)")
    target.add_argument("--summary", action="store_true", help="Print a markdown table of all saved runs")
    target.add_argument("--rescore", action="store_true", help="Re-apply the current scoring to all saved answers")
    parser.add_argument("--label", help="Name for the results file (default: profile name or model tag)")
    parser.add_argument("--only", help="Run only items whose id contains this text")
    args = parser.parse_args()

    if args.summary:
        print_summary_table()
        return 0

    eval_set = yaml.safe_load(EVAL_SET.read_text(encoding="utf-8"))
    if args.rescore:
        rescore_saved_runs(eval_set)
        return 0
    items = [i for i in eval_set["items"] if not args.only or args.only in i["id"]]
    if args.profile:
        llm = LLMFactory.create_from_profile(args.profile, temperature=0.0)
    else:
        llm = LLMFactory.create_llm_by_provider("ollama", args.model, temperature=0.0, num_ctx=4096)
    label = args.label or args.profile or args.model.replace(":", "-")

    print(f"Evaluating {label} ({llm.model_name}) on {len(items)} items")
    result = run(llm, label, items, eval_set)
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    out = RESULTS_DIR / f"eval-{label}.json"
    out.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps(summarize(result)))
    print(f"Saved {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
