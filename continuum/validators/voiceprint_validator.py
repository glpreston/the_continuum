# continuum/validators/voiceprint_validator.py

"""
Continuum Voiceprint Validator
Checks whether MetaPersona output aligns with the Unified Continuum Voiceprint Specification.
"""

from dataclasses import dataclass
from typing import Dict, List
import re
import statistics


# ---------------------------------------------------------
# Validation Result Structure
# ---------------------------------------------------------

@dataclass
class ValidationResult:
    tone: str
    pacing: str
    density: str
    signature_phrasing: str
    forbidden_elements: str
    metaphor_density: str
    grounding: str
    softening_crispness_balance: str
    overall: str
    details: Dict[str, any]


# ---------------------------------------------------------
# Helper Functions
# ---------------------------------------------------------

def split_sentences(text: str) -> List[str]:
    return [s.strip() for s in re.split(r"[.!?]+", text) if s.strip()]


def count_words(sentence: str) -> int:
    return len(sentence.split())


def contains_any(text: str, words: List[str]) -> bool:
    return any(w.lower() in text.lower() for w in words)


def count_occurrences(text: str, words: List[str]) -> int:
    return sum(text.lower().count(w.lower()) for w in words)


# ---------------------------------------------------------
# Main Validator
# ---------------------------------------------------------

def validate_output(text: str, emotion_state: Dict, voiceprint) -> ValidationResult:
    """
    Validates MetaPersona output against the Continuum Unified Voiceprint.
    """

    sentences = split_sentences(text)
    word_counts = [count_words(s) for s in sentences] or [0]
    avg_sentence_length = statistics.mean(word_counts)

    # -------------------------------
    # 1. Tone Check
    # -------------------------------
    tone_pass = True
    harsh_markers = ["obviously", "clearly you", "you should", "that's wrong"]
    if contains_any(text, harsh_markers):
        tone_pass = False

    # -------------------------------
    # 2. Pacing Check
    # -------------------------------
    pacing_status = "pass"
    if avg_sentence_length > 24:
        pacing_status = "warning: too long"
    elif avg_sentence_length < 8:
        pacing_status = "warning: too short"

    # -------------------------------
    # 3. Density Check
    # -------------------------------
    density_status = "pass"
    if len(sentences) > 0:
        if avg_sentence_length > 20:
            density_status = "warning: high density"
        if avg_sentence_length < 10:
            density_status = "warning: low density"

    # -------------------------------
    # 4. Signature Phrasing
    # -------------------------------
    sig_phrases = voiceprint.signature_phrasing
    sig_count = count_occurrences(text, sig_phrases)

    if sig_count == 0:
        sig_status = "warning: no signature phrasing"
    elif sig_count > 3:
        sig_status = "warning: overuse"
    else:
        sig_status = "pass"

    # -------------------------------
    # 5. Forbidden Elements
    # -------------------------------
    forbidden = voiceprint.forbidden_elements
    forbidden_hits = [w for w in forbidden if w.lower() in text.lower()]

    forbidden_status = "pass" if not forbidden_hits else f"fail: {forbidden_hits}"

    # -------------------------------
    # 6. Metaphor Density
    # -------------------------------
    metaphor_markers = ["like", "as if", "imagine", "picture", "as though"]
    metaphor_count = count_occurrences(text, metaphor_markers)

    metaphor_status = "pass"
    if metaphor_count > 5:
        metaphor_status = "warning: too metaphorical"

    # -------------------------------
    # 7. Grounding Language
    # -------------------------------
    grounding_phrases = ["we can stay steady", "keep things grounded", "we can move through this"]
    grounding_count = count_occurrences(text, grounding_phrases)

    grounding_status = "pass"
    if emotion_state.get("dominant") in ["sadness", "tension", "fatigue"] and grounding_count == 0:
        grounding_status = "warning: grounding missing"

    # -------------------------------
    # 8. Softening / Crispness Balance
    # -------------------------------
    softeners = ["gently", "a bit", "we can take our time"]
    crispness = ["clearly", "directly", "in essence"]

    soft_count = count_occurrences(text, softeners)
    crisp_count = count_occurrences(text, crispness)

    balance_status = "pass"
    if soft_count > 5:
        balance_status = "warning: too soft"
    if crisp_count > 5:
        balance_status = "warning: too crisp"

    # -------------------------------
    # Overall
    # -------------------------------
    failures = [
        tone_pass,
        forbidden_status == "pass",
    ]

    overall = "pass" if all(failures) else "warning"

    # -------------------------------
    # Build Result
    # -------------------------------
    return ValidationResult(
        tone="pass" if tone_pass else "warning",
        pacing=pacing_status,
        density=density_status,
        signature_phrasing=sig_status,
        forbidden_elements=forbidden_status,
        metaphor_density=metaphor_status,
        grounding=grounding_status,
        softening_crispness_balance=balance_status,
        overall=overall,
        details={
            "avg_sentence_length": avg_sentence_length,
            "signature_phrase_count": sig_count,
            "metaphor_count": metaphor_count,
            "grounding_count": grounding_count,
            "softening_count": soft_count,
            "crispness_count": crisp_count,
        }
    )