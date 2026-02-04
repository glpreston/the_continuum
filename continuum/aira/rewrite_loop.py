# continuum/aira/rewrite_loop.py

from continuum.core.logger import log_debug, log_error

from continuum.aira.rewrite_pass import rewrite_pass
from continuum.aira.diff import compute_diff, should_stop_early
from continuum.aira.safety import (
    clamp_length,
    is_excessively_long,
)


def rewrite_loop(
    llm_client,
    model: str,
    base_text,
    memory_summary: str,
    emotion_label: str,
    base_temperature: float,
    max_tokens: int,
    max_rewrite_depth: int = 3,
    early_stop_threshold: float = 0.92,
):
    # ⭐ Normalize base_text BEFORE ANYTHING ELSE
    if not isinstance(base_text, str):
        base_text = str(base_text) if base_text is not None else ""

    # ⭐ Now safe to check emptiness
    if not base_text.strip():
        log_error("[AIRA] rewrite_loop received empty base_text")
        return base_text

    # ⭐ Now safe to call len()
    log_debug(
        f"[AIRA] Starting rewrite loop: depth={max_rewrite_depth}, "
        f"model={model}, base_len={len(base_text)}"
    )
    
    current_text = base_text

    for pass_index in range(max_rewrite_depth):
        log_debug(f"[AIRA] Rewrite pass {pass_index + 1}/{max_rewrite_depth}")

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

        if not isinstance(rewritten, str) or not rewritten.strip():
            log_error("[AIRA] rewrite_pass returned empty or invalid text, stopping early")
            break

        # Clamp runaway length
        if is_excessively_long(rewritten, max_tokens):
            log_debug("[AIRA] Rewritten text excessively long, clamping")
            rewritten = clamp_length(rewritten, max_tokens)

        # Compute diff and decide whether to stop early
        diff_score = compute_diff(current_text, rewritten)
        log_debug(f"[AIRA] Diff score after pass {pass_index + 1}: {diff_score:.4f}")

        if should_stop_early(diff_score, early_stop_threshold):
            log_debug("[AIRA] Early stop triggered by diff threshold")
            current_text = rewritten
            break

        current_text = rewritten

    return current_text