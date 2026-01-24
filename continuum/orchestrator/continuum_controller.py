# continuum/orchestrator/continuum_controller.py
# Clean, modular ContinuumController orchestrator

from continuum.core.logger import log_info, log_error

# Modular initialization chunks
from continuum.orchestrator.controller.controller_init import initialize_controller_state
from continuum.orchestrator.controller.controller_actors import initialize_actors_and_senate
from continuum.orchestrator.controller.controller_pipelines import initialize_pipelines
from continuum.orchestrator.controller.controller_rewrite import meta_rewrite_llm
from continuum.orchestrator.controller.controller_process import process_message as _process_message

# NEW Phase‑4 model selector
from continuum.orchestrator.model_selector import ModelSelector

# Legacy TypeScript selector (optional)
from continuum.ts_bridge.selector_client import select_model as ts_select_model

# Legacy UI compatibility layer
from continuum.orchestrator.controller_legacy import LegacyUIFields


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
        # Legacy UI compatibility fields
        # ---------------------------------------------------------
        self._init_legacy_fields()

        # ---------------------------------------------------------
        # Core initialization
        # ---------------------------------------------------------

        # 1. Load config, registry, emotional engine, context
        initialize_controller_state(self)

        # 2. Load actors, Senate, Jury
        initialize_actors_and_senate(self)

        # 3. Load emotion, fusion, meta‑persona pipelines
        initialize_pipelines(self)

        # Simple in‑memory turn log (UI / debugging)
        self.turn_logger = []

        # 4. Attach rewrite hook (Meta‑Persona)
        self.meta_rewrite_llm = lambda **kwargs: meta_rewrite_llm(self, **kwargs)

        # ---------------------------------------------------------
        # Phase‑4 model + generation defaults
        # ---------------------------------------------------------
        self.temperature = 0.7
        self.max_tokens = 512
        self.system_prompt = "You are Continuum."
        self.voiceprint = {"style": "neutral"}

        # Simple in‑memory turn log (UI / debugging)
        self.turn_logger = []

        # 4. Attach rewrite hook (Meta‑Persona)
        self.meta_rewrite_llm = lambda **kwargs: meta_rewrite_llm(self, **kwargs)

        # ---------------------------------------------------------
        # 5. Phase‑4 Python Model Selector
        # ---------------------------------------------------------
        self.model_selector = ModelSelector(self)

        # ---------------------------------------------------------
        # 6. Legacy TypeScript selector (optional)
        # ---------------------------------------------------------
        # Keep it available for backwards compatibility
        self.ts_select_model = ts_select_model

        log_info("ContinuumController initialized (modular, DB‑backed)", phase="controller")
        log_error("🔥 CONTROLLER INITIALIZATION COMPLETE 🔥", phase="controller")

    # ---------------------------------------------------------
    # Main message pipeline (now with adaptive model selection)
    # ---------------------------------------------------------
    def process_message(self, message: str) -> str:
        """
        Adaptive wrapper around the modular process_message pipeline.
        The pipeline can call:
            - self.model_selector.select_model(...)  (Phase‑4)
            - self.ts_select_model(...)              (legacy TS)
        """
        return _process_message(self, message)