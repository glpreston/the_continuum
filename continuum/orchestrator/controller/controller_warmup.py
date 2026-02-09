# continuum/orchestrator/controller/controller_warmup.py

from continuum.core.logger import log_error
from continuum.orchestrator.controller.controller_intent import classify_intent


def initialize_warmup(controller):
    """
    Phase‑5 warmup sequence:
    - Intent classifier warmup
    - LLM model warmup
    - Greeter warmup
    """

    try:
        # Warm up intent classifier
        classify_intent(controller, "warmup")


        # Warm up Aira_Lite model
        controller.llm_client.warm_model(
            controller.intent_classifier_model,
            controller.intent_classifier_endpoint,
        )

        # Warm up Greeter model
        greeter = controller.actors.get("Greeter")
        if greeter:
            greeter.propose(
                controller=controller,
                message="warmup",
                context=controller.context,
                emotional_state=controller.emotional_state,
                emotional_memory=controller.emotional_memory,
                memory=controller.memory,
                voiceprint=controller.voiceprint,
                metadata={},
                telemetry=None,
            )

    except Exception as e:
        log_error(f"[Warmup] Non‑fatal warmup error: {e}", phase="controller")