# continuum/rubric/structure.py
"""
Structural Scoring — Jury Rubric 3.0
------------------------------------

Evaluates:
- Coherence (semantic + formatting cues)
- Structural clarity (organization, flow)
- Prompt alignment (does the structure match the LLM prompt?)

All scores normalized to [0, 1].
"""

from typing import Optional
import difflib


# =========================================================
# Basic Utilities
# =========================================================

def _sentence_count(text: str) -> int:
    return len([s for s in text.split(".") if s.strip()])


def _paragraph_count(text: str) -> int:
    return len([p for p in text.split("\n") if p.strip()])


def _has_list_structure(text: str) -> bool:
    return any(
        text.strip().startswith(prefix)
        or f"\n{prefix}" in text
        for prefix in ("- ", "* ", "1.", "2.", "•")
    )


# =========================================================
# Structural Coherence
# =========================================================

def _score_coherence(text: str) -> float:
    """
    Measures basic structural coherence:
    - multiple sentences
    - paragraph breaks
    - list structure
    - connective flow
    """

    if not text:
        return 0.0

    score = 0.0

    # Sentence structure
    if _sentence_count(text) >= 2:
        score += 0.3

    # Paragraph structure
    if _paragraph_count(text) >= 2:
        score += 0.3

    # List structure
    if _has_list_structure(text):
        score += 0.2

    # Connective flow (simple heuristic)
    connectors = ["therefore", "however", "because", "first", "next", "finally"]
    if any(c in text.lower() for c in connectors):
        score += 0.2

    return min(score, 1.0)


# =========================================================
# Prompt Alignment
# =========================================================

def _score_prompt_alignment(proposal: str, prompt: str) -> float:
    """
    Measures how structurally aligned the proposal is with the LLM prompt.
    Uses sequence similarity as a soft structural proxy.
    """

    if not proposal or not prompt:
        return 0.5  # neutral

    sim = difflib.SequenceMatcher(None, proposal.lower(), prompt.lower()).ratio()

    # Structural alignment is softer than semantic alignment
    return max(0.0, min(sim * 0.8 + 0.2, 1.0))


# =========================================================
# Master Structural Score
# =========================================================

def score_structure(
    proposal: str,
    llm_prompt: Optional[str] = "",
) -> float:
    """
    Combines:
    - structural coherence
    - prompt alignment

    Returns a single structural clarity score.
    """

    if not proposal:
        return 0.0

    coherence = _score_coherence(proposal)
    alignment = _score_prompt_alignment(proposal, llm_prompt)

    # Weighted blend
    total = 0.6 * coherence + 0.4 * alignment
    return round(min(max(total, 0.0), 1.0), 4)