# continuum/orchestrator/fusion_filters.py

import re
from typing import List


# ---------------------------------------------------------
# 1. Refusal / Safety / Meta‑Commentary Patterns
# ---------------------------------------------------------

REFUSAL_PATTERNS = [
    r"^i\s+can(\'t|not)\b",
    r"^i\s+am\s+unable\b",
    r"^i\s+am\s+not\s+able\b",
    r"^i\s+am\s+not\s+permitted\b",
    r"^i\s+must\s+ensure\b",
    r"^i\s+cannot\b",
    r"^i\s+can\s+not\b",
]

META_PATTERNS = [
    r"^the\s+user(\'s)?\s+request\b",
    r"^the\s+user(\'s)?\s+message\b",        # NEW — catches “The user’s message…”
    r"^the\s+user\s+is\s+asking\b",
    r"^the\s+user\s+is\s+expressing\b",
    r"^this\s+prompt\s+can\s+be\s+broken\b",
    r"^it(\'s| is)\s+essential\b",
    r"^to\s+provide\b",
    r"^the\s+statement\s+is\b",
    r"^the\s+question\s+is\b",
]

SAFETY_PATTERNS = [
    r"consult\s+a\s+professional",
    r"medical\s+advice",
    r"legal\s+advice",
    r"ensure\s+safety",
]


# ---------------------------------------------------------
# 2. Narrative Fragment Detection
# ---------------------------------------------------------

NARRATIVE_STARTERS = [
    r"^as\s+she\b",
    r"^as\s+he\b",
    r"^as\s+the\b",
    r"^as\s+they\b",
]


# ---------------------------------------------------------
# 3. Utility: Sentence Fragment Detection
# ---------------------------------------------------------

def is_fragment(sentence: str) -> bool:
    """Detects incomplete or dangling sentences."""
    s = sentence.strip().rstrip(",;:")

    # Too short to be meaningful
    if len(s.split()) < 4:
        return True

    # Must contain at least one verb-like pattern
    if not re.search(
        r"\b(is|are|was|were|be|being|been|has|have|had|do|does|did|can|could|will|would|should|may|might)\b",
        s,
    ):
        return True

    # Dangling endings
    if s.endswith(("and", "or", "but", "so", "because", "as")):
        return True

    # NEW: detect truncated last words (e.g., "powde")
    last_word = s.split()[-1]
    if len(last_word) <= 4 and not re.search(r"[aeiou]", last_word):
        return True

    return False


# ---------------------------------------------------------
# 4. Main Filter Function
# ---------------------------------------------------------

def filter_sentence(sentence: str, user_message: str) -> bool:
    """Returns True if the sentence should be kept; False if removed."""

    s = sentence.strip().lower()

    # Remove user‑echo
    if user_message and user_message.lower() in s:
        return False

    # Refusal frames
    if any(re.match(p, s) for p in REFUSAL_PATTERNS):
        return False

    # Meta‑commentary
    if any(re.match(p, s) for p in META_PATTERNS):
        return False

    # Safety misfires
    if any(re.search(p, s) for p in SAFETY_PATTERNS):
        return False

    # Narrative fragments (only remove if incomplete)
    if any(re.match(p, s) for p in NARRATIVE_STARTERS) and is_fragment(s):
        return False

    # General fragments
    if is_fragment(s):
        return False

    return True


def filter_sentences(sentences: List[str], user_message: str) -> List[str]:
    """Applies semantic filtering to a list of sentences."""
    return [s for s in sentences if filter_sentence(s, user_message)]