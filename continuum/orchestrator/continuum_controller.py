# continuum/orchestrator/continuum_controller.py
# Clean, modular ContinuumController orchestrator (Router + v2 routing, DB-driven actors)

import time
from typing import Optional, Dict, Any
import re

from sqlalchemy import text

from continuum.core.logger import log_debug, log_error, log_info

# Modular initialization chunks
from continuum.orchestrator.controller.controller_init import initialize_controller_state
from continuum.orchestrator.controller.controller_actors import initialize_actors_and_senate
from continuum.orchestrator.controller.controller_pipelines import initialize_pipelines
from continuum.orchestrator.controller.controller_process import process_message as _process_message
from continuum.orchestrator.deliberation_engine import DeliberationEngine

from continuum.aira.meta_rewrite import emotional_rewrite

# DB-backed registry (telemetry / nodes)
from continuum.db.registry import ModelRegistry

# LLM client
from continuum.llm.llm_client import LLMClient

# Legacy UI compatibility layer
from continuum.orchestrator.controller_legacy import LegacyUIFields

# New routing spine (DB-driven)
from continuum.orchestrator.router.model_selector_v2 import (
    ModelSelectorV2,
    RoutingDecision,
)
from continuum.orchestrator.router.node_discovery import discover_live_models

# Phase‑5 Telemetry
from continuum.telemetry.telemetry_config import TelemetryConfigLoader
from continuum.telemetry.node_health_store import NodeHealthStore
from continuum.telemetry.heartbeat_manager import HeartbeatManager

# Phase-5 D1-D6
from continuum.emotion.state import EmotionalState
from continuum.emotion.timeline import EmotionalArcTimeline
from continuum.emotion.transition import EmotionalTransitionEngine
from continuum.emotion.memory import EmotionalMemoryEngine
from continuum.emotion.modulation import OutputModulationEngine

from continuum.db.models.cognitive_trace import CognitiveTrace
from continuum.orchestrator.controller.intent_classifier import build_intent_prompt, INTENT_LABELS


class ContinuumController(LegacyUIFields):
    """
    The Continuum orchestrator.

    Clean, modular, and composed of small focused modules:
      - controller_init.py
      - controller_actors.py
      - controller_pipelines.py
      - controller_process.py

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
        # 1. Emotional Engine (Phase‑5D)
        # ---------------------------------------------------------
        self.emotional_state = EmotionalState()
        self.emotional_memory = EmotionalMemoryEngine(self.emotional_state)
        self.emotion_timeline = EmotionalArcTimeline()
        self.emotion_transition = EmotionalTransitionEngine(
            self.emotional_state,
            self.emotion_timeline,
        )
        self.emotion_modulation = OutputModulationEngine(self.emotional_state)
        # Alias for rewrite pipeline compatibility
        self.emotion_state = self.emotional_state
        self.emotion_memory = self.emotional_memory
        
        # ---------------------------------------------------------
        # 2. DB, context, memory
        # ---------------------------------------------------------
        initialize_controller_state(self)
        self.memory = self.context.memory

        # ---------------------------------------------------------
        # 3. Rewrite config
        # ---------------------------------------------------------
        self._load_rewrite_config()

        # ---------------------------------------------------------
        # 4. Model registry + discovery
        # ---------------------------------------------------------
        self.registry = ModelRegistry(self.db)

        try:
            discover_live_models()
        except Exception as e:
            log_error(f"[Router] Failed to discover live models: {e}", phase="router")

        # ---------------------------------------------------------
        # 5. Actor defaults + fallbacks
        # ---------------------------------------------------------
        self.actor_defaults, self.actor_fallbacks = self._load_actor_defaults_from_db()

        # ---------------------------------------------------------
        # 6. Model selector + router interface
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
        # 7. LLM client (must exist BEFORE warm‑up)
        # ---------------------------------------------------------
        self.llm_client = LLMClient()

        # ---------------------------------------------------------
        # 8. Intent classifier config (must exist BEFORE warm‑up)
        # ---------------------------------------------------------
        self.intent_classifier_model = "qwen2.5:0.5b"
        self.intent_classifier_endpoint = "http://localhost:11434/api/generate"

        # ---------------------------------------------------------
        # 9. Load actors + Senate + Jury
        # ---------------------------------------------------------
        self.actor_settings = self._load_actor_settings_from_db()
        initialize_actors_and_senate(self)
        self.deliberation_engine = DeliberationEngine(self.senate, self.jury)

        # ---------------------------------------------------------
        # 10. Pipelines (emotion, fusion, meta)
        # ---------------------------------------------------------
        initialize_pipelines(self)

        # ---------------------------------------------------------
        # 11. System‑level defaults (MUST be before warm‑up)
        # ---------------------------------------------------------
        self.temperature = 0.7
        self.max_tokens = 512
        self.system_prompt = "You are Continuum."
        self.voiceprint = {"style": "neutral"}
        self.max_rewrite_depth = 3

        # ---------------------------------------------------------
        # 12. Warm‑up (AFTER actors + classifier + voiceprint exist)
        # ---------------------------------------------------------
        try:
            # Warm up intent classifier
            self.classify_intent("warmup")

            # Warm up Aira_Lite model
            self.llm_client.warm_model("qwen2.5:0.5b", self.intent_classifier_endpoint)

            # Warm up Greeter model
            greeter = self.actors.get("Greeter")
            if greeter:
                greeter.propose(
                    controller=self,
                    message="warmup",
                    context=self.context,
                    emotional_state=self.emotional_state,
                    emotional_memory=self.emotional_memory,
                    memory=self.memory,
                    voiceprint=self.voiceprint,
                    metadata={},
                    telemetry=None,
                )
        except Exception as e:
            log_error(f"[Warmup] Non‑fatal warmup error: {e}", phase="controller")

        # ---------------------------------------------------------
        # 13. Telemetry + routing debug
        # ---------------------------------------------------------
        self._init_telemetry()
        self.last_routing_decision = None

        # ---------------------------------------------------------
        # 14. Turn log + rewrite pipeline
        # ---------------------------------------------------------
        self.turn_logger = []
        self.meta_rewrite_llm = lambda **kwargs: emotional_rewrite(self, **kwargs)

        log_info("ContinuumController initialized (DB-driven routing + Telemetry)", phase="controller")
        log_error("🔥 CONTROLLER INITIALIZATION COMPLETE 🔥", phase="controller")


    def old_worn_out__init__(self):
        log_error("🔥 CONTROLLER.__init__() START 🔥", phase="controller")

        from continuum.core.logger import logger as continuum_logger
        self.logger = continuum_logger

        # ---------------------------------------------------------
        # 0. Legacy UI fields
        # ---------------------------------------------------------
        self._init_legacy_fields()

        # ---------------------------------------------------------
        # Emotional Engine (Phase‑5D)
        # ---------------------------------------------------------
        self.emotion_state = EmotionalState()
        self.emotion_timeline = EmotionalArcTimeline()
        self.emotion_memory = EmotionalMemoryEngine(self.emotion_state)
        self.emotion_transition = EmotionalTransitionEngine(
            self.emotion_state,
            self.emotion_timeline,
        )
        self.emotion_modulation = OutputModulationEngine(self.emotion_state)

        # ---------------------------------------------------------
        # 1. Load DB, emotional engine, context
        # ---------------------------------------------------------
        initialize_controller_state(self)   # sets self.db, self.context, etc.
        self.memory = self.context.memory

        # ---------------------------------------------------------
        # 2. Load rewrite model from DB (rewrite_config)
        # ---------------------------------------------------------
        self._load_rewrite_config()

        # ---------------------------------------------------------
        # 3. Load DB-backed ModelRegistry (for telemetry / nodes)
        # ---------------------------------------------------------
        self.registry = ModelRegistry(self.db)

        # ---------------------------------------------------------
        # 4. Discover live models (for DB population / telemetry)
        # ---------------------------------------------------------
        try:
            live_models = discover_live_models()
            # At this point, your discovery pipeline should already
            # be populating `models`, `nodes`, and `model_nodes`.
            # If you ever want to enforce that here, you can add a
            # persist_discovery_results(self.db, live_models) call.
        except Exception as e:
            log_error(f"[Router] Failed to discover live models: {e}", phase="router")
            live_models = []

        # ---------------------------------------------------------
        # 5. Load actor defaults / fallbacks from DB (no hardcoding)
        # ---------------------------------------------------------
        self.actor_defaults, self.actor_fallbacks = self._load_actor_defaults_from_db()

        # ---------------------------------------------------------
        # 6. DB-driven, node-aware model selector
        # ---------------------------------------------------------
        self.model_selector = ModelSelectorV2(
            db=self.db,
            actor_defaults=self.actor_defaults,
            actor_fallbacks=self.actor_fallbacks,
            min_health_threshold=0.0,
            logger=self.logger.info,
        )

        # Simple wrapper: router-like interface that produces the structure
        # expected by BaseLLMActor (model_selection + node_selection).
        self.router = self

        # LLM client
        self.llm_client = LLMClient()

        # After: self.llm_client = LLMClient()
        # After: initialize_actors_and_senate(self)

        try:
            # Warm up intent classifier model
            self.classify_intent("warmup")

            # Warm up Greeter’s model once via a tiny call
            greeter = self.actors.get("Greeter")
            if greeter:
                greeter.propose(
                    controller=self,
                    message="warmup",
                    context=self.context,
                    emotional_state=self.emotion_state,
                    emotional_memory=self.emotion_memory,
                    memory=self.memory,
                    voiceprint=self.voiceprint,
                    metadata={},
                    telemetry=None,
                )
        except Exception as e:
            log_error(f"[Warmup] Non‑fatal warmup error: {e}", phase="controller")


        # ---------------------------------------------------------
        # 7. Load actors, Senate, Jury (with DB-driven preferences)
        # ---------------------------------------------------------
        self.actor_settings = self._load_actor_settings_from_db()
        initialize_actors_and_senate(self)
        self.deliberation_engine = DeliberationEngine(self.senate, self.jury)

        # ---------------------------------------------------------
        # 8. Load pipelines (emotion, fusion, meta, etc.)
        # ---------------------------------------------------------
        initialize_pipelines(self)

        # Fusion debug mode
        self.debug_fusion = True

        # Simple in-memory turn log (UI / debugging)
        self.turn_logger = []

        # Attach emotional rewrite pipeline (Phase‑5D)
        self.meta_rewrite_llm = lambda **kwargs: emotional_rewrite(self, **kwargs)

        # ---------------------------------------------------------
        # 9. Phase‑4.5: generation defaults (system-level)
        # ---------------------------------------------------------
        # These can be moved into system_settings later if you want.
        self.temperature = 0.7
        self.max_tokens = 512
        self.system_prompt = "You are Continuum."
        self.voiceprint = {"style": "neutral"}
        self.max_rewrite_depth = 3

        # Routing debug / inspection
        self.last_routing_decision = None

        # ---------------------------------------------------------
        # 10. Phase‑5 Telemetry Integration
        # ---------------------------------------------------------
        self._init_telemetry()

        # ---------------------------------------------------------
        # 11. Dedicated intent classifier config
        # ---------------------------------------------------------
        # Classifier runs on localhost (same as 'Gamer') for portability.
        self.intent_classifier_model = "qwen2.5:0.5b"
        self.intent_classifier_endpoint = "http://localhost:11434/api/generate"

        log_info("ContinuumController initialized (DB-driven routing + Telemetry)", phase="controller")
        log_error("🔥 CONTROLLER INITIALIZATION COMPLETE 🔥", phase="controller")

    # ============================================================
    # DB helpers
    # ============================================================

    def _load_rewrite_config(self):
        try:
            row = self.db.execute(
                text("SELECT pinned_model FROM rewrite_config LIMIT 1")
            ).fetchone()

            if row and row[0]:
                self.rewrite_model = row[0]
            else:
                # Safe fallback if DB has no rewrite_config yet
                self.rewrite_model = "qwen2.5:0.5b"
        except Exception as e:
            log_error(f"[REWRITE CONFIG] Failed to load rewrite model: {e}")
            self.rewrite_model = "qwen2.5:0.5b"

    def _load_actor_defaults_from_db(self):
        """
        Build actor_defaults and actor_fallbacks from the `actors` table.

        actors:
          - name
          - default_model
          - fallback_model
        """
        actor_defaults = {}
        actor_fallbacks = {}

        try:
            rows = self.db.execute(
                text(
                    """
                    SELECT name, default_model, fallback_model
                    FROM actors
                    """
                )
            ).mappings().all()

            for r in rows:
                name = r["name"]
                default_model = r["default_model"]
                fallback_model = r["fallback_model"]

                # Here we treat default_model as a "class key" or a concrete model.
                # If you want to use model classes (e.g., "general-medium"),
                # store those strings in default_model and let MODEL_CLASSES expand them.
                if default_model:
                    actor_defaults[name] = default_model
                if fallback_model:
                    actor_fallbacks[name] = fallback_model

            log_info(f"[Actors] Loaded {len(actor_defaults)} actor defaults from DB", phase="controller")

        except Exception as e:
            log_error(f"[Actors] Failed to load actor defaults from DB: {e}", phase="controller")

        return actor_defaults, actor_fallbacks

    def _load_actor_settings_from_db(self):
        """
        Build per-actor model preferences for the Senate from DB.

        Uses:
          - actor_model_preferences (actor_name, model_name, preference_weight)
          - actors (for existence / enabled actors)
        """
        settings = {}

        try:
            # Load all actors
            actor_rows = self.db.execute(
                text("SELECT name FROM actors")
            ).mappings().all()
            actor_names = [r["name"] for r in actor_rows]

            # Load preferences
            pref_rows = self.db.execute(
                text(
                    """
                    SELECT actor_name, model_name, preference_weight
                    FROM actor_model_preferences
                    """
                )
            ).mappings().all()

            # Group by actor
            prefs_by_actor: Dict[str, list] = {}
            for r in pref_rows:
                actor = r["actor_name"]
                model = r["model_name"]
                weight = r["preference_weight"]
                prefs_by_actor.setdefault(actor, []).append((model, weight))

            # Build actor_settings structure expected by Senate
            for actor in actor_names:
                prefs = prefs_by_actor.get(actor, [])
                preferred_models = [m for (m, w) in sorted(prefs, key=lambda x: -x[1])] if prefs else []

                settings[actor] = {
                    "preferred_models": preferred_models,
                    "enabled": True,
                    "weight": 1.0,
                }

            log_info(f"[Actors] Loaded actor_settings for {len(settings)} actors from DB", phase="controller")

        except Exception as e:
            log_error(f"[Actors] Failed to load actor_settings from DB: {e}", phase="controller")
            settings = {}

        return settings

    def _init_telemetry(self):
        try:
            telemetry_config = TelemetryConfigLoader(self.db).load()
            self.node_health_store = NodeHealthStore(lambda: self.db)
            self.heartbeat = HeartbeatManager(
                config=telemetry_config,
                node_store=self.registry,
                node_health_store=self.node_health_store,
                db_session_factory=lambda: self.db,
                logger=self.logger.info,
            )
            print("🔥🔥🔥🔥🔥🔥LOADING HeartbeatManager FROM:🔥🔥🔥🔥🔥🔥", __file__)
            self.heartbeat.on_system_start()
            log_info("[Telemetry] HeartbeatManager started (warmup active)", phase="telemetry")

        except Exception as e:
            log_error(f"[Telemetry] Failed to initialize heartbeat: {e}", phase="telemetry")
            self.heartbeat = None

    # ============================================================
    # Intent Classification (dedicated, non-recursive, lightweight)
    # ============================================================
    def classify_intent(self, user_message: str) -> str:
        """
        Fast, cached intent classification.

        - Uses tiny local model
        - Avoids recursion
        - Avoids double calls per turn
        - Uses warm-up cache in LLMClient
        """

        # ---------------------------------------------------------
        # 0. Per-turn cache (prevents double LLM calls)
        # ---------------------------------------------------------
        if hasattr(self, "_last_intent_query") and self._last_intent_query == user_message:
            return self._last_intent_result

        print("INTENT DEBUG: entering classify_intent")

        prompt = build_intent_prompt(user_message)
        print("INTENT DEBUG: built prompt:\n", prompt)

        try:
            response = self.llm_client.generate(
                prompt=prompt,
                model=self.intent_classifier_model,
                temperature=0.0,
                max_tokens=8,
                endpoint=self.intent_classifier_endpoint,
            )
        except Exception as e:
            print("LLM ERROR (intent classifier):", e)
            return "analysis"

        raw_text = self._extract_intent_text(response)
        print("INTENT DEBUG: raw_text:", repr(raw_text))

        intent = self._normalize_intent_label(raw_text)
        print("INTENT DEBUG: normalized intent:", intent)

        if intent not in INTENT_LABELS:
            print(
                f"INTENT WARNING: model returned unknown label '{intent}', "
                "falling back to 'analysis'"
            )
            intent = "analysis"

        # ---------------------------------------------------------
        # Cache result for this turn
        # ---------------------------------------------------------
        self._last_intent_query = user_message
        self._last_intent_result = intent

        return intent


    def _extract_intent_text(self, response) -> str:
        """
        Extract plain text from LLMClient.generate() response.
        """
        if isinstance(response, str):
            return response

        if hasattr(response, "text"):
            return response.text

        if isinstance(response, dict):
            if "text" in response:
                return response["text"]
            if "content" in response:
                return response["content"]

        return str(response)

    def _normalize_intent_label(self, raw_text: str) -> str:
        """
        Take the raw model output and extract a single valid label.
        """
        if not raw_text:
            return "analysis"

        text = raw_text.strip().lower()
        print("INTENT DEBUG: normalized raw text:", repr(text))

        if text in INTENT_LABELS:
            return text

        for label in INTENT_LABELS:
            pattern = r"\b" + re.escape(label) + r"\b"
            if re.search(pattern, text):
                return label

        return "analysis"

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
        required_memory_gb = decision.required_memory_gb

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
        if self.heartbeat:
            self.heartbeat.on_user_prompt()

        intent_name = self.classify_intent(message)
        log_error(f"[INTENT] Classified as: {intent_name}", phase="controller")

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
        if self.heartbeat:
            self.heartbeat.stop()
        log_info("[Controller] Shutdown complete", phase="controller")