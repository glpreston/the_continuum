# continuum/orchestrator/continuum_controller.py
# Clean, modular ContinuumController orchestrator

from continuum.core.logger import log_info, log_error

# Modular initialization chunks
from continuum.orchestrator.controller.controller_init import initialize_controller_state
from continuum.orchestrator.controller.controller_actors import initialize_actors_and_senate
from continuum.orchestrator.controller.controller_pipelines import initialize_pipelines
from continuum.aira.meta_rewrite import meta_rewrite_llm as aira_meta_rewrite_llm
from continuum.orchestrator.controller.controller_process import process_message as _process_message
from continuum.orchestrator.model_selector import ModelSelector
from continuum.orchestrator.node_selector import NodeSelector
from sqlalchemy import text

# NEW DB-backed registry
from continuum.db.registry import ModelRegistry

# Phase‑4 model selector (RESTORED)
from continuum.orchestrator.model_selector import ModelSelector


# LLM client
from continuum.llm.llm_client import LLMClient

# Legacy UI compatibility layer
from continuum.orchestrator.controller_legacy import LegacyUIFields

# Optional legacy TS selector
from continuum.ts_bridge.selector_client import select_model as ts_select_model


class ContinuumController(LegacyUIFields):
    """
    The Continuum orchestrator.
    Clean, modular, and composed of small focused modules:
      - controller_init.py
      - controller_actors.py
      - controller_pipelines.py
      - controller_rewrite.py
      - controller_process.py
    """

    def __init__(self):
        print("USING CONTROLLER FILE:", __file__)
        log_error("🔥 CONTROLLER.__init__() START 🔥", phase="controller")

        # ---------------------------------------------------------
        # 0. Legacy UI fields
        # ---------------------------------------------------------
        self._init_legacy_fields()

        # ---------------------------------------------------------
        # 1. Load DB, emotional engine, context
        # ---------------------------------------------------------
        initialize_controller_state(self)   # sets self.db
        self.memory = self.context.memory
        # ---------------------------------------------------------
        # Load rewrite model from DB (rewrite_config)
        # ---------------------------------------------------------
        try:
            row = self.db.execute(text("SELECT pinned_model FROM rewrite_config LIMIT 1")).fetchone()

            if row and row[0]:
                self.rewrite_model = row[0]
            else:
                self.rewrite_model = "gemma3:4b"
        except Exception as e:
            log_error(f"[REWRITE CONFIG] Failed to load rewrite model: {e}")
            self.rewrite_model = "llama3.2:latest"

        # ---------------------------------------------------------
        # 2. Load NEW DB-backed ModelRegistry
        # ---------------------------------------------------------
        self.registry = ModelRegistry(self.db)

        # ---------------------------------------------------------
        # 3. RESTORE Phase‑4 ModelSelector (required by actors)
        # ---------------------------------------------------------
        self.model_selector = ModelSelector(self)

        self.registry = ModelRegistry(self.db)
        self.model_selector = ModelSelector(self)
        self.node_selector = NodeSelector(self)

        # LLM client
        self.llm_client = LLMClient()

        # ---------------------------------------------------------
        # 4. Load actors, Senate, Jury
        # ---------------------------------------------------------
        initialize_actors_and_senate(self)

        # ---------------------------------------------------------
        # 5. Load pipelines (emotion, fusion, meta, etc.)
        # ---------------------------------------------------------
        initialize_pipelines(self)

        # Fusion debug mode
        self.debug_fusion = True

        # Simple in‑memory turn log (UI / debugging)
        self.turn_logger = []

        # Attach rewrite hook (Meta‑Persona)
      
        # Explicitly bind to Aira’s rewrite function
        self.meta_rewrite_llm = lambda **kwargs: aira_meta_rewrite_llm(self, **kwargs)
        


        # ---------------------------------------------------------
        # 6. Phase‑4.5: generation defaults
        # ---------------------------------------------------------
        self.temperature = 0.7
        self.max_tokens = 512
        self.system_prompt = "You are Continuum."
        self.voiceprint = {"style": "neutral"}
        self.max_rewrite_depth = 3

        # ---------------------------------------------------------
        # 7. Legacy TypeScript selector (optional)
        # ---------------------------------------------------------
        self.ts_select_model = ts_select_model

        log_info("ContinuumController initialized (modular, DB‑backed)", phase="controller")
        log_error("🔥 CONTROLLER INITIALIZATION COMPLETE 🔥", phase="controller")

    # ---------------------------------------------------------
    # Main message pipeline (adaptive model selection)
    # ---------------------------------------------------------
    def process_message(self, message: str) -> str:
        """
        Adaptive wrapper around the modular process_message pipeline.
        The pipeline can call:
            - self.model_selector.select_model(...)
            - self.registry.get_best_node_for_model(...)
            - self.ts_select_model(...) (legacy)
        """
        return _process_message(self, message)