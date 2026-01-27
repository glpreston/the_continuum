# continuum/orchestrator/controller_process.py
# Main message‑processing pipeline for ContinuumController

from continuum.core.logger import log_debug, log_error


def process_message(controller, message: str) -> str:
    """
    Full processing pipeline for a single user message.
    Handles:
      - Emotion detection
      - Emotional state update
      - Senate → Jury deliberation
      - Fusion 2.0
      - Meta‑Persona rewrite
      - Emotional arc recording
      - Turn logging
    """

    log_error("🔥 ENTERED controller_process.process_message() 🔥", phase="controller")

    controller.context.add_user_message(message)

    # ---------------------------------------------------------
    # 1. Emotion detection
    # ---------------------------------------------------------
    raw_state, dominant_emotion, intensity = controller.emotion_detector.detect(message)
    log_debug(f"[PROCESS] Emotion detected: {dominant_emotion} ({intensity})", phase="emotion")

    controller.emotional_memory.add_event(
        raw_state=raw_state,
        dominant_emotion=dominant_emotion,
        metadata={"source": "model"},
    )

    controller.emotional_state = controller.state_manager.update(
        controller.emotional_state,
        raw_state,
    )

    # ---------------------------------------------------------
    # 2. Senate → Jury deliberation (now selector‑aware)
    # ---------------------------------------------------------
    log_error("🔥 CALLING DELIBERATION ENGINE 🔥", phase="delib")

    """
    ranked, final_proposal = controller.deliberation_engine.run(
        controller=controller,
        context=controller.context,
        message=message,
        emotional_state=controller.emotional_state,
        emotional_memory=controller.emotional_memory,
        select_model=controller.select_model,   # ⭐ Inject selector here
    )"""

    ranked, final_proposal = controller.deliberation_engine.run(
        controller,
        controller.context,
        message,
        controller.emotional_state,
        controller.emotional_memory,
    )


    log_debug(f"[PROCESS] Final proposal from Jury: {final_proposal}", phase="delib")

    # ---------------------------------------------------------
    # 3. Fusion adjust
    # ---------------------------------------------------------
    log_error("🔥 CALLING FUSION ADJUST 🔥", phase="fusion")

    fusion_weights = controller.fusion_pipeline.adjust(final_proposal)
    log_debug(f"[PROCESS] Fusion weights: {fusion_weights}", phase="fusion")

    # ---------------------------------------------------------
    # 4. Fusion run
    # ---------------------------------------------------------
    log_error("🔥 CALLING FUSION RUN 🔥", phase="fusion")

    final_text = controller.fusion_pipeline.run(
        fusion_weights=fusion_weights,
        ranked_proposals=ranked,
        controller=controller,
    )

    log_debug(f"[PROCESS] Final text before rewrite: {final_text}", phase="fusion")

    print("FINAL PROPOSAL RAW:", final_proposal)
    # Store the fused output as the final proposal
    controller.last_final_proposal = {
        "actor": "FusionEngine",
        "content": final_text,
        "metadata": {
            "source": "max_hybrid_fusion",
            "fusion_weights": fusion_weights,
            "jury_proposal": final_proposal,
        },
    }
    # ---------------------------------------------------------
    # 5. Meta‑Persona rewrite
    # ---------------------------------------------------------
    log_error("🔥 CALLING META‑PERSONA REWRITE 🔥", phase="meta")

    print("REWRITE FUNCTION:", controller.meta_rewrite_llm)
    print("REWRITE FUNCTION MODULE:", controller.meta_rewrite_llm.__module__)

    rewritten = controller.meta_rewrite_llm(
        core_text=final_text,
        emotion_label=dominant_emotion,
    )

    log_debug(f"[PROCESS] Rewritten output: {rewritten}", phase="meta")
    controller.context.add_assistant_message(rewritten)
    # ---------------------------------------------------------
    # 6. Emotional arc recording
    # ---------------------------------------------------------
    controller.arc_pipeline.record(
        emotional_state=controller.emotional_state,
        dominant_emotion=dominant_emotion,
        fusion_weights=fusion_weights,
    )

    # ---------------------------------------------------------
    # 7. Turn logging
    # ---------------------------------------------------------
    controller.turn_logger.append({
        "message": final_text,
        "emotion": controller.emotional_state,
        "proposals": ranked,
    })

    return rewritten