# continuum/orchestrator/controller/controller_intent.py

import re
from continuum.core.logger import log_info, log_debug, log_error
from continuum.orchestrator.controller.intent_classifier import (
    build_intent_prompt,
    INTENT_LABELS,
)


# ============================================================
# Intent Classification (dedicated, non-recursive, lightweight)
# ============================================================
def classify_intent(controller, user_message: str) -> str:
    """
    Fast, cached intent classification.

    - Uses tiny local model
    - Avoids recursion
    - Avoids double calls per turn
    - Uses warm-up cache in LLMClient
    """

    # ---------------------------------------------------------
    # 0. Per-turn cache (prevents double LLM calls)
    # ---------------------------------------------------------
    if (
        hasattr(controller, "_last_intent_query")
        and controller._last_intent_query == user_message
    ):
        return controller._last_intent_result

    log_debug("INTENT DEBUG: entering classify_intent", phase="controller_intent")

    prompt = build_intent_prompt(user_message)
    log_debug(f"INTENT DEBUG: built prompt:\n{prompt}", phase="controller_intent")

    try:
        response = controller.llm_client.generate(
            prompt=prompt,
            model=controller.intent_classifier_model,
            temperature=0.0,
            max_tokens=8,
            endpoint=controller.intent_classifier_endpoint,
        )
    except Exception as e:
        log_error(f"LLM ERROR (intent classifier): {e}", phase="controller_intent")
        return "analysis"

    raw_text = _extract_intent_text(response)
    log_debug(f"INTENT DEBUG: raw_text: {repr(raw_text)}", phase="controller_intent")

    intent = _normalize_intent_label(raw_text)
    log_debug(f"INTENT DEBUG: normalized intent: {intent}", phase="controller_intent")

    if intent not in INTENT_LABELS:
        log_debug(
            f"INTENT WARNING: model returned unknown label '{intent}', "
            "falling back to 'analysis'"
        , phase="controller_intent")
        intent = "analysis"

    # ---------------------------------------------------------
    # Cache result for this turn
    # ---------------------------------------------------------
    controller._last_intent_query = user_message
    controller._last_intent_result = intent

    return intent


# ============================================================
# Helpers
# ============================================================
def _extract_intent_text(response) -> str:
    """
    Extract plain text from LLMClient.generate() response.
    """
    if isinstance(response, str):
        return response

    if hasattr(response, "text"):
        return response.text

    if isinstance(response, dict):
        if "text" in response:
            return response["text"]
        if "content" in response:
            return response["content"]

    return str(response)


def _normalize_intent_label(raw_text: str) -> str:
    """
    Take the raw model output and extract a single valid label.
    """
    if not raw_text:
        return "analysis"

    text = raw_text.strip().lower()
    log_debug(f"INTENT DEBUG: normalized raw text: {repr(text)}", phase="controller_intent")

    if text in INTENT_LABELS:
        return text

    for label in INTENT_LABELS:
        pattern = r"\b" + re.escape(label) + r"\b"
        if re.search(pattern, text):
            return label

    return "analysis"