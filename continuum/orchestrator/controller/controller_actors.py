# continuum/orchestrator/controller_actors.py
# Actor + Senate initialization for ContinuumController

from typing import Dict, Any

from continuum.actors.architect import Architect
from continuum.actors.storyweaver import Storyweaver
from continuum.actors.analyst import Analyst
from continuum.actors.synthesizer import Synthesizer

from continuum.actors.senate_architect import SenateArchitect
from continuum.actors.senate_storyweaver import SenateStoryweaver
from continuum.actors.senate_analyst import SenateAnalyst
from continuum.actors.senate_synthesizer import SenateSynthesizer
from continuum.orchestrator.deliberation_engine import DeliberationEngine

from continuum.orchestrator.senate import Senate
from continuum.orchestrator.jury import Jury

from continuum.core.logger import log_debug


def initialize_actors_and_senate(controller):
    """
    Initializes:
      - LLM actors
      - Senate wrappers
      - Senate
      - Jury
      - Actor enable/disable settings
    """

    # ---------------------------------------------------------
    # 1. LLM Actors
    # ---------------------------------------------------------
    controller.actors: Dict[str, Any] = {}

    for actor_name, cfg in controller.actors_config.items():
        model_name = cfg["default_model"]
        fallback_model = cfg["fallback_model"]
        personality = cfg["personality"]

        if actor_name == "Architect":
            actor_cls = Architect
        elif actor_name == "Storyweaver":
            actor_cls = Storyweaver
        elif actor_name == "Analyst":
            actor_cls = Analyst
        elif actor_name == "Synthesizer":
            actor_cls = Synthesizer
        else:
            raise ValueError(f"Unknown actor in DB: {actor_name}")

        llm_actor = actor_cls(
            name=actor_name,
            model_name=model_name,
            fallback_model=fallback_model,
            personality=personality,
            system_prompt="",
            temperature=0.7,
            max_tokens=2048,
            controller=controller,
        )

        controller.actors[actor_name] = llm_actor

    log_debug("[ACTORS] LLM actors initialized", phase="controller")

    # ---------------------------------------------------------
    # 2. Senate Wrappers
    # ---------------------------------------------------------
    controller.senate_actors = {
        "Architect": SenateArchitect(controller.actors["Architect"]),
        "Storyweaver": SenateStoryweaver(controller.actors["Storyweaver"]),
        "Analyst": SenateAnalyst(controller.actors["Analyst"]),
        "Synthesizer": SenateSynthesizer(controller.actors["Synthesizer"]),
    }

    # ---------------------------------------------------------
    # 3. Senate
    # ---------------------------------------------------------
    controller.senate = Senate([
        controller.senate_actors["Architect"],
        controller.senate_actors["Storyweaver"],
        controller.senate_actors["Analyst"],
        controller.senate_actors["Synthesizer"],
    ])

    controller.senate_to_llm_map = {
        "SenateArchitect": "Architect",
        "SenateStoryweaver": "Storyweaver",
        "SenateAnalyst": "Analyst",
        "SenateSynthesizer": "Synthesizer",
    }

    # ---------------------------------------------------------
    # 4. Jury
    # ---------------------------------------------------------
    controller.jury = Jury()

    # ---------------------------------------------------------
    # 4.5 Deliberation Engine
    # ---------------------------------------------------------
    controller.deliberation_engine = DeliberationEngine(
        senate=controller.senate,
        jury=controller.jury,
    )   

    # ---------------------------------------------------------
    # 5. Actor enable/disable settings
    # ---------------------------------------------------------
    controller.actor_settings = {
        "Architect": {"enabled": True},
        "Storyweaver": {"enabled": True},
        "Analyst": {"enabled": True},
        "Synthesizer": {"enabled": True},
    }

    log_debug("[ACTORS] Senate + Jury initialized", phase="controller")