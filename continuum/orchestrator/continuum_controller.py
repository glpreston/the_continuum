# continuum/orchestrator/continuum_controller.py
# Clean, modular ContinuumController orchestrator (Router + v2 routing)

from sqlalchemy import text

from continuum.core.logger import log_info, log_error

# Modular initialization chunks
from continuum.orchestrator.controller.controller_init import initialize_controller_state
from continuum.orchestrator.controller.controller_actors import initialize_actors_and_senate
from continuum.orchestrator.controller.controller_pipelines import initialize_pipelines
from continuum.orchestrator.controller.controller_process import process_message as _process_message
from continuum.orchestrator.deliberation_engine import DeliberationEngine

from continuum.aira.meta_rewrite import meta_rewrite_llm as aira_meta_rewrite_llm

# NEW DB-backed registry
from continuum.db.registry import ModelRegistry

# LLM client
from continuum.llm.llm_client import LLMClient

# Legacy UI compatibility layer
from continuum.orchestrator.controller_legacy import LegacyUIFields

# New routing spine
from continuum.orchestrator.router.router import Router
from continuum.orchestrator.router.intent_classifier_contract import (
    IntentClassifierContract,
    IntentResult,
)


class BasicIntentClassifier(IntentClassifierContract):
    """
    Temporary/basic intent classifier implementation.

    You can replace this with:
    - an LLM-based classifier
    - a rules/embedding-based classifier
    - or a TS-bridge-backed classifier if you really want

    Contract: classify(text) -> IntentResult
    """

    def classify(self, text: str) -> IntentResult:
        # TODO: replace with real classifier logic
        # For now, treat everything as a generic "conversation" intent.
        return IntentResult(
            intent="conversation",
            confidence=0.75,
            matched_alias=None,
            raw_text=text,
        )


class ContinuumController(LegacyUIFields):
    """
    The Continuum orchestrator.

    Clean, modular, and composed of small focused modules:
      - controller_init.py
      - controller_actors.py
      - controller_pipelines.py
      - controller_process.py

    Now uses the new routing spine:
      user_text → Router (Intent + ModelSelectorV2 + NodeSelectorV2)
    """

    def __init__(self):
        print("USING CONTROLLER FILE:", __file__)
        log_error("🔥 CONTROLLER.__init__() START 🔥", phase="controller")
        from continuum.core.logger import logger as continuum_logger
        self.logger = continuum_logger

        # ---------------------------------------------------------
        # 0. Legacy UI fields
        # ---------------------------------------------------------
        self._init_legacy_fields()

        # ---------------------------------------------------------
        # 1. Load DB, emotional engine, context
        # ---------------------------------------------------------
        initialize_controller_state(self)   # sets self.db, self.context, etc.
        self.memory = self.context.memory

        # ---------------------------------------------------------
        # 2. Load rewrite model from DB (rewrite_config)
        # ---------------------------------------------------------
        try:
            row = self.db.execute(
                text("SELECT pinned_model FROM rewrite_config LIMIT 1")
            ).fetchone()

            if row and row[0]:
                self.rewrite_model = row[0]
            else:
                self.rewrite_model = "gemma3:4b"
        except Exception as e:
            log_error(f"[REWRITE CONFIG] Failed to load rewrite model: {e}")
            self.rewrite_model = "llama3.2:latest"

        # ---------------------------------------------------------
        # 3. Load NEW DB-backed ModelRegistry
        # ---------------------------------------------------------
        self.registry = ModelRegistry(self.db)

        # ---------------------------------------------------------
        # 4. New routing spine (Router + basic IntentClassifier)
        # ---------------------------------------------------------
        self.intent_classifier = BasicIntentClassifier()
        self.router = Router(
            intent_classifier=self.intent_classifier,
            db_conn=self.db,
            logger_instance=self.logger,
        )
        # LLM client
        self.llm_client = LLMClient()

        # ---------------------------------------------------------
        # 5. Load actors, Senate, Jury
        # ---------------------------------------------------------
        initialize_actors_and_senate(self)
        # Attach deliberation engine (Senate → Jury pipeline)
        self.deliberation_engine = DeliberationEngine(self.senate, self.jury)
        
        # ---------------------------------------------------------
        # 6. Load pipelines (emotion, fusion, meta, etc.)
        # ---------------------------------------------------------
        initialize_pipelines(self)

        # Fusion debug mode
        self.debug_fusion = True

        # Simple in-memory turn log (UI / debugging)
        self.turn_logger = []

        # Attach rewrite hook (Meta-Persona)
        # Explicitly bind to Aira’s rewrite function
        self.meta_rewrite_llm = lambda **kwargs: aira_meta_rewrite_llm(self, **kwargs)

        # ---------------------------------------------------------
        # 7. Phase‑4.5: generation defaults
        # ---------------------------------------------------------
        self.temperature = 0.7
        self.max_tokens = 512
        self.system_prompt = "You are Continuum."
        self.voiceprint = {"style": "neutral"}
        self.max_rewrite_depth = 3

        # Routing debug / inspection
        self.last_routing_decision = None

        log_info("ContinuumController initialized (Router + v2 routing, DB‑backed)", phase="controller")
        log_error("🔥 CONTROLLER INITIALIZATION COMPLETE 🔥", phase="controller")

    # ---------------------------------------------------------
    # Main message pipeline (Router-first, then modular pipeline)
    # ---------------------------------------------------------
    def process_message(self, message: str) -> str:
        """
        Main entry point for handling a user message.

        Flow:
          1. Route via Router (intent + model + node)
          2. Store routing decision on self for downstream use
          3. Run the modular process_message pipeline
        """
        # 1. Router: decide intent, model, node
        routing_decision = self.router.route(
            user_text=message,
            actor_name=None,  # you can pass a specific actor name if desired
            extra_context={},
        )
        self.last_routing_decision = routing_decision

        log_info(
            f"[Controller] Routing decision: {routing_decision}",
            phase="controller",
        )

        # TODO: In a next pass, we can thread routing_decision directly
        # into the pipelines and actors. For now, we expose it via
        # self.last_routing_decision so controller_process / pipelines
        # can start consuming it incrementally.

        # 2. Run the existing modular pipeline
        return _process_message(self, message)