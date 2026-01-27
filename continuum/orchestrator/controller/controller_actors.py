# continuum/orchestrator/controller/controller_actors.py

import os
from continuum.core.logger import log_debug

from continuum.actors.architect import Architect
from continuum.actors.storyweaver import Storyweaver
from continuum.actors.analyst import Analyst
from continuum.actors.synthesizer import Synthesizer

from continuum.orchestrator.senate import Senate
from continuum.orchestrator.jury import Jury
from continuum.orchestrator.deliberation_engine import DeliberationEngine


def load_prompt(name: str) -> str:
    base = os.path.join(os.path.dirname(__file__), "..", "actors", "prompts")
    path = os.path.abspath(os.path.join(base, name))
    try:
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        return f"[ERROR: could not load prompt {name}: {e}]"


def initialize_actors_and_senate(controller):
    """
    Initializes actors using DB-backed registry.actor_profiles.
    Replaces the old config-based actor loading system.
    """

    controller.actors = {}
    registry = controller.registry

    # Map DB actor names → prompt files + Python classes
    ACTOR_MAP = {
        "Architect": ("architect_prompt.txt", Architect),
        "Storyweaver": ("storyweaver_prompt.txt", Storyweaver),
        "Analyst": ("analyst_prompt.txt", Analyst),
        "Synthesizer": ("synthesizer_prompt.txt", Synthesizer),
    }

    # ---------------------------------------------------------
    # Load actors from DB
    # ---------------------------------------------------------
    for actor_name, profile in registry.actor_profiles.items():

        if actor_name not in ACTOR_MAP:
            raise ValueError(f"Unknown actor in DB: {actor_name}")

        prompt_file, actor_cls = ACTOR_MAP[actor_name]
        system_prompt = load_prompt(prompt_file)

        actor = actor_cls(
            name=actor_name,
            model_name=profile.model_name,
            fallback_model=profile.fallback_model,
            personality=profile.personality,
            system_prompt=system_prompt,
            temperature=profile.temperature_default,
            max_tokens=profile.context_window,
            controller=controller,
        )

        controller.actors[actor_name] = actor

        log_debug(f"[ACTORS] Loaded actor '{actor_name}'", phase="actors")

    # ---------------------------------------------------------
    # Senate
    # ---------------------------------------------------------
    controller.senate = Senate([
        controller.actors["Architect"],
        controller.actors["Storyweaver"],
        controller.actors["Analyst"],
        controller.actors["Synthesizer"],
    ])

    # ---------------------------------------------------------
    # Jury
    # ---------------------------------------------------------
    controller.jury = Jury()

    # ---------------------------------------------------------
    # Deliberation Engine
    # ---------------------------------------------------------
    controller.deliberation_engine = DeliberationEngine(
        senate=controller.senate,
        jury=controller.jury,
    )

    # ---------------------------------------------------------
    # Actor enable/disable settings
    # ---------------------------------------------------------
    controller.actor_settings = {
        "Architect": {"enabled": True},
        "Storyweaver": {"enabled": True},
        "Analyst": {"enabled": True},
        "Synthesizer": {"enabled": True},
    }

    log_debug("[ACTORS] Actor system initialization complete", phase="actors")