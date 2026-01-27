# aira/rewrite_pass.py

from typing import Optional

from continuum.core.logger import log_debug, log_error
from continuum.aira.prompt import build_prompt


def _apply_temperature_curve(
    base_temperature: float,
    pass_index: int,
    decay_factor: float = 0.9,
    min_temperature: float = 0.3,
) -> float:
    """
    Apply a diminishing temperature curve across passes.

    pass_index: 0-based index of the rewrite pass.
    """
    adjusted = base_temperature * (decay_factor ** pass_index)
    clamped = max(min_temperature, adjusted)

    log_debug(
        f"[AIRA] Temperature curve: base={base_temperature}, "
        f"pass_index={pass_index}, adjusted={adjusted:.4f}, clamped={clamped:.4f}"
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
    Perform a single Aira rewrite pass.

    - Builds the prompt using Aira's voice template.
    - Applies a diminishing temperature curve based on pass_index.
    - Calls the LLM client.
    - Returns the rewritten text or None on failure.
    """

    if not isinstance(text_to_rewrite, str) or not text_to_rewrite.strip():
        log_error("[AIRA] rewrite_pass received empty or invalid text_to_rewrite")
        return None

    prompt = build_prompt(
        text_to_rewrite=text_to_rewrite,
        memory_summary=memory_summary,
        emotion_label=emotion_label,
    )

    temperature = _apply_temperature_curve(
        base_temperature=base_temperature,
        pass_index=pass_index,
    )

    log_debug(
        f"[AIRA] Starting rewrite pass {pass_index} "
        f"with model={model}, temperature={temperature:.4f}, max_tokens={max_tokens}"
    )

    try:
        rewritten = llm_client.generate(
            prompt=prompt,
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
        )

        if not rewritten:
            log_error(f"[AIRA] Empty response from LLM on pass {pass_index}")
            return None

        rewritten_str = rewritten.strip()
        if not rewritten_str:
            log_error(f"[AIRA] Whitespace-only response from LLM on pass {pass_index}")
            return None

        log_debug(
            f"[AIRA] Completed rewrite pass {pass_index}, "
            f"original_len={len(text_to_rewrite)}, rewritten_len={len(rewritten_str)}"
        )
        return rewritten_str

    except Exception as e:
        log_error(f"[AIRA] Error during rewrite pass {pass_index}: {e}")
        return None