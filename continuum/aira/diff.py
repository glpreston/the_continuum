# continuum/aira/diff.py

import difflib
from continuum.core.logger import log_debug, log_error

# -------------------------------------------------------------------
# Phase‑5 constants (Phase‑6: move to DB/config)
# -------------------------------------------------------------------

DEFAULT_EARLY_STOP_THRESHOLD = 0.92


def compute_diff(before: str, after: str) -> str:
    if not isinstance(before, str) or not isinstance(after, str):
        log_error("[AIRA][diff] compute_diff received non-string input")
        return ""

    try:
        before_lines = before.splitlines(keepends=True)
        after_lines = after.splitlines(keepends=True)
    except Exception as e:
        log_error(f"[AIRA][diff] Error splitting lines: {e}")
        return ""

    diff = difflib.unified_diff(
        before_lines,
        after_lines,
        fromfile="before",
        tofile="after",
        lineterm=""
    )

    diff_text = "".join(diff)
    log_debug("[AIRA][diff] Unified diff computed")
    return diff_text


def diff_magnitude(before: str, after: str) -> float:
    """
    Compute a similarity ratio between 0 and 1.
    1.0 means identical.
    0.0 means completely different.
    """

    if not isinstance(before, str) or not isinstance(after, str):
        log_error("[AIRA][diff] diff_magnitude received non-string input")
        return 0.0

    matcher = difflib.SequenceMatcher(None, before, after)
    ratio = matcher.ratio()

    # Safe formatting
    try:
        ratio_display = f"{ratio:.4f}"
    except Exception:
        ratio_display = str(ratio)

    log_debug(f"[AIRA][diff] Diff magnitude ratio: {ratio_display}")
    return ratio


def should_stop_early(before: str, after: str, threshold: float = DEFAULT_EARLY_STOP_THRESHOLD) -> bool:
    """
    Decide whether to stop rewriting early based on similarity.

    If the rewrite changed very little (ratio >= threshold),
    we stop to avoid over‑rewriting or flattening Aira's voice.
    """

    ratio = diff_magnitude(before, after)

    if ratio >= threshold:
        log_debug(
            f"[AIRA][diff] Early stop triggered "
            f"(ratio={ratio:.4f} >= threshold={threshold})"
        )
        return True

    return False