#continuum/orchestrator/fusion_engine.py

from typing import Dict, List, Any
from continuum.orchestrator.fusion_filters import filter_sentences

def fused_response(
    fusion_weights: Dict[str, float],
    ranked_proposals: List[Dict[str, Any]],
    controller: Any,
) -> str:
    """
    Fusion 3.0 — MAX‑HYBRID MODE
      - Synthesizer full backbone
      - Architect always contributes 1–2 sentences
      - Analyst always contributes 1 sentence
      - Storyweaver always contributes 1 sentence
      - Filtering is softened (never blocks distilled actors)
      - Dedup is minimal (exact-match only)
      - Debug mode prints distilled_points before rewrite
      - Meta‑Persona rewrites final unified paragraph
    """
    print("\n>>> ENTERED fused_response() — MAX‑HYBRID ACTIVE <<<\n")

    # ---------------------------------------------------------
    # 1) Normalize proposals by actor (lower‑cased keys)
    # ---------------------------------------------------------
    proposals_by_actor: Dict[str, Dict[str, Any]] = {}
    for p in ranked_proposals:
        actor_name = (p.get("actor") or "").strip().lower()
        if actor_name:
            proposals_by_actor[actor_name] = p

    # ---------------------------------------------------------
    # 2) Depth‑boosted weighting (Fusion‑2.1)
    # ---------------------------------------------------------
    def boosted_weight(actor_name: str, base_weight: float) -> float:
        normalized = (actor_name or "").strip().lower()
        proposal = proposals_by_actor.get(normalized, {})
        scores = proposal.get("metadata", {}).get("jury_scores", {}) or {}
        depth = scores.get("semantic_depth", 0.0)
        integrative = scores.get("integrative_reasoning", 0.0)

        return base_weight * (1 + 0.6 * depth + 0.5 * integrative)

    weighted_actors = sorted(
        [(name, boosted_weight(name, w)) for name, w in fusion_weights.items()],
        key=lambda x: x[1],
        reverse=True,
    )

    # ---------------------------------------------------------
    # 3) Get last user message for echo filtering
    # ---------------------------------------------------------
    last_user = controller.context.last_user_message()
    user_message = last_user.content if last_user else ""

    # ---------------------------------------------------------
    # 4) MAX‑HYBRID FUSION
    # ---------------------------------------------------------
    distilled_points: List[str] = []
    seen: set[str] = set()

    ordered_actors = ["synthesizer", "architect", "analyst", "storyweaver"]

    for actor in ordered_actors:
        proposal = proposals_by_actor.get(actor)
        if not proposal:
            continue

        text = (proposal.get("content") or "").strip()
        if not text:
            continue

        # 4a) Synthesizer → full backbone
        if actor == "synthesizer":
            distilled_points.append(text)
            continue

        # 4b) Distilled sentences for other actors
        sentences = [s.strip() for s in text.split(".") if s.strip()]
        if not sentences:
            continue

        if actor == "architect":
            selected = sentences[:2]
        elif actor == "analyst":
            selected = sentences[:1]
        elif actor == "storyweaver":
            selected = sentences[:1]
        else:
            selected = sentences[:1]

        for s in selected:
            if not s:
                continue

            # 4c) Soft filtering — NEVER blocks distilled actors
            filtered = filter_sentences([s], user_message)
            if not filtered:
                filtered = [s]

            s = filtered[0]

            # 4d) Minimal dedup — exact match only
            key = s.lower()
            if key in seen:
                continue

            seen.add(key)
            distilled_points.append(s)

    # ---------------------------------------------------------
    # 4.5) DEBUG MODE — print distilled_points before rewrite
    # ---------------------------------------------------------
    if getattr(controller, "debug_fusion", False):
        print("\n================ HYBRID FUSION DEBUG ================")
        print("Distilled Points (pre‑rewrite):")
        for i, dp in enumerate(distilled_points, 1):
            print(f"{i}. {dp}")
        print("=====================================================\n")

    # ---------------------------------------------------------
    # 5) Fallback if somehow empty (should never happen in Max‑Hybrid)
    # ---------------------------------------------------------
    if not distilled_points and weighted_actors:
        top_actor_name = weighted_actors[0][0]
        top_actor_norm = (top_actor_name or "").strip().lower()
        proposal = proposals_by_actor.get(top_actor_norm, {})
        text = (proposal.get("content") or "").strip()
        if text:
            distilled_points = [text[:300]]

    if not distilled_points:
        fused_raw = (
            "The Continuum could not derive a coherent synthesis "
            "from the available proposals."
        )
    else:
        # ---------------------------------------------------------
        # 6) Build unified paragraph
        # ---------------------------------------------------------
        fused_raw = (
            " ".join(distilled_points)
            .replace("..", ".")
            .strip()
        )

    controller.last_raw_actor_output = fused_raw

    # ---------------------------------------------------------
    # 7) Ensure controller.last_final_proposal is always set
    # ---------------------------------------------------------
    if not controller.last_final_proposal:
        if weighted_actors:
            top_actor_name = weighted_actors[0][0]
            top_actor_norm = (top_actor_name or "").strip().lower()
            controller.last_final_proposal = proposals_by_actor.get(top_actor_norm)
        if not controller.last_final_proposal and ranked_proposals:
            controller.last_final_proposal = ranked_proposals[0]

    # ---------------------------------------------------------
    # 8) Meta‑Persona rewrite
    # ---------------------------------------------------------
    rewritten = controller.meta_persona.render(
        fused_raw,
        controller,
        controller.context,
        controller.emotional_state,
        controller.emotional_memory,
    )

    return rewritten