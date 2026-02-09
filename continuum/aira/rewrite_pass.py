# continuum/aira/rewrite_pass.py

from typing import Optional

from continuum.core.logger import log_debug, log_error
from continuum.aira.prompt import build_prompt

# -------------------------------------------------------------------
# Phase‑5 constants (Phase‑6: move to DB/config)
# -------------------------------------------------------------------

TEMPERATURE_DECAY_FACTOR = 0.9
MIN_TEMPERATURE = 0.3


def _apply_temperature_curve(
    base_temperature: float,
    pass_index: int,
    decay_factor: float = TEMPERATURE_DECAY_FACTOR,
    min_temperature: float = MIN_TEMPERATURE,
) -> float:
    """
    Apply a diminishing temperature curve across passes.
    pass_index: 0-based index of the rewrite pass.
    """
    adjusted = base_temperature * (decay_factor ** pass_index)
    clamped = max(min_temperature, adjusted)

    log_debug(
        f"[AIRA][rewrite_pass] Temperature curve: "
        f"base={base_temperature}, pass_index={pass_index}, "
        f"adjusted={adjusted:.4f}, clamped={clamped:.4f}"
    )
    return clamped


def rewrite_pass(
    llm_client,
    model: str,
    text_to_rewrite: str,
    memory_summary: str,
    emotion_label: str,
    base_temperature: float,
    max_tokens: int,
    pass_index: int,
) -> Optional[str]:
    """
    Perform a single Aira rewrite pass (model-aware, endpoint-agnostic).

    - Builds the prompt using Aira's voice template.
    - Applies a diminishing temperature curve based on pass_index.
    - Calls the LLM client using its current/default endpoint.
    - Returns the rewritten text or None on failure.
    """

    # Validate input text
    if not isinstance(text_to_rewrite, str) or not text_to_rewrite.strip():
        log_error("[AIRA][rewrite_pass] Received empty or invalid text_to_rewrite")
        return None

    # Build prompt
    try:
        prompt = build_prompt(
            text_to_rewrite=text_to_rewrite,
            memory_summary=memory_summary,
            emotion_label=emotion_label,
        )
    except Exception as e:
        log_error(f"[AIRA][rewrite_pass] Error building prompt: {e}")
        return None

    # Apply temperature curve
    temperature = _apply_temperature_curve(
        base_temperature=base_temperature,
        pass_index=pass_index,
    )

    log_debug(
        f"[AIRA][rewrite_pass] Calling LLM: model={model}, "
        f"temperature={temperature:.3f}, max_tokens={max_tokens}"
    )

    # Call LLM
    try:
        response = llm_client.generate(
            prompt=prompt,
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
        )
    except Exception as e:
        log_error(f"[AIRA][rewrite_pass] LLM error: {e}")
        return None

    # Normalize response
    if isinstance(response, dict):
        text = (
            response.get("text")
            or response.get("response")
            or response.get("content")
        )
    else:
        text = str(response) if response is not None else None

    # Validate output
    if not text or not str(text).strip():
        log_error("[AIRA][rewrite_pass] Received empty response from LLM")
        return None

    log_debug(
        f"[AIRA][rewrite_pass] Rewrite pass complete: "
        f"input_len={len(text_to_rewrite)}, output_len={len(text)}"
    )

    return text