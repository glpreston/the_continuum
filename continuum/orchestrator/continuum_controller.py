# continuum/orchestrator/continuum_controller.py
# Clean, modular ContinuumController orchestrator (Router + v2 routing, DB-driven actors)

from typing import Optional, Dict, Any

from continuum.core.logger import log_debug, log_error, log_info
from continuum.orchestrator.controller.controller_process import is_greeting_message

# Modular initialization chunks
from continuum.orchestrator.controller.controller_init import (
    initialize_controller_state,
    load_rewrite_config,
    load_actor_defaults,
    load_actor_settings,
)
from continuum.orchestrator.controller.controller_actors import (
    initialize_actors_and_senate,
)
from continuum.orchestrator.controller.controller_pipelines import (
    initialize_pipelines,
)
from continuum.orchestrator.controller.controller_process import (
    process_message as _process_message,
)
from continuum.orchestrator.controller.controller_intent import classify_intent
from continuum.orchestrator.controller.controller_telemetry import (
    initialize_telemetry,
)
from continuum.orchestrator.controller.controller_warmup import (
    initialize_warmup,
)
from continuum.orchestrator.controller.controller_rewrite import (
    initialize_legacy_rewrite_wrapper,
)

from continuum.orchestrator.deliberation_engine import DeliberationEngine

# New routing spine (DB-driven)
from continuum.orchestrator.router.model_selector_v2 import (
    ModelSelectorV2,
    RoutingDecision,
)
from continuum.orchestrator.router.node_discovery import discover_live_models

# LLM client
from continuum.llm.llm_client import LLMClient

# Legacy UI compatibility layer
from continuum.orchestrator.controller_legacy import LegacyUIFields


class ContinuumController(LegacyUIFields):
    """
    The Continuum orchestrator.

    Clean, modular, and composed of small focused modules:
      - controller_init.py
      - controller_actors.py
      - controller_pipelines.py
      - controller_process.py
      - controller_intent.py
      - controller_telemetry.py
      - controller_warmup.py
      - controller_rewrite.py

    Uses the Phase‑5 routing spine:
      user_text → ModelSelectorV2 (DB inventory) → node + model

    Actors, defaults, and preferences are DB-driven (no hardcoded model names).
    """

    def __init__(self):
        log_error("🔥 CONTROLLER.__init__() START 🔥", phase="controller")

        # ---------------------------------------------------------
        # 0. Logger + Legacy UI fields
        # ---------------------------------------------------------
        from continuum.core.logger import logger as continuum_logger

        self.logger = continuum_logger
        self._init_legacy_fields()

        # ---------------------------------------------------------
        # 1. Core state (DB, emotion, context, registry, flags)
        # ---------------------------------------------------------
        initialize_controller_state(self)
        self.memory = self.context.memory
        self.last_routing_decision = None

        # ---------------------------------------------------------
        # 2. Rewrite config
        # ---------------------------------------------------------
        load_rewrite_config(self)

        # ---------------------------------------------------------
        # 3. Model discovery (router inventory)
        # ---------------------------------------------------------
        try:
            discover_live_models()
        except Exception as e:
            log_error(f"[Router] Failed to discover live models: {e}", phase="router")

        # ---------------------------------------------------------
        # 4. Actor defaults + fallbacks + settings
        # ---------------------------------------------------------
        load_actor_defaults(self)
        load_actor_settings(self)

        # ---------------------------------------------------------
        # 5. Model selector + router interface
        # ---------------------------------------------------------
        self.model_selector = ModelSelectorV2(
            db=self.db,
            actor_defaults=self.actor_defaults,
            actor_fallbacks=self.actor_fallbacks,
            min_health_threshold=0.0,
            logger=self.logger.info,
        )
        self.router = self

        # ---------------------------------------------------------
        # 6. LLM client (must exist BEFORE warm‑up)
        # ---------------------------------------------------------
        self.llm_client = LLMClient()

        # ---------------------------------------------------------
        # 7. Intent classifier config (must exist BEFORE warm‑up)
        # ---------------------------------------------------------
        self.intent_classifier_model = "qwen2.5:0.5b"
        self.intent_classifier_endpoint = "http://localhost:11434/api/generate"

        # ---------------------------------------------------------
        # 8. Load actors + Senate + Jury
        # ---------------------------------------------------------
        initialize_actors_and_senate(self)
        self.deliberation_engine = DeliberationEngine(self.senate, self.jury)

        # ---------------------------------------------------------
        # 9. Pipelines (emotion, fusion, meta)
        # ---------------------------------------------------------
        initialize_pipelines(self)

        # ---------------------------------------------------------
        # 10. System‑level defaults (MUST be before warm‑up)
        # ---------------------------------------------------------
        self.temperature = 0.7
        self.max_tokens = 512
        self.system_prompt = "You are Continuum."
        self.voiceprint = {"style": "neutral"}
        self.max_rewrite_depth = 3

        # ---------------------------------------------------------
        # 11. Warm‑up (AFTER actors + classifier + voiceprint exist)
        # ---------------------------------------------------------
        initialize_warmup(self)

        # ---------------------------------------------------------
        # 12. Telemetry + routing debug
        # ---------------------------------------------------------
        initialize_telemetry(self)
        self.last_routing_decision = None

        # ---------------------------------------------------------
        # 13. Turn log + legacy rewrite wrapper
        # ---------------------------------------------------------
        self.turn_logger = []
        initialize_legacy_rewrite_wrapper(self)

        log_info(
            "ContinuumController initialized (DB-driven routing + Telemetry)",
            phase="controller",
        )
        log_error("🔥 CONTROLLER INITIALIZATION COMPLETE 🔥", phase="controller")

    # ============================================================
    # Routing logic (DB-driven, using ModelSelectorV2)
    # ============================================================
    def route(
        self,
        user_text: str,
        actor_name: Optional[str] = None,
        extra_context: Optional[Dict[str, Any]] = None,
        intent_name: Optional[str] = None,
    ) -> Dict[str, Any]:
        extra_context = extra_context or {}

        # 1. Intent: use provided intent_name, or default to analysis
        intent_name = intent_name or "analysis"
        actor_name = actor_name or "Architect"

        # 2. Select model via ModelSelectorV2
        decision: Optional[RoutingDecision] = self.model_selector.select_models(
            intent_name=intent_name,
            actor_name=actor_name,
            require_vision=False,
        )

        if not decision:
            raise RuntimeError(
                f"[ContinuumController] No model selected for actor '{actor_name}' "
                f"and intent '{intent_name}'"
            )

        top_model = decision.model
        selected_node_name = decision.node
        required_memory_gb = decision.required_memory_gb  # kept for future use

        # 3. Build node_selection structure with host so actors can use it.
        host = selected_node_name  # for Ollama-style nodes, name == host

        node_selection = {
            "selected_node": {
                "name": selected_node_name,
                "host": host,
            },
            "available_nodes": [],
        }

        # 4. Build routing decision
        routing_decision = {
            "intent": intent_name,
            "intent_confidence": None,
            "matched_alias": None,
            "raw_text": user_text,
            "actor_name": actor_name,
            "model_selection": {
                "selected_model": top_model,
                "selected_node": node_selection["selected_node"],
            },
            "node_selection": node_selection,
            "extra_context": extra_context,
        }

        self.last_routing_decision = routing_decision
        return routing_decision

    # ============================================================
    # Main message pipeline (intent → route → pipeline)
    # ============================================================
    def process_message(self, message: str) -> str:
        if getattr(self, "heartbeat", None):
            self.heartbeat.on_user_prompt()

        intent_name = classify_intent(self, message)
        log_debug(f"[INTENT] Classified as: {intent_name}", phase="controller")

        # Phase‑5 Greeting Override (FINAL routing point)
        if is_greeting_message(message):
            log_debug("[INTENT] Greeting override triggered → intent = 'greeting'", phase="controller")
            intent_name = "greeting"

        # Choose actor based on intent
        actor_name = self.select_actor_for_intent(intent_name)

        routing_decision = self.route(
            user_text=message,
            actor_name=actor_name,
            extra_context={},
            intent_name=intent_name,
        )

        self.last_routing_decision = routing_decision

        log_info(
            f"[Controller] Routing decision: {routing_decision}",
            phase="controller",
        )

        return _process_message(self, message)

    # ============================================================
    # Actor selection based on intent
    # ============================================================
    def select_actor_for_intent(self, intent: str) -> str:
        """
        Map intents to actors.
        This ensures greetings go to Greeter, analysis to Analyst, etc.
        """
        intent = (intent or "").lower()

        # Social / lightweight
        if intent in ("greeting", "chitchat"):
            return "Greeter"

        # Narrative / creative
        if intent == "story":
            return "Storyweaver"

        # Code generation / technical tasks
        if intent == "code":
            return "Synthesizer"

        # Structured reasoning
        if intent == "analysis":
            return "Analyst"

        # Step-by-step instructions
        if intent == "task":
            return "Synthesizer"

        # Big conceptual questions
        if intent == "big_idea":
            return "Architect"

        # Factual questions
        if intent == "fact":
            return "Analyst"

        # Light tasks (recipes, simple info)
        if intent == "light_task":
            return "Greeter"

        # Default fallback
        return "Architect"

    # ============================================================
    # Optional: clean shutdown hook
    # ============================================================
    def shutdown(self):
        if getattr(self, "heartbeat", None):
            self.heartbeat.stop()
        log_info("[Controller] Shutdown complete", phase="controller")