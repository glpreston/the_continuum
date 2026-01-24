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

    # Depth‑boosted weighting (Fusion‑2.1)
    def boosted_weight(actor_name, base_weight):
        proposal = proposals_by_actor.get(actor_name, {})
        scores = proposal.get("metadata", {}).get("jury_scores", {})
        depth = scores.get("semantic_depth", 0.0)
        integrative = scores.get("integrative_reasoning", 0.0)

        # Nonlinear boost: deeper + more integrative actors get more influence
        return base_weight * (1 + 0.6 * depth + 0.5 * integrative)

    weighted_actors = sorted(
        [(name, boosted_weight(name, w)) for name, w in fusion_weights.items()],
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
        # Fusion‑2.1: structure‑preserving selection
        if weight >= 0.75:
            # Keep first 2 sentences to preserve structure
            selected = sentences[:2]
        elif weight >= 0.40:
            # Keep the strongest opening sentence
            selected = sentences[:1]
        else:
            # Keep a short conceptual fragment
            selected = [sentences[0][:160]]

        for s in selected:
            if not s:
                continue

            # Apply semantic filtering (refusal, meta, safety, fragments, user‑echo)
            filtered = filter_sentences([s], user_message)
            if not filtered:
                continue

            s = filtered[0]

            # Deduplication
        # Fusion‑2.1: stronger redundancy suppression
        key = " ".join(s.lower().split())
        if any(key in existing.lower() or existing.lower() in key for existing in seen):
            continue

        seen.add(s)
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
        # Fusion‑2.1: preserve conceptual flow
        fused_raw = (
            " ".join(distilled_points)
            .replace("..", ".")
            .strip()
        )
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