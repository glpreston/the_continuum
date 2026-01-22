from typing import Dict, List, Any
from continuum.emotion.state_machine import EmotionalState
from continuum.orchestrator.fusion_filters import filter_sentences


def fused_response(
    fusion_weights: Dict[str, float],
    ranked_proposals: List[Dict[str, Any]],
    controller: Any,
) -> str:
    """
    Fusion 2.1:
      - Weight‑aware blending
      - Meaning extraction (not naive truncation)
      - Deduplication
      - Semantic filtering (refusal, meta, safety, fragments, user‑echo)
      - Unified single‑paragraph synthesis
      - Meta‑Persona rewrite into final voice
    """

    # Proposals keyed by Senate actor names
    proposals_by_actor = {p.get("actor"): p for p in ranked_proposals}

    # Sort actors by descending weight
    weighted_actors = sorted(
        fusion_weights.items(),
        key=lambda x: x[1],
        reverse=True
    )

    # Get the last user message (for echo filtering)
    last_user = controller.context.last_user_message()
    user_message = last_user.content if last_user else ""

    # ---------------------------------------------------------
    # 1. Extract distilled meaning from each actor proposal
    # ---------------------------------------------------------
    distilled_points: List[str] = []
    seen = set()

    for senate_name, weight in weighted_actors:
        if weight <= 0:
            continue

        proposal = proposals_by_actor.get(senate_name)
        if not proposal:
            continue

        text = proposal.get("content", "")
        if not text:
            continue

        # Break into sentences
        sentences = [s.strip() for s in text.split(".") if s.strip()]
        if not sentences:
            continue

        # Weight‑aware selection
        if weight >= 0.75:
            selected = sentences[:2]
        elif weight >= 0.40:
            selected = sentences[:1]
        else:
            selected = [sentences[0][:120]]

        for s in selected:
            if not s:
                continue

            # Apply semantic filtering (refusal, meta, safety, fragments, user‑echo)
            filtered = filter_sentences([s], user_message)
            if not filtered:
                continue

            s = filtered[0]

            # Deduplication
            key = s.lower().strip()
            if key in seen:
                continue

            seen.add(key)
            distilled_points.append(s)

    # ---------------------------------------------------------
    # 2. Fallback: if nothing survived, use top actor’s content
    # ---------------------------------------------------------
    if not distilled_points and weighted_actors:
        top_actor = weighted_actors[0][0]
        proposal = proposals_by_actor.get(top_actor, {})
        text = proposal.get("content", "") or ""
        distilled_points = [text.strip()[:300]]

    # If still nothing, hard fallback
    if not distilled_points:
        fused_raw = (
            "The Continuum could not derive a coherent synthesis "
            "from the available proposals."
        )
    else:
        # ---------------------------------------------------------
        # 3. Build a unified paragraph
        # ---------------------------------------------------------
        fused_raw = " ".join(distilled_points).strip()

    # Store raw fused actor output for debugging/inspection
    controller.last_raw_actor_output = fused_raw

    # ---------------------------------------------------------
    # Ensure controller.last_final_proposal is always set
    # ---------------------------------------------------------
    if not controller.last_final_proposal:
        if weighted_actors:
            top_actor = weighted_actors[0][0]
            controller.last_final_proposal = proposals_by_actor.get(top_actor)
        if not controller.last_final_proposal:
            controller.last_final_proposal = ranked_proposals[0]

    # ---------------------------------------------------------
    # 4. Meta‑Persona rewrite into final voice
    # ---------------------------------------------------------
    rewritten = controller.meta_persona.render(
        fused_raw,
        controller,
        controller.context,
        controller.emotional_state,
        controller.emotional_memory,
    )

    return rewritten