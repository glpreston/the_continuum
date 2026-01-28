# continuum/orchestrator/controller/controller_actors.py
# Phase‑5 clean actor + Senate initialization

import os
from continuum.core.logger import log_debug

# LLM actors
from continuum.actors.architect import Architect
from continuum.actors.analyst import Analyst
from continuum.actors.storyweaver import Storyweaver
from continuum.actors.synthesizer import Synthesizer

# Senate wrappers
from continuum.actors.senate_architect import SenateArchitect
from continuum.actors.senate_analyst import SenateAnalyst
from continuum.actors.senate_storyweaver import SenateStoryweaver
from continuum.actors.senate_synthesizer import SenateSynthesizer
from continuum.orchestrator.senate import Senate


def initialize_actors_and_senate(controller):
    """
    Phase‑5 actor initialization:
      - No model_name or fallback_model
      - Actors are Router‑agnostic
      - Senate wrappers are clean and simple
      - Controller stores actors + Senate in a predictable structure
    """

    log_debug("[ACTORS] Initializing Phase‑5 actors", phase="actors")

    # ---------------------------------------------------------
    # 1. Instantiate LLM actors (Router‑agnostic)
    # ---------------------------------------------------------
    architect = Architect(controller)
    analyst = Analyst(controller)
    storyweaver = Storyweaver(controller)
    synthesizer = Synthesizer(controller)

    controller.actors = {
        "Architect": architect,
        "Analyst": analyst,
        "Storyweaver": storyweaver,
        "Synthesizer": synthesizer,
    }

    log_debug("[ACTORS] LLM actors instantiated", phase="actors")

    # ---------------------------------------------------------
    # 2. Senate wrappers
    # ---------------------------------------------------------
    senate_architect = SenateArchitect(architect)
    senate_analyst = SenateAnalyst(analyst)
    senate_storyweaver = SenateStoryweaver(storyweaver)
    senate_synthesizer = SenateSynthesizer(synthesizer)

    controller.senate_actors = {
        "Architect": senate_architect,
        "Analyst": senate_analyst,
        "Storyweaver": senate_storyweaver,
        "Synthesizer": senate_synthesizer,
    }

    log_debug("[ACTORS] Senate wrappers instantiated", phase="actors")

    # ---------------------------------------------------------
    # 3. Senate list (ordered)
    # ---------------------------------------------------------
    
    senate_members = [
        senate_architect,
        senate_analyst,
        senate_storyweaver,
        senate_synthesizer,
    ]

    controller.senate_members = senate_members
    controller.senate = Senate(senate_members)

    log_debug("[ACTORS] Senate list created", phase="actors")

    # ---------------------------------------------------------
    # 3.5 Jury initialization (Phase‑5)
    # ---------------------------------------------------------
    from continuum.orchestrator.jury import Jury
    controller.jury = Jury()


    # ---------------------------------------------------------
    # 3.5 Jury initialization (Phase‑5)
    # ---------------------------------------------------------
    from continuum.orchestrator.jury import Jury
    controller.jury = Jury()


    # ---------------------------------------------------------
    # 4. Actor enable/disable settings
    # ---------------------------------------------------------
    controller.actor_settings = {
        "Architect": {"enabled": True},
        "Analyst": {"enabled": True},
        "Storyweaver": {"enabled": True},
        "Synthesizer": {"enabled": True},
    }

    log_debug("[ACTORS] Actor settings initialized", phase="actors")

    log_debug("[ACTORS] Phase‑5 actor system initialization complete", phase="actors")