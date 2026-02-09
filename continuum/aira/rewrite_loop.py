# continuum/aira/rewrite_loop.py

from continuum.core.logger import log_debug, log_error
from continuum.aira.diff import diff_magnitude
from continuum.aira.rewrite_pass import rewrite_pass
from continuum.aira.diff import compute_diff, should_stop_early
from continuum.aira.safety import (
    clamp_length,
    is_excessively_long,
)

# -------------------------------------------------------------------
# Phase‑5 constants (Phase‑6: move to DB/config)
# -------------------------------------------------------------------

DEFAULT_EARLY_STOP_THRESHOLD = 0.92
DEFAULT_MAX_REWRITE_DEPTH = 3


def rewrite_loop(
    llm_client,
    model: str,
    base_text,
    memory_summary: str,
    emotion_label: str,
    base_temperature: float,
    max_tokens: int,
    max_rewrite_depth: int = DEFAULT_MAX_REWRITE_DEPTH,
    early_stop_threshold: float = DEFAULT_EARLY_STOP_THRESHOLD,
):
    """
    Multi‑pass rewrite loop for Aira.
    Applies:
    - rewrite_pass()
    - length guardrails
    - diff‑based early stopping
    """

    # Normalize base_text
    if not isinstance(base_text, str):
        base_text = str(base_text) if base_text is not None else ""

    if not base_text.strip():
        log_error("[AIRA][rewrite_loop] Received empty base_text")
        return base_text

    log_debug(
        f"[AIRA][rewrite_loop] Starting rewrite loop: "
        f"depth={max_rewrite_depth}, model={model}, base_len={len(base_text)}"
    )

    current_text = base_text

    for pass_index in range(max_rewrite_depth):
        log_debug(
            f"[AIRA][rewrite_loop] Rewrite pass {pass_index + 1}/{max_rewrite_depth}"
        )

        rewritten = rewrite_pass(
            llm_client=llm_client,
            model=model,
            text_to_rewrite=current_text,
            memory_summary=memory_summary,
            emotion_label=emotion_label,
            base_temperature=base_temperature,
            max_tokens=max_tokens,
            pass_index=pass_index,
        )

        # Validate rewritten output
        if not isinstance(rewritten, str) or not rewritten.strip():
            log_error(
                "[AIRA][rewrite_loop] rewrite_pass returned empty or invalid text; stopping early"
            )
            break

        # Guardrail: prevent runaway length
        if is_excessively_long(current_text, rewritten):
            log_debug("[AIRA][rewrite_loop] Rewritten text excessively long; clamping")
            rewritten = clamp_length(rewritten, max_tokens)     

        # Compute similarity ratio (0.0–1.0)
        ratio = diff_magnitude(current_text, rewritten)
        ratio_display = f"{ratio:.4f}"

        log_debug(
            f"[AIRA][rewrite_loop] Diff ratio after pass {pass_index + 1}: {ratio_display}"
        )

        # Early stop if rewrite changed very little
        if ratio >= early_stop_threshold:
            log_debug("[AIRA][rewrite_loop] Early stop triggered by diff threshold")
            current_text = rewritten
            break

        current_text = rewritten
    log_debug(
        f"[AIRA][rewrite_loop] Rewrite loop complete: final_len={len(current_text)}"
    )

    return current_text