# continuum/orchestrator/controller_init.py

import uuid
from continuum.db.sqlalchemy_connection import get_db_session

from continuum.persona.emotional_memory import EmotionalMemory
from continuum.emotion.state_machine import EmotionalState

from continuum.db.registry import ModelRegistry
from continuum.core.context import ContinuumContext
from continuum.core.logger import log_debug, log_error


def initialize_controller_state(controller):
    log_error("🔥 ENTERED controller_init.initialize_controller_state() 🔥", phase="controller")

    # ---------------------------------------------------------
    # 1. Database session
    # ---------------------------------------------------------
    controller.db = get_db_session()

    # ---------------------------------------------------------
    # 2. Emotional engine
    # ---------------------------------------------------------
    controller.emotional_memory = EmotionalMemory()
    controller.emotional_state = EmotionalState()

    # ---------------------------------------------------------
    # 3. Model registry (auto-loads nodes/models from DB)
    # ---------------------------------------------------------
    controller.registry = ModelRegistry(controller.db)

    log_debug("[INIT] Model registry initialized", phase="controller")

    # ---------------------------------------------------------
    # 4. Core context
    # ---------------------------------------------------------
    controller.context = ContinuumContext(conversation_id=str(uuid.uuid4()))
    controller.context.emotional_state = controller.emotional_state
    controller.context.emotional_memory = controller.emotional_memory
    controller.context.debug_flags["show_prompts"] = True

    # ---------------------------------------------------------
    # 5. Meta‑Persona rewrite flags
    # ---------------------------------------------------------
    controller.flags = {"enable_meta_llm": True}

    log_debug("[INIT] Controller initialization complete", phase="controller")