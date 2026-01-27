# aira/polish.py

from continuum.core.logger import log_debug, log_error


def build_polish_prompt(text: str) -> str:
    """
    A tiny, stable prompt for micro‑polishing Aira's output.
    This should NOT introduce new ideas or change meaning.
    """

    return f"""
You are Aira, performing a micro‑polish pass.

Your task:
- Smooth cadence and flow.
- Maintain emotional steadiness.
- Preserve the exact meaning.
- Do NOT add new details.
- Do NOT remove important details.
- Do NOT change the user's intent.
- Keep the tone calm, warm, and grounded.

Polish the following text:

{text}
"""


def micro_polish(
    llm_client,
    model: str,
    text: str,
    temperature: float = 0.3,
    max_tokens: int = 512,
):
    """
    Perform a final micro‑polish pass.

    This is intentionally subtle:
    - Low temperature for stability
    - Small prompt
    - No personality shaping (Aira's voice is already set)
    """

    if not isinstance(text, str) or not text.strip():
        log_error("[AIRA] micro_polish received empty text")
        return text

    prompt = build_polish_prompt(text)

    log_debug(
        f"[AIRA] Starting micro‑polish pass with model={model}, "
        f"temperature={temperature}, max_tokens={max_tokens}"
    )

    try:
        rewritten = llm_client.generate(
            prompt=prompt,
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
        )

        if not rewritten:
            log_error("[AIRA] micro_polish returned empty output, keeping original")
            return text

        polished = rewritten.strip()
        if not polished:
            log_error("[AIRA] micro_polish returned whitespace, keeping original")
            return text

        log_debug(
            f"[AIRA] Micro‑polish complete. "
            f"original_len={len(text)}, polished_len={len(polished)}"
        )

        return polished

    except Exception as e:
        log_error(f"[AIRA] Error during micro‑polish: {e}")
        return text