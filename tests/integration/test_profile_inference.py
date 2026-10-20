"""Real inference through each local model profile (issue #2).

Runs a short synthetic clinical prompt through the Ollama-backed profiles in
config/llm_profiles.yml. Each profile is skipped when Ollama is not reachable or its
model has not been pulled, so this is safe to run anywhere; CI runs unit tests only.

    uv run pytest -m ollama tests/integration/test_profile_inference.py
"""

import pytest

from src.llm.llm_factory import LLMFactory
from src.llm.ollama_llm import check_ollama_availability, is_model_available
from src.llm.profile_config import get_profile


PROMPT = (
    "Answer with the letter only. Which drug class does metoprolol belong to? "
    "A) ACE inhibitor B) Beta blocker C) Calcium channel blocker D) Diuretic"
)


@pytest.mark.ollama
@pytest.mark.integration
@pytest.mark.parametrize("profile", ["edge", "cpu", "gpu"])
def test_profile_answers_clinical_question(profile):
    model = get_profile(profile)["model"]
    if not check_ollama_availability():
        pytest.skip("Ollama is not running")
    if not is_model_available(model):
        pytest.skip(f"{model} not pulled: ollama pull {model}")

    llm = LLMFactory.create_from_profile(profile, temperature=0.0)
    answer = llm.invoke(PROMPT)

    assert "<unused9" not in answer and "<think>" not in answer
    assert answer.strip().upper().startswith("B") or "beta blocker" in answer.lower()
    assert llm.last_usage and llm.last_usage["output_tokens"] > 0
