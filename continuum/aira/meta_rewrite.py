# continuum/aira/meta_rewrite.py

"""
Phase‑5.1 — Meta‑Rewrite Compatibility Layer
--------------------------------------------

This module is retained ONLY for:
- UI tools
- Debugging
- Backwards compatibility

The actual rewrite engine now lives in:
    continuum.persona.meta_persona.MetaPersona.render()

This file provides:
- Aira_Lite fast‑path rewrite
- A thin wrapper around MetaPersona.render()
- A simplified emotional rewrite wrapper

All legacy rewrite logic (rewrite_loop, micro_polish, tone prefixes,
routing, memory summaries, ArcPoint conversions, etc.) has been removed.
"""

import datetime
from typing import Optional

from continuum.core.logger import log_debug, log_error
from continuum.persona.meta_persona import MetaPersona
from continuum.persona.style_rewrite import apply_style


# -------------------------------------------------------------------
# Constants (Phase‑6: move to DB/config)
# -------------------------------------------------------------------

DEFAULT_EMOTION_LABEL = "neutral"

AIRA_LITE_MODEL = "qwen2.5:0.5b"
AIRA_LITE_MAX_TOKENS = 128
AIRA_LITE_TEMPERATURE = 0.4

FALLBACK_NO_PROPOSAL_MESSAGE = (
    "The Continuum encountered an error: no proposals were available for rewrite."
)


# -------------------------------------------------------------------
# Helpers
# -------------------------------------------------------------------

def _extract_base_text(core_text: Optional[str], proposal: Optional[dict]) -> Optional[str]:
    """
    Determine the base text to rewrite from core_text or proposal.
    """
    if isinstance(core_text, str) and core_text.strip():
        return core_text.strip()

    if isinstance(proposal, dict):
        candidate = (
            proposal.get("content")
            or proposal.get("text")
            or proposal.get("message")
        )
        if isinstance(candidate, str) and candidate.strip():
            return candidate.strip()

    return None


# -------------------------------------------------------------------
# Aira‑Lite Fast Path
# -------------------------------------------------------------------

def _aira_lite_rewrite(
    controller,
    core_text: str | None,
    proposal: dict | None,
):
    """
    Ultra‑fast rewrite path for greetings/chitchat using Aira_Lite persona.
    - Uses a tiny model (qwen2.5:0.5b)
    - Single‑pass rewrite
    - No rewrite_loop, no micro‑polish
    """

    base_text = _extract_base_text(core_text, proposal)
    if not base_text:
        log_debug("[AIRA_LITE][meta_rewrite] No base_text; returning default greeting")
        return "Hello!"

    llm_client = controller.llm_client

    try:
        rewritten = llm_client.generate(
            model=AIRA_LITE_MODEL,
            prompt=base_text,
            max_tokens=AIRA_LITE_MAX_TOKENS,
            temperature=AIRA_LITE_TEMPERATURE,
        )
    except Exception as e:
        log_error(f"[AIRA_LITE][meta_rewrite] Error during rewrite: {e}")
        return base_text

    # Normalize rewritten output
    if isinstance(rewritten, dict):
        rewritten = (
            rewritten.get("response")
            or rewritten.get("content")
            or str(rewritten)
        )

    if not isinstance(rewritten, str):
        rewritten = str(rewritten)

    rewritten = rewritten.strip()
    if not rewritten:
        log_error("[AIRA_LITE][meta_rewrite] Empty rewrite output; falling back to base_text")
        return base_text

    return rewritten


# -------------------------------------------------------------------
# Phase‑5 Meta‑Rewrite Wrapper
# -------------------------------------------------------------------

def meta_rewrite_llm(
    controller,
    core_text: str | None = None,
    proposal: dict | None = None,
    persona_name: str | None = "Aira",
    **kwargs,
) -> str:
    """
    Thin Phase‑5 wrapper around MetaPersona.render().

    - Extracts base text
    - Routes Aira_Lite to fast path
    - Delegates all rewriting to MetaPersona.render()
    """

    log_debug(
        "[AIRA][meta_rewrite] meta_rewrite_llm invoked "
        f"(persona={persona_name})"
    )

    # Aira_Lite fast path
    if persona_name == "Aira_Lite":
        return _aira_lite_rewrite(
            controller=controller,
            core_text=core_text,
            proposal=proposal,
        )

    base_text = _extract_base_text(core_text, proposal)
    if not base_text:
        log_error("[AIRA][meta_rewrite] No valid core_text or proposal content")
        return FALLBACK_NO_PROPOSAL_MESSAGE

    try:
        persona_engine: MetaPersona = controller.persona_engine
        return persona_engine.render(
            text=base_text,
            persona_name=persona_name,
            **kwargs,
        )
    except Exception as e:
        log_error(f"[AIRA][meta_rewrite] Error in MetaPersona.render(): {e}")
        return base_text


# -------------------------------------------------------------------
# Emotional Rewrite Wrapper (Simplified Phase‑5D)
# -------------------------------------------------------------------

def emotional_rewrite(
    controller,
    core_text: str | None = None,
    user_text: str | None = None,
    user_emotion: str | None = None,
    style_weights: dict | None = None,
    proposal: dict | None = None,
    persona_name: str | None = "Aira",
    **kwargs,
):
    """
    Simplified emotional rewrite pipeline:
    - Update emotion state
    - Call MetaPersona.render()
    - Apply persona style
    - Apply emotional modulation
    """

    if user_text is None:
        user_text = core_text

    if user_emotion is None:
        user_emotion = DEFAULT_EMOTION_LABEL

    if style_weights is None:
        style_weights = {}

    log_debug(
        "[AIRA][emotional_rewrite] Invoked "
        f"(user_emotion={user_emotion}, style_weights_keys={list(style_weights.keys())})"
    )

    # 1. Update emotional state
    try:
        controller.emotion_transition.apply_user_emotion(user_emotion)
    except Exception as e:
        log_error(f"[AIRA][emotional_rewrite] Error applying user emotion: {e}")

    # 2. Core rewrite via MetaPersona
    try:
        persona_engine: MetaPersona = controller.persona_engine
        rewritten = persona_engine.render(
            text=user_text,
            persona_name=persona_name,
            emotion=user_emotion,
            **kwargs,
        )
    except Exception as e:
        log_error(f"[AIRA][emotional_rewrite] Error in MetaPersona.render(): {e}")
        rewritten = user_text

    # 3. Apply persona style
    styled = apply_style(rewritten, style_weights)

    # 4. Apply emotional modulation
    try:
        final = controller.emotion_modulation.modulate(styled, style_weights)
    except Exception as e:
        log_error(f"[AIRA][emotional_rewrite] Error during emotional modulation: {e}")
        final = styled

    log_debug(
        "[AIRA][emotional_rewrite] Complete "
        f"(final_len={len(final)})"
    )

    return final