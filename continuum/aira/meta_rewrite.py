# continuum/aira/meta_rewrite.py
print("USING META_REWRITE FILE:", __file__)

from typing import Optional

from continuum.core.logger import log_debug, log_error

from continuum.aira.rewrite_loop import rewrite_loop
from continuum.aira.polish import micro_polish
from continuum.aira.safety import validate_rewrite


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


def meta_rewrite_llm(
    controller,
    core_text: str | None = None,
    proposal: dict | None = None,
    emotion_label: str | None = None,
    enable_micro_polish: bool = True,
    routing: dict | None = None,
    **kwargs,
) -> str:
    """
    Aira Meta‑Persona rewrite hook (Phase‑5, Router-aware).

    Pipeline:
    - Extract base text from core_text/proposal
    - Use SAME model + node as main generation (via Router)
    - Build memory summary
    - Run multi‑pass rewrite loop
    - Optionally run micro‑polish
    - Return final Aira‑voiced text
    """

    log_debug("[AIRA] meta_rewrite_llm invoked")

    base_text = _extract_base_text(core_text, proposal)
    if not base_text:
        log_error("[AIRA] No valid core_text or proposal content")
        return "The Continuum encountered an error: no proposals available."

    if not emotion_label:
        emotion_label = "neutral"

    # Routing: use same model + node as main generation
    routing = routing or getattr(controller, "last_routing_decision", None)
    if not routing:
        log_error("[AIRA] No routing decision available for rewrite; falling back to base_text")
        return base_text

    model_sel = routing.get("model_selection", {})
    node_sel = routing.get("node_selection", {})

    if not model_sel.get("candidates"):
        log_error("[AIRA] Routing missing model candidates; falling back to base_text")
        return base_text

    model = model_sel["candidates"][0]["model"]
    node = node_sel.get("selected_node")
    if not node:
        log_error("[AIRA] Routing missing selected_node; falling back to base_text")
        return base_text

    host = node.get("host")
    port = node.get("port")
    if not host:
        log_error("[AIRA] Routing missing host; falling back to base_text")
        return base_text

    if host.startswith("http://") or host.startswith("https://"):
        base = host.rstrip("/")
        if port:
            if ":" not in base.split("//", 1)[1]:
                base = f"{base}:{port}"
    else:
        base = f"http://{host}"
        if port:
            base = f"{base}:{port}"

    endpoint = f"{base}/api/generate"

    # Controller settings
    llm_client = controller.llm_client
    base_temperature = getattr(controller, "temperature", 0.7)
    max_tokens = getattr(controller, "max_tokens", 1024)
    max_rewrite_depth = getattr(controller, "max_rewrite_depth", 3)

    # Memory summary for Aira's prompt
    try:
        if hasattr(controller, "context") and hasattr(controller.context, "get_memory_summary"):
            memory_summary = controller.context.get_memory_summary()
        else:
            memory_summary = ""
    except Exception as e:
        log_error(f"[AIRA] Error getting memory summary: {e}")
        memory_summary = ""

    log_debug(
        f"[AIRA] Starting Aira rewrite with model={model}, "
        f"endpoint={endpoint}, emotion_label={emotion_label}, "
        f"max_rewrite_depth={max_rewrite_depth}"
    )

    # -----------------------------
    # Multi‑pass rewrite loop
    # -----------------------------
    try:
        rewritten = rewrite_loop(
            llm_client=llm_client,
            model=model,
            endpoint=endpoint,
            base_text=base_text,
            memory_summary=memory_summary,
            emotion_label=emotion_label,
            base_temperature=base_temperature,
            max_tokens=max_tokens,
            max_rewrite_depth=max_rewrite_depth,
        )
    except Exception as e:
        log_error(f"[AIRA] Error in rewrite_loop: {e}")
        return base_text

    if not validate_rewrite(base_text, rewritten):
        log_error("[AIRA] Rewrite validation failed, falling back to base_text")
        return base_text

    final_text = rewritten

    # -----------------------------
    # Optional micro‑polish pass
    # -----------------------------
    if enable_micro_polish:
        try:
            polished = micro_polish(
                llm_client=llm_client,
                model=model,
                endpoint=endpoint,
                text=final_text,
                temperature=0.3,
                max_tokens=max_tokens,
            )

            if validate_rewrite(final_text, polished):
                final_text = polished
            else:
                log_error("[AIRA] Micro‑polish validation failed, keeping pre‑polish text")

        except Exception as e:
            log_error(f"[AIRA] Error during micro‑polish: {e}")

    log_debug(
        f"[AIRA] meta_rewrite_llm complete. "
        f"original_len={len(base_text)}, final_len={len(final_text)}"
    )

    return final_text