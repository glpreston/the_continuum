# continuum/aira/safety.py

from continuum.core.logger import log_debug, log_error

# -------------------------------------------------------------------
# Phase‑5 constants (Phase‑6: move to DB/config)
# -------------------------------------------------------------------

MAX_LENGTH_GROWTH_FACTOR = 2.0
MIN_TEMPERATURE = 0.2
MAX_TEMPERATURE = 1.2
MIN_REWRITE_RATIO = 0.2  # rewritten must be at least 20% of original


# -----------------------------
# Length Safety
# -----------------------------

def is_excessively_long(
    original: str,
    rewritten: str,
    max_growth_factor: float = MAX_LENGTH_GROWTH_FACTOR,
) -> bool:
    """
    Return True if the rewritten text is excessively longer than the original.
    max_growth_factor:
        2.0 means "no more than 2x the original length".
    """

    if not isinstance(original, str) or not isinstance(rewritten, str):
        log_error("[AIRA][safety] is_excessively_long received non-string input")
        return False

    if not original:
        return False

    orig_len = len(original)
    new_len = len(rewritten)

    if new_len > orig_len * max_growth_factor:
        log_error(
            f"[AIRA][safety] Excessive length growth detected: "
            f"original_len={orig_len}, rewritten_len={new_len}, "
            f"max_growth_factor={max_growth_factor}"
        )
        return True

    log_debug(
        f"[AIRA][safety] Length check OK: "
        f"original_len={orig_len}, rewritten_len={new_len}, "
        f"max_growth_factor={max_growth_factor}"
    )
    return False


def clamp_length(text: str, max_length: int) -> str:
    """
    Clamp text to a maximum character length, attempting to cut at a boundary.
    """

    if not isinstance(text, str):
        log_error("[AIRA][safety] clamp_length received non-string input")
        return ""

    if len(text) <= max_length:
        return text

    truncated = text[:max_length]

    # Try to avoid cutting mid‑sentence if possible
    last_period = truncated.rfind(".")
    if last_period > max_length * 0.6:
        truncated = truncated[: last_period + 1]

    log_error(
        f"[AIRA][safety] Text clamped: max_length={max_length}, "
        f"final_len={len(truncated)}"
    )
    return truncated


# -----------------------------
# Temperature Safety
# -----------------------------

def clamp_temperature(
    temperature: float,
    min_temperature: float = MIN_TEMPERATURE,
    max_temperature: float = MAX_TEMPERATURE,
) -> float:
    """
    Clamp temperature into a safe range.
    """

    clamped = max(min_temperature, min(max_temperature, temperature))

    if clamped != temperature:
        log_debug(
            f"[AIRA][safety] Temperature clamped: "
            f"original={temperature}, clamped={clamped}, "
            f"range=({min_temperature}, {max_temperature})"
        )
    else:
        log_debug(
            f"[AIRA][safety] Temperature within safe range: {temperature}"
        )

    return clamped


# -----------------------------
# Rewrite Validation
# -----------------------------

def validate_rewrite(original: str, rewritten: str) -> bool:
    """
    Basic sanity checks on a rewritten output.
    Returns True if the rewritten text looks usable.
    """

    if not isinstance(rewritten, str):
        log_error("[AIRA][safety] validate_rewrite: rewritten is not a string")
        return False

    stripped = rewritten.strip()
    if not stripped:
        log_error("[AIRA][safety] validate_rewrite: rewritten is empty/whitespace")
        return False

    if not isinstance(original, str):
        log_error("[AIRA][safety] validate_rewrite: original is not a string")
        return False

    # If it's absurdly short compared to original, likely a failure
    if original and len(stripped) < len(original) * MIN_REWRITE_RATIO:
        log_error(
            f"[AIRA][safety] validate_rewrite: rewritten too short "
            f"(original_len={len(original)}, rewritten_len={len(stripped)})"
        )
        return False

    log_debug(
        f"[AIRA][safety] validate_rewrite: accepted "
        f"(original_len={len(original)}, rewritten_len={len(stripped)})"
    )
    return True