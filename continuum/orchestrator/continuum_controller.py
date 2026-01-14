# continuum/orchestrator/continuum_controller.py

import uuid
from typing import Any, List

from ..core.context import ContinuumContext
from .senate import Senate
from .jury import Jury
from continuum.tools.tool_registry import ToolRegistry
from continuum.persona.meta_persona import MetaPersona

# Senate actors
from continuum.actors.senate_architect import SenateArchitect
from continuum.actors.senate_storyweaver import SenateStoryweaver
from continuum.actors.senate_analyst import SenateAnalyst
from continuum.actors.senate_synthesizer import SenateSynthesizer

# Emotional memory
from continuum.persona.emotional_memory import EmotionalMemory

# Semantic embedding for Jury emotional alignment
from continuum.memory.semantic import embed as get_embedding


class ContinuumController:
    """
    The orchestrator of The Continuum.
    Coordinates:
      - context management
      - Senate deliberation
      - Jury adjudication
      - final actor response
    """

    def __init__(self, *args, **kwargs):

        self.turn_history = []

        # Emotional memory
        self.emotional_memory = EmotionalMemory(max_events=20)

        # Lazy-loaded emotion model (initialized on first use)
        self.emotion_model = None

        # Narrator mode (used by UI / meta layers)
        self.narrator_mode = False

        # Senate actors
        actors = [
            SenateArchitect(),
            SenateStoryweaver(),
            SenateAnalyst(),
            SenateSynthesizer(),
        ]

        # Core components
        self.context = ContinuumContext(conversation_id=str(uuid.uuid4()))
        self.senate = Senate(actors)
        self.jury = Jury()
        self.actors = {actor.name: actor for actor in actors}

        # Wire embedding function into Jury for emotional alignment
        self.jury.embed_fn = get_embedding

        # Tool registry
        self.tool_registry = ToolRegistry()

        # Persona settings
        self.persona_settings = {
            "voice": "Warm, precise, collaborative",
            "show_actor_name": False,
            "show_meta_persona": False,
        }

        # Theme settings (used by Streamlit theme panel)
        self.theme_settings = {
            "font_size": "medium",
            "density": "comfortable",
            "accent_color": "blue",
            "mode": "Continuum",
        }

        # Actor settings (used by Actor Controls Panel)
        self.actor_settings = {
            "SenateArchitect": {"enabled": True, "weight": 1.0},
            "SenateStoryweaver": {"enabled": True, "weight": 1.0},
            "SenateAnalyst": {"enabled": True, "weight": 1.0},
            "SenateSynthesizer": {"enabled": True, "weight": 1.0},
        }

        # Traces panel expects these
        self.last_ranked_proposals: List[dict] = []
        self.last_final_proposal: dict | None = None
        self.tool_logs = []

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

    # ---------------------------------------------------------
    # Lazy emotion model loader
    # ---------------------------------------------------------
    def get_emotion_model(self):
        if self.emotion_model is None:
            from transformers import pipeline
            self.emotion_model = pipeline(
                "text-classification",
                model="SamLowe/roberta-base-go_emotions",
                top_k=None,
            )
        return self.emotion_model

    # ---------------------------------------------------------
    # Keyword-based emotion override
    # ---------------------------------------------------------
    def keyword_emotion_override(self, text: str):
        """
        Rule-based overrides for common emotional expressions that
        transformer models often misclassify.
        """
        text = text.lower()

        overrides = {
            "overwhelmed": ("sadness", 0.85),
            "burned out": ("sadness", 0.9),
            "burnt out": ("sadness", 0.9),
            "stressed": ("anxiety", 0.8),
            "anxious": ("anxiety", 0.9),
            "worried": ("anxiety", 0.75),
            "frustrated": ("anger", 0.8),
            "angry": ("anger", 0.9),
            "lonely": ("sadness", 0.9),
            "numb": ("sadness", 0.7),
            "tired": ("sadness", 0.6),
            "exhausted": ("sadness", 0.85),
            "confused": ("confusion", 0.8),
        }

        for key, (label, intensity) in overrides.items():
            if key in text:
                return label, intensity

        return None

    # ---------------------------------------------------------
    # Main pipeline
    # ---------------------------------------------------------
    def process_message(self, message: str) -> str:
        """
        Full Continuum pipeline:
        1. Detect emotion + store in EmotionalMemory
        2. Senate gathers and ranks proposals
        3. Jury selects the best proposal
        4. Winning actor generates final response
        """

        print("PROCESS_MESSAGE CALLED")

        # ❌ IMPORTANT: Removed duplicate user-message add
        # self.context.add_user_message(message)

        # 2. Detect emotion
        emotion_label = ""
        intensity = 0.0

        try:
            override = self.keyword_emotion_override(message)
            if override:
                emotion_label, intensity = override
            else:
                raw = self.get_emotion_model()(message)
                top = raw[0][0]
                emotion_label = top["label"]
                intensity = top["score"]

        except Exception as e:
            print("DEBUG emotion detection failed:", e)

        # Store in EmotionalMemory
        self.emotional_memory.add_event(emotion_label, intensity)
        print("DEBUG EmotionalMemory.add_event:", emotion_label, intensity)

        # 3. Senate deliberation
        ranked_proposals = self.senate.deliberate(self.context, message, self)
        self.last_ranked_proposals = ranked_proposals

        # 4. Jury adjudication
        final_proposal = self.jury.adjudicate(
            ranked_proposals,
            message=message,
            user_emotion=self.emotional_memory.get_emotional_state(),
            memory_summary=self.context.get_memory_summary(),
        )
        self.last_final_proposal = final_proposal

        # 5. Winning actor generates final response
        actor_name = final_proposal.get("actor")
        actor = self.actors.get(actor_name)

        self.meta_persona.voice = self.persona_settings["voice"]
        self.context.debug_flags["show_meta_persona"] = self.persona_settings["show_meta_persona"]

        if not actor:
            return "The Continuum encountered an error: unknown actor."

        final_text = actor.respond(self.context, final_proposal)

        # Meta-persona rewrite
        rewritten = self.meta_persona.render(final_text, self.context)

        # Store the rewritten version (not the raw actor output)
        self.context.add_assistant_message(rewritten)

        # -----------------------------------------
        # Store per-turn metadata for timeline
        # -----------------------------------------
        self.turn_history.append({
            "user": message,
            "emotion": {
                "label": emotion_label,
                "intensity": intensity
            },
            "final_proposal": final_proposal,
            "assistant": rewritten
        })

        return ""