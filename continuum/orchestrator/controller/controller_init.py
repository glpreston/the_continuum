# continuum/orchestrator/controller_init.py
# Initialization module for ContinuumController

import uuid
from typing import Dict, Any

from continuum.db.mysql_connection import MySQLConfigDB
from continuum.config.config_loader import ConfigLoader

from continuum.persona.emotional_memory import EmotionalMemory
from continuum.emotion.state_machine import EmotionalState

from continuum.orchestrator.model_registry import ModelRegistry
from continuum.core.context import ContinuumContext
from continuum.core.logger import log_debug, log_error


def initialize_controller_state(controller):
    """
    Handles all initialization steps for ContinuumController.
    Cleanly separated so the main controller file stays readable.
    """

    log_error("🔥 ENTERED controller_init.initialize_controller_state() 🔥", phase="controller")

    # ---------------------------------------------------------
    # 1. Load configuration from DB
    # ---------------------------------------------------------
    controller.config_db = MySQLConfigDB(
        host="192.168.50.114",
        port=3306,
        user="aira_user",
        password="1241Aira2026!",
        database="aira_config"
    )

    controller.config_loader = ConfigLoader(controller.config_db)
    controller.config = controller.config_loader.load_all()

    controller.nodes = controller.config["nodes"]
    controller.actors_config = controller.config["actors"]
    controller.models_config = controller.config["models"]
    controller.system_settings = controller.config["system_settings"]
    controller.persona_presets = controller.config["persona_presets"]

    log_debug("[INIT] Loaded DB configuration", phase="controller")

    # ---------------------------------------------------------
    # 2. Emotional engine core
    # ---------------------------------------------------------
    controller.emotional_memory = EmotionalMemory()
    controller.emotional_state = EmotionalState()

    # ---------------------------------------------------------
    # 3. Model registry
    # ---------------------------------------------------------
    controller.registry = ModelRegistry()

    for model_name, model_info in controller.models_config.items():
        controller.registry.register_model(
            name=model_name,
            provider=model_info["provider"],
            context_window=model_info["context_window"],
            temperature_default=model_info["temperature_default"],
        )

    # Register + instantiate Meta‑Rewrite model
    controller.registry.register_model(
        name="meta_rewrite",
        provider="openai",
        context_window=4096,
        temperature_default=0.4,
    )
    #controller.registry.instantiate_model("meta_rewrite")

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