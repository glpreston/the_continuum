# continuum/orchestrator/fusion_engine.py

from typing import Dict, List, Any
from continuum.emotion.state_machine import EmotionalState


def fused_response(
    fusion_weights: Dict[str, float],
    ranked_proposals: List[Dict[str, Any]],
    controller: Any,
) -> str:
    """
    Build a fused response by calling each actor according to its weight
    and then letting Meta‑Persona unify the final text.
    """
    proposals_by_actor = {p.get("actor"): p for p in ranked_proposals}

    candidate_chunks = []
    for actor_name, weight in fusion_weights.items():
        if weight <= 0:
            continue

        actor = controller.actors.get(actor_name)
        if actor is None:
            continue

        proposal = proposals_by_actor.get(actor_name, {})
        text = actor.respond(
            context=controller.context,
            proposal=proposal,
            emotional_memory=controller.emotional_memory,
            emotional_state=EmotionalState.from_dict(
                controller.emotional_state.as_dict()
            ),
        )
        candidate_chunks.append((actor_name, weight, text))

    if not candidate_chunks:
        return "The Continuum encountered an error: no valid actors for fusion."

    candidate_chunks.sort(key=lambda x: x[1], reverse=True)
    fused_raw = "\n\n".join(chunk[2].strip() for chunk in candidate_chunks)

    controller.last_raw_actor_output = fused_raw

    # PATCHED: updated MetaPersona.render call
    rewritten = controller.meta_persona.render(
        fused_raw,
        controller,                 # NEW
        controller.context,
        controller.emotional_state,
        controller.emotional_memory,
    )

    return rewritten