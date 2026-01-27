# aira/diff.py

import difflib
from continuum.core.logger import log_debug


def compute_diff(before: str, after: str) -> str:
    """
    Produce a unified diff between two text versions.
    Used for debugging, logging, and UI visualization.
    """
    before_lines = before.splitlines(keepends=True)
    after_lines = after.splitlines(keepends=True)

    diff = difflib.unified_diff(
        before_lines,
        after_lines,
        fromfile="before",
        tofile="after",
        lineterm=""
    )

    diff_text = "".join(diff)
    log_debug("[AIRA] Diff computed")
    return diff_text


def diff_magnitude(before: str, after: str) -> float:
    """
    Compute a similarity ratio between 0 and 1.
    1.0 means identical.
    0.0 means completely different.
    """
    matcher = difflib.SequenceMatcher(None, before, after)
    ratio = matcher.ratio()

    log_debug(f"[AIRA] Diff magnitude ratio: {ratio:.4f}")
    return ratio


def should_stop_early(before: str, after: str, threshold: float = 0.92) -> bool:
    """
    Decide whether to stop rewriting early based on similarity.

    If the rewrite changed very little (ratio >= threshold),
    we stop to avoid over‑rewriting or flattening Aira's voice.
    """
    ratio = diff_magnitude(before, after)

    if ratio >= threshold:
        log_debug(
            f"[AIRA] Early stop triggered (ratio={ratio:.4f} >= threshold={threshold})"
        )
        return True

    return False