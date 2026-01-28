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
    endpoint: str,
    base_text: str,
    memory_summary: str,
    emotion_label: str,
    base_temperature: float,
    max_tokens: int,
    max_rewrite_depth: int = 3,
    early_stop_threshold: float = 0.92,
):
    """
    Perform Aira's full multi-pass rewrite loop (Router-aware).

    Responsibilities:
    - Run multiple rewrite passes
    - Apply diminishing temperature curve
    - Stop early if diff is small
    - Clamp runaway length
    - Log diffs for debugging/UI
    """

    if not isinstance(base_text, str) or not base_text.strip():
        log_error("[AIRA] rewrite_loop received empty base_text")
        return base_text

    log_debug(
        f"[AIRA] Starting rewrite loop: depth={max_rewrite_depth}, "
        f"model={model}, endpoint={endpoint}, base_len={len(base_text)}"
    )

    current_text = base_text

    for pass_index in range(max_rewrite_depth):
        log_debug(f"[AIRA] ---- Rewrite pass {pass_index} ----")

        rewritten = rewrite_pass(
            llm_client=llm_client,
            model=model,
            endpoint=endpoint,
            text_to_rewrite=current_text,
            memory_summary=memory_summary,
            emotion_label=emotion_label,
            base_temperature=base_temperature,
            max_tokens=max_tokens,
            pass_index=pass_index,
        )

        if not rewritten:
            log_error(f"[AIRA] Rewrite pass {pass_index} returned None, stopping early")
            break

        # Safety: clamp runaway length
        if is_excessively_long(current_text, rewritten):
            log_error("[AIRA] Rewrite grew excessively long, clamping")
            rewritten = clamp_length(rewritten, max_length=len(current_text) * 2)

        # Compute diff for logging and early stopping
        diff_text = compute_diff(current_text, rewritten)
        log_debug(f"[AIRA] Diff for pass {pass_index}:\n{diff_text}")

        # Early stop if rewrite changed very little
        if should_stop_early(current_text, rewritten, threshold=early_stop_threshold):
            log_debug(f"[AIRA] Early stop triggered at pass {pass_index}")
            current_text = rewritten
            break

        current_text = rewritten

    log_debug(
        f"[AIRA] Rewrite loop complete. Final length={len(current_text)}, "
        f"original_length={len(base_text)}"
    )

    return current_text