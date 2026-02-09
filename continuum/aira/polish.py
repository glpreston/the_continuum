# continuum/aira/polish.py

from continuum.core.logger import log_debug, log_error

# -------------------------------------------------------------------
# Phase‑5 constants (Phase‑6: move to DB/config)
# -------------------------------------------------------------------

MICRO_POLISH_TEMPERATURE = 0.3
MICRO_POLISH_MAX_TOKENS = 512


def build_polish_prompt(text: str) -> str:
    """
    A tiny, stable prompt for micro‑polishing Aira's output.
    This should NOT introduce new ideas or change meaning.
    """

    return f"""\
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
    temperature: float = MICRO_POLISH_TEMPERATURE,
    max_tokens: int = MICRO_POLISH_MAX_TOKENS,
):
    """
    Perform a final micro‑polish pass.

    This is intentionally subtle:
    - Low temperature for stability
    - Small prompt
    - No personality shaping (Aira's voice is already set)
    """

    if not isinstance(text, str) or not text.strip():
        log_error("[AIRA][polish] micro_polish received empty text")
        return text

    prompt = build_polish_prompt(text)

    log_debug(
        f"[AIRA][polish] Starting micro‑polish pass: "
        f"model={model}, temperature={temperature}, max_tokens={max_tokens}"
    )

    try:
        response = llm_client.generate(
            prompt=prompt,
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
        )
    except Exception as e:
        log_error(f"[AIRA][polish] Error during micro‑polish LLM call: {e}")
        return text

    # Normalize response
    if isinstance(response, dict):
        rewritten = (
            response.get("text")
            or response.get("response")
            or response.get("content")
        )
    else:
        rewritten = response

    if not isinstance(rewritten, str):
        log_error("[AIRA][polish] LLM returned non-string output; keeping original")
        return text

    polished = rewritten.strip()
    if not polished:
        log_error("[AIRA][polish] LLM returned empty/whitespace; keeping original")
        return text

    log_debug(
        f"[AIRA][polish] Micro‑polish complete: "
        f"original_len={len(text)}, polished_len={len(polished)}"
    )

    return polished