"""Best-effort, regex-based PII masking for text that leaves the process (issue #16).

Used by the Langfuse client (`src.llm.observability`) and meant for any future cloud-LLM path,
so the masking rules live in one place. It catches identifiers with a recognisable shape
(email, phone, BSN/SSN, IBAN, dates, Dutch postcodes, street addresses) and names that follow a
cue such as "Naam:", "patient" or "Mevr.". Names without such a cue are NOT masked: this is not a
de-identification guarantee. Server-side masking and retention policies are Langfuse Enterprise
features and would be needed for real PHI.
"""

import re
from typing import Any


_MONTHS = (
    r"jan(?:uari|uary)?|feb(?:ruari|ruary)?|maa(?:rt)?|mar(?:ch)?|apr(?:il)?|mei|may|jun[ie]?|jul[iy]?"
    r"|aug(?:ustus|ust)?|sep(?:tember)?|okt(?:ober)?|oct(?:ober)?|nov(?:ember)?|dec(?:ember)?"
)
_NAME = r"[A-Z][a-zà-ÿ'\-]+(?:\s+(?:van|de|der|den|het|ter|ten|v\.d\.|[A-Z][a-zà-ÿ'\-]+))*"

# Order matters: longer or more specific shapes go first so a later rule cannot split them.
_PATTERNS: list[tuple[str, re.Pattern[str]]] = [
    ("EMAIL", re.compile(r"\b[\w.+-]+@[\w-]+(?:\.[\w-]+)+\b")),
    ("IBAN", re.compile(r"\b[A-Z]{2}\d{2}\s?[A-Z]{4}(?:\s?\d{2,4}){2,5}\b")),
    (
        "DATE",
        re.compile(
            r"\b(?:\d{4}-\d{1,2}-\d{1,2}|\d{1,2}[-/.]\d{1,2}[-/.]\d{2,4}|\d{1,2}\s+(?:" + _MONTHS + r")\.?\s+\d{4})\b",
            re.IGNORECASE,
        ),
    ),
    ("SSN", re.compile(r"\b\d{3}-\d{2}-\d{4}\b")),
    ("BSN", re.compile(r"\b\d{4}\.?\d{2}\.?\d{3}\b|\b\d{3}\.\d{3}\.\d{3}\b")),
    ("PHONE", re.compile(r"(?<![\w+])(?:\+\d{1,3}[\s-]?(?:\(0\))?|0)\d(?:[\s-]?\d){7,9}\b")),
    ("POSTCODE", re.compile(r"\b\d{4}\s?[A-Z]{2}\b")),
    (
        "ADDRESS",
        re.compile(
            r"\b[A-Z][a-zà-ÿ]*(?:straat|laan|weg|plein|gracht|kade|singel|dijk|steeg|hof|park)\s+\d+\s?[a-zA-Z]?\b"
            r"|\b\d+\s+[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\s+(?:Street|St|Avenue|Ave|Road|Rd|Lane|Ln|Drive|Dr|Boulevard|Blvd)\b"
        ),
    ),
    # The cue (group 1) is kept and is case-insensitive; the name itself must be capitalised.
    ("NAME", re.compile(r"(?i:(\b(?:naam|name):\s*|\b(?:patiënt|patient)\s+|\b(?:dhr|mevr|mw|mr|mrs|ms|dr|drs)\.?\s+))" + _NAME)),
]


def _is_bsn(digits: str) -> bool:
    """True when nine digits pass the Dutch BSN eleven-test (elfproef)."""
    if len(digits) != 9:
        return False
    total = sum(int(d) * w for d, w in zip(digits[:8], range(9, 1, -1), strict=True)) - int(digits[8])
    return total % 11 == 0


def _replace(label: str, match: re.Match[str]) -> str:
    if label == "BSN" and not _is_bsn(re.sub(r"\D", "", match.group())):
        return match.group()
    if label == "NAME":
        return f"{match.group(1)}[NAME]"
    return f"[{label}]"


def mask_pii(text: str) -> str:
    """Return `text` with recognisable PII replaced by `[LABEL]` placeholders."""
    for label, pattern in _PATTERNS:
        text = pattern.sub(lambda m, label=label: _replace(label, m), text)
    return text


def mask_pii_data(data: Any) -> Any:
    """Mask every string inside `data`, recursing into dicts, lists and tuples. Keys are kept."""
    if isinstance(data, str):
        return mask_pii(data)
    if isinstance(data, dict):
        return {key: mask_pii_data(value) for key, value in data.items()}
    if isinstance(data, list | tuple):
        return type(data)(mask_pii_data(item) for item in data)
    return data
