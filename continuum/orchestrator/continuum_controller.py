# continuum/orchestrator/continuum_controller.py

import uuid
from typing import Any, List

from ..core.context import ContinuumContext
from .senate import Senate
from .jury import Jury
from continuum.tools.tool_registry import ToolRegistry
from continuum.persona.meta_persona import MetaPersona

# NEW: Import the four Senate actors
from continuum.actors.senate_architect import SenateArchitect
from continuum.actors.senate_storyweaver import SenateStoryweaver
from continuum.actors.senate_analyst import SenateAnalyst
from continuum.actors.senate_synthesizer import SenateSynthesizer


class ContinuumController:
    """
    The orchestrator of The Continuum.
    It coordinates:
      - context management
      - Senate deliberation
      - Jury adjudication
      - final actor response
    """

    def __init__(self):

        # ---------------------------------------------------------
        # Instantiate the four Senate actors (J12 + J13)
        # ---------------------------------------------------------
        actors = [
            SenateArchitect(),
            SenateStoryweaver(),
            SenateAnalyst(),
            SenateSynthesizer(),
        ]

        # ---------------------------------------------------------
        # Existing initialization logic (unchanged)
        # ---------------------------------------------------------
        self.context = ContinuumContext(conversation_id=str(uuid.uuid4()))
        self.senate = Senate(actors)
        self.jury = Jury()
        self.actors = {actor.name: actor for actor in actors}

        # Tool registry
        self.tool_registry = ToolRegistry()

        # J5: Persona settings MUST come BEFORE meta_persona
        self.persona_settings = {
            "voice": "Warm, precise, collaborative",
            "show_actor_name": False,
            "show_meta_persona": False,
        }

        # Meta persona
        self.meta_persona = MetaPersona(
            name="The Continuum",
            voice=self.persona_settings["voice"],
            traits={
                "architect": "Thinks in systems",
                "storyweaver": "Uses metaphor to make complexity intuitive",
                "deliberative": "Surfaces tradeoffs gracefully",
            },
        )

        # J2: Trace storage
        self.last_ranked_proposals = []
        self.last_final_proposal = None

        # J4: Tool logs
        self.tool_logs = []

        # J7: Actor settings
        self.actor_settings = {
            actor.name: {
                "enabled": True,
                "weight": 1.0,
            }
            for actor in actors
        }

        # J8: Theme settings
        self.theme_settings = {
            "mode": "Light",
            "accent_color": "blue",
            "font_size": "medium",
            "density": "comfortable",
        }

    # ---------------------------------------------------------
    # MAIN ENTRYPOINT
    # ---------------------------------------------------------
    def process_message(self, message: str) -> str:
        """
        Full Continuum pipeline:
        1. Update context
        2. Senate gathers and ranks proposals
        3. Jury selects the best proposal
        4. Winning actor generates final response
        """

        # 1. Update context
        self.context.add_user_message(message)

        # 2. Senate deliberation
        ranked_proposals = self.senate.deliberate(self.context, message, self)
        self.last_ranked_proposals = ranked_proposals

        # 3. Jury adjudication
        final_proposal = self.jury.adjudicate(ranked_proposals)
        self.last_final_proposal = final_proposal

        # 4. Ask the winning actor to generate the final response
        actor_name = final_proposal.get("actor")
        actor = self.actors.get(actor_name)

        self.meta_persona.voice = self.persona_settings["voice"]
        self.context.debug_flags["show_meta_persona"] = self.persona_settings["show_meta_persona"]

        if not actor:
            return "The Continuum encountered an error: unknown actor."

        # Generate the actor's raw output
        final_text = actor.respond(self.context, final_proposal)

        # 5. Save assistant response to context
        self.context.add_assistant_message(final_text)

        # 6. Pass through meta-persona
        return self.meta_persona.render(final_text, self.context)