# continuum/orchestrator/controller_process.py
# Modernized message‑processing pipeline for ContinuumController (Phase‑5)

from email.mime import message
import time
import re

from continuum.core.logger import log_debug, log_info, log_error
from continuum.db.models.cognitive_trace import CognitiveTrace
from continuum.orchestrator.controller.intent_routing import INTENT_TO_ACTORS
from continuum.orchestrator.controller.controller_intent import classify_intent


# ============================
# CONTROLLER CONSTANTS (Phase‑5)
# ============================

GREETER_FASTPATH_INTENTS = ("greeting", "chitchat")
DEFAULT_ACTOR_FALLBACK = "Architect"

# Option C — intent‑only Greeter fast‑path
ENABLE_GREETER_INTENT_FASTPATH = True

def is_greeting_message(message: str) -> bool:
    if not message:
        return False

    msg = message.lower().strip()

    GREETING_PATTERNS = [
        r"^hello\b",
        r"^hi\b",
        r"^hey\b",
        r"^hiya\b",
        r"^yo\b",
        r"^greetings\b",
        r"^good (morning|afternoon|evening)\b",
    ]

    for pattern in GREETING_PATTERNS:
        if re.match(pattern, msg):
            return True

    return False

def process_message(
    controller,
    message: str,
    *,
    trace: bool = True,
    rewrite: bool = True,
) -> str:
    """
    Full processing pipeline for a single user message.
    Router‑aware + cognitively traced + MetaPersona‑integrated.
    """

    t_total_start = time.perf_counter()
    timings: dict[str, float] = {}

    # 0. Add user message to context
    controller.context.add_user_message(message)

    # 1. Emotion detection
    t_emotion_start = time.perf_counter()
    raw_state, dominant_emotion, intensity = controller.emotion_detector.detect(message)
    log_debug(
        f"[PROCESS] Emotion detected: {dominant_emotion} ({intensity})",
        phase="emotion",
    )

    controller.emotional_memory.add_event(
        raw_state=raw_state,
        dominant_emotion=dominant_emotion,
        metadata={"source": "model"},
    )

    controller.emotional_state = controller.state_manager.update(
        controller.emotional_state,
        raw_state,
    )
    timings["emotion_time"] = time.perf_counter() - t_emotion_start

    # 2. Restore routing info (for fusion / rewrite / trace)
    routing = getattr(controller, "last_routing_decision", None) or {}
    model_choice = routing.get("model_selection", {})
    node_choice = routing.get("node_selection", {})

    # 3. Intent classification → actors_to_run
    intent = classify_intent(controller, message)
    
    # Phase‑5 Greeting Override (Option B)
    if is_greeting_message(message):
        intent = "greeting"

    actors_to_run = INTENT_TO_ACTORS.get(intent, [DEFAULT_ACTOR_FALLBACK])

    log_debug(f"[INTENT] Classified as: {intent}", phase="intent")
    log_debug(f"[INTENT] Actors to run: {actors_to_run}", phase="intent")

    # 3a. Greeter FAST‑PATH (intent‑only)
    greeter_actor = controller.actors.get("Greeter")

    should_fastpath_greeter = (
        ENABLE_GREETER_INTENT_FASTPATH
        and intent in GREETER_FASTPATH_INTENTS
        and "Greeter" in actors_to_run
        and greeter_actor is not None
    )

    if should_fastpath_greeter:
        log_debug("⚡ FAST‑PATH: Bypassing Senate/Jury for Greeter", phase="fastpath")

        t_greeter_start = time.perf_counter()
        proposal = greeter_actor.propose(
            controller=controller,
            message=message,
            context=controller.context,
            emotional_state=controller.emotional_state,
            emotional_memory=controller.emotional_memory,
            memory=controller.memory,
            voiceprint=getattr(controller, "voiceprint", None),
            metadata={},
            telemetry=None,
        )
        timings["deliberation_time"] = time.perf_counter() - t_greeter_start

        final_text = proposal.get("content") if isinstance(proposal, dict) else str(proposal)

        # Optional MetaPersona rewrite
        if rewrite:
            log_debug("🔥 CALLING META‑PERSONA REWRITE (FAST‑PATH) 🔥", phase="meta")
            t_rewrite_start = time.perf_counter()
            rewritten = controller.meta_persona.render(
                text=final_text,
                persona_name="Aira",
                emotion=dominant_emotion,
                controller=controller,
                context=controller.context,
                emotional_state=controller.emotional_state,
                emotional_memory=controller.emotional_memory,
                actor_name="Greeter",
            )
            timings["rewrite_time"] = time.perf_counter() - t_rewrite_start
        else:
            rewritten = final_text
            timings["rewrite_time"] = 0.0

        controller.context.add_assistant_message(rewritten)

        total_time = time.perf_counter() - t_total_start
        timings["total_time"] = total_time
        timings.setdefault("fusion_adjust_time", 0.0)
        timings.setdefault("fusion_run_time", 0.0)

        if trace:
            controller.last_trace = {
                "timings": timings,
                "routing": routing,
                "ranked_proposals": [],
                "final_proposal": {"actor": "Greeter", "content": final_text},
                "fusion_output": final_text,
                "rewritten_output": rewritten,
                "emotion": {
                    "dominant": dominant_emotion,
                    "intensity": intensity,
                },
                "actor_timings": None,
            }

        return rewritten

    # 4. Senate → Jury deliberation
    log_debug("🔥 CALLING DELIBERATION ENGINE 🔥", phase="delib")
    t_delib_start = time.perf_counter()
    ranked, final_proposal = controller.deliberation_engine.run(
        controller=controller,
        context=controller.context,
        message=message,
        emotional_state=controller.emotional_state,
        emotional_memory=controller.emotional_memory,
        actors_to_run=actors_to_run,
    )
    timings["deliberation_time"] = time.perf_counter() - t_delib_start

    log_debug(f"[PROCESS] Final proposal from Jury: {final_proposal}", phase="delib")

    # Guard if Senate/Jury produced nothing
    if not ranked:
        total_time = time.perf_counter() - t_total_start
        timings["total_time"] = total_time

        actor_timings = getattr(controller, "last_trace", {}).get("actor_timings", None)

        if trace:
            controller.last_trace = {
                "timings": timings,
                "routing": routing,
                "ranked_proposals": ranked,
                "final_proposal": final_proposal,
                "fusion_output": None,
                "rewritten_output": None,
                "emotion": {
                    "dominant": dominant_emotion,
                    "intensity": intensity,
                },
                "actor_timings": actor_timings,
            }

        return (
            "The Continuum encountered an internal issue: "
            "no proposals were generated by the actors/Senate for this request."
        )

    # 5. Fusion adjust
    log_debug("🔥 CALLING FUSION ADJUST 🔥", phase="fusion")
    t_fusion_adjust_start = time.perf_counter()
    fusion_weights = controller.fusion_pipeline.adjust(final_proposal)
    timings["fusion_adjust_time"] = time.perf_counter() - t_fusion_adjust_start
    log_debug(f"[PROCESS] Fusion weights: {fusion_weights}", phase="fusion")

    # 6. Fusion run
    log_debug("🔥 CALLING FUSION RUN 🔥", phase="fusion")
    t_fusion_run_start = time.perf_counter()
    final_text = controller.fusion_pipeline.run(
        fusion_weights=fusion_weights,
        ranked_proposals=ranked,
        controller=controller,
        routing=routing,
    )
    timings["fusion_run_time"] = time.perf_counter() - t_fusion_run_start
    log_debug(f"[PROCESS] Final text before rewrite: {final_text}", phase="fusion")

    controller.last_final_proposal = {
        "actor": "FusionEngine",
        "content": final_text,
        "metadata": {
            "source": "max_hybrid_fusion",
            "fusion_weights": fusion_weights,
            "jury_proposal": final_proposal,
            "routing": routing,
        },
    }

    jury_winner = final_proposal.get("actor") if isinstance(final_proposal, dict) else None
    primary_actor = jury_winner or (actors_to_run[0] if actors_to_run else None)

    # 7. Meta‑Persona rewrite (optional)
    if rewrite:
        log_debug("🔥 CALLING META‑PERSONA REWRITE 🔥", phase="meta")
        t_rewrite_start = time.perf_counter()
        rewritten = controller.meta_persona.render(
            text=final_text,
            persona_name="Aira",
            emotion=dominant_emotion,
            controller=controller,
            context=controller.context,
            emotional_state=controller.emotional_state,
            emotional_memory=controller.emotional_memory,
            actor_name=primary_actor,
        )
        timings["rewrite_time"] = time.perf_counter() - t_rewrite_start
    else:
        rewritten = final_text
        timings["rewrite_time"] = 0.0

    log_debug(f"[PROCESS] Rewritten output: {rewritten}", phase="meta")
    controller.context.add_assistant_message(rewritten)

    # 8. Emotional arc recording
    controller.arc_pipeline.record(
        emotional_state=controller.emotional_state,
        dominant_emotion=dominant_emotion,
        fusion_weights=fusion_weights,
    )
    log_debug("[PROCESS] Emotional arc snapshot recorded", phase="emotion_arc")

    # 9. Turn logging (lightweight)
    controller.turn_logger.append(
        {
            "message": final_text,
            "emotion": controller.emotional_state,
            "proposals": ranked,
            "routing": routing,
        }
    )

    # 10. Cognitive trace assembly + DB insert (optional)
    total_time = time.perf_counter() - t_total_start
    timings["total_time"] = total_time

    if trace:
        model_name = model_choice.get("selected_model")
        node_name = node_choice.get("selected_node", {}).get("name")

        actor_confidence = final_proposal.get("confidence") if isinstance(final_proposal, dict) else None
        actor_output = final_proposal.get("content") if isinstance(final_proposal, dict) else ""
        actor_output_length = len(actor_output or "")

        rewrite_delta = len(rewritten or "") - len(final_text or "")

        senate_time = timings.get("deliberation_time")
        jury_time = None
        fusion_time = (
            timings.get("fusion_adjust_time", 0.0)
            + timings.get("fusion_run_time", 0.0)
        )

        record = CognitiveTrace(
            actor_name=jury_winner,
            model_name=model_name,
            node_name=node_name,
            routing_time=None,
            actor_time=None,
            senate_time=senate_time,
            jury_time=jury_time,
            fusion_time=fusion_time,
            rewrite_time=timings.get("rewrite_time"),
            total_time=total_time,
            actor_confidence=actor_confidence,
            actor_output_length=actor_output_length,
            jury_winner=jury_winner,
            jury_scores=None,
            rewrite_delta=rewrite_delta,
            error_flag=False,
            error_message=None,
        )

        try:
            controller.db.add(record)
            controller.db.commit()
        except Exception as e:
            log_error(f"[TRACE] Failed to persist CognitiveTrace: {e}", phase="trace")
            controller.db.rollback()

        actor_timings = getattr(controller, "last_trace", {}).get("actor_timings", None)

        controller.last_trace = {
            "timings": timings,
            "routing": routing,
            "ranked_proposals": ranked,
            "final_proposal": final_proposal,
            "fusion_output": final_text,
            "rewritten_output": rewritten,
            "emotion": {
                "dominant": dominant_emotion,
                "intensity": intensity,
            },
            "actor_timings": actor_timings,
        }

    return rewritten