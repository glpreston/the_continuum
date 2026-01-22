# continuum/orchestrator/continuum_controller.py
# Clean, modular ContinuumController orchestrator

from continuum.core.logger import log_info, log_error

# Modular initialization chunks
from continuum.orchestrator.controller.controller_init import initialize_controller_state
from continuum.orchestrator.controller.controller_actors import initialize_actors_and_senate
from continuum.orchestrator.controller.controller_pipelines import initialize_pipelines
from continuum.orchestrator.controller.controller_rewrite import meta_rewrite_llm
from continuum.orchestrator.controller.controller_process import process_message

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

        log_info("ContinuumController initialized (modular, DB‑backed)", phase="controller")
        log_error("🔥 CONTROLLER INITIALIZATION COMPLETE 🔥", phase="controller")

    # ---------------------------------------------------------
    # Main message pipeline
    # ---------------------------------------------------------
    def process_message(self, message: str) -> str:
        return process_message(self, message)