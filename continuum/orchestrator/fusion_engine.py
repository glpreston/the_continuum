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

    # Proposals keyed by Senate actor names
    proposals_by_actor = {p.get("actor"): p for p in ranked_proposals}

    candidate_chunks = []

    for senate_name, weight in fusion_weights.items():
        if weight <= 0:
            continue

        # Map Senate actor → LLM actor
        llm_name = controller.senate_to_llm_map.get(senate_name, senate_name)

        proposal = proposals_by_actor.get(senate_name)
        if proposal is None:
            continue

        actor = controller.actors.get(llm_name)
        if actor is None:
            continue

        text = actor.respond(
            context=controller.context,
            selected_proposal=proposal,
            emotional_memory=controller.emotional_memory,
            emotional_state=EmotionalState.from_dict(
                controller.emotional_state.as_dict()
            ),
        )

        candidate_chunks.append((llm_name, weight, text))

    if not candidate_chunks:
        return "The Continuum encountered an error: no valid actors for fusion."

    # Sort by weight (highest first)
    candidate_chunks.sort(key=lambda x: x[1], reverse=True)

    # The winning proposal is the one with the highest weight
    winning_llm_name = candidate_chunks[0][0]
    winning_senate_name = None

    # Reverse lookup: find the Senate actor that maps to this LLM actor
    for senate_name, llm_name in controller.senate_to_llm_map.items():
        if llm_name == winning_llm_name:
            winning_senate_name = senate_name
            break

    # Store the final proposal for Meta‑Persona
    if winning_senate_name:
        controller.last_final_proposal = proposals_by_actor.get(winning_senate_name)

    fused_raw = "\n\n".join(chunk[2].strip() for chunk in candidate_chunks)
    controller.last_raw_actor_output = fused_raw

    rewritten = controller.meta_persona.render(
        fused_raw,
        controller,
        controller.context,
        controller.emotional_state,
        controller.emotional_memory,
    )

    return rewritten