"""Unit tests for the best-effort PII masking used before traces leave the process (issue #16)."""

import pytest

from src.llm import observability
from src.privacy.pii import mask_pii, mask_pii_data


# A synthetic consult with planted PII. Every value below is made up; 111222333 passes the BSN eleven-test.
PLANTED_PII = {
    "Jan de Vries": "Naam: Jan de Vries",
    "12-03-1958": "geboren 12-03-1958",
    "111222333": "BSN 111222333",
    "06-12345678": "tel 06-12345678",
    "jan.devries@example.nl": "mail jan.devries@example.nl",
    "Kerkstraat 12a": "woont Kerkstraat 12a",
    "1234 AB": "1234 AB Utrecht",
}
CONVERSATION = [
    {"role": "doctor", "text": "Goedemorgen. " + ", ".join(PLANTED_PII.values()) + "?"},
    {"role": "patient", "text": "Ja, dat klopt. Sinds 3 dagen pijn op de borst, mevr. Bakker weet ervan."},
    {"role": "doctor", "text": "Patient Maria Jansen, DOB 1980-05-17, SSN 123-45-6789, +31 20 123 4567."},
]


def test_planted_pii_is_removed_from_a_conversation():
    """No planted value survives masking anywhere in the conversation; the roles and clinical content do."""
    masked = mask_pii_data(CONVERSATION)
    flat = str(masked)

    for value in [*PLANTED_PII, "Bakker", "Maria Jansen", "1980-05-17", "123-45-6789", "123 4567"]:
        assert value not in flat
    assert [turn["role"] for turn in masked] == ["doctor", "patient", "doctor"]
    assert "pijn op de borst" in flat


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("Naam: Jan de Vries.", "Naam: [NAME]."),
        ("Mevr. Bakker belde", "Mevr. [NAME] belde"),
        ("geb. 12-03-1958", "geb. [DATE]"),
        ("born 3 maart 1975", "born [DATE]"),
        ("BSN 111.222.333", "BSN [BSN]"),
        ("SSN 123-45-6789", "SSN [SSN]"),
        ("bel 0612345678", "bel [PHONE]"),
        ("bel +31 6 12345678", "bel [PHONE]"),
        ("IBAN NL91 ABNA 0417 1643 00", "IBAN [IBAN]"),
        ("at 221 Baker Street.", "at [ADDRESS]."),
        ("Kerkstraat 12a, 1234 AB Utrecht", "[ADDRESS], [POSTCODE] Utrecht"),
        ("a@b.example.com", "[EMAIL]"),
    ],
)
def test_each_pii_shape_is_masked(text, expected):
    """Each supported identifier shape becomes its `[LABEL]` placeholder, keeping the cue words around it."""
    assert mask_pii(text) == expected


@pytest.mark.parametrize(
    "text",
    [
        "The patient reports chest pain since 2 days.",
        "BP 120/80, metoprolol 50 mg twice daily.",
        "Order 123456789 is not a valid BSN.",
    ],
)
def test_clinical_text_without_pii_is_unchanged(text):
    """Ordinary clinical text, and nine digits that fail the BSN eleven-test, are left alone."""
    assert mask_pii(text) == text


def test_mask_pii_data_keeps_structure_and_non_strings():
    """Dict keys, tuples and non-string values pass through; only strings are masked."""
    data = {"input": ("Naam: Jan", 3), "tokens": 42, "ok": None}

    assert mask_pii_data(data) == {"input": ("Naam: [NAME]", 3), "tokens": 42, "ok": None}


def test_langfuse_mask_callback_masks_data_regardless_of_provider():
    """The callback Langfuse invokes masks its `data` and ignores extra keyword arguments."""
    assert observability.langfuse_mask(data={"prompt": "Mevr. Bakker"}, provider="ollama") == {"prompt": "Mevr. [NAME]"}
