# continuum/orchestrator/continuum_controller.py
# updated for ei 2.0

import uuid
from typing import Any, List

from ..core.context import ContinuumContext
from .senate import Senate
from .jury import Jury
from continuum.tools.tool_registry import ToolRegistry
from continuum.persona.meta_persona import MetaPersona
import inspect
print("MetaPersona loaded from:", inspect.getfile(MetaPersona))

# Senate actors
from continuum.actors.senate_architect import SenateArchitect
from continuum.actors.senate_storyweaver import SenateStoryweaver
from continuum.actors.senate_analyst import SenateAnalyst
from continuum.actors.senate_synthesizer import SenateSynthesizer

# Emotional memory
from continuum.persona.emotional_memory import EmotionalMemory

# Semantic embedding for Jury emotional alignment
from continuum.memory.semantic import embed as get_embedding

# Phase 4 emotional engine
from continuum.emotion.mappings import build_delta_from_labels
from continuum.emotion.state_machine import update_emotional_state, EmotionalState


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

        # Phase 4: persistent emotional state
        self.emotional_state = EmotionalState()

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
        2. Update Phase 4 Emotional State
        3. Senate gathers and ranks proposals
        4. Jury selects the best proposal
        5. Winning actor generates final response
        """

        print("PROCESS_MESSAGE CALLED")

        # ---------------------------------------------------------
        # 1. Detect emotion (EI‑2.0 format)
        # ---------------------------------------------------------
        raw_state = {}
        dominant_emotion = ""
        intensity = 0.0

        try:
            # Keyword override first
            override = self.keyword_emotion_override(message)
            if override:
                label, score = override
                raw_state = {label: score}
                dominant_emotion = label
                intensity = score

            else:
                # Transformer model output
                raw = self.get_emotion_model()(message)[0]

                # Convert to EI‑2.0 dimension dict
                raw_state = {entry["label"]: entry["score"] for entry in raw}

                # Dominant emotion
                dominant_emotion = max(raw_state, key=raw_state.get)
                intensity = raw_state[dominant_emotion]

        except Exception as e:
            print("DEBUG emotion detection failed:", e)
            raw_state = {"neutral": 0.0}
            dominant_emotion = "neutral"
            intensity = 0.0

        # ---------------------------------------------------------
        # Store EI‑2.0 emotional event
        # ---------------------------------------------------------
        self.emotional_memory.add_event(
            raw_state=raw_state,
            dominant_emotion=dominant_emotion,
            metadata={"source": "model"},
        )

        # ---------------------------------------------------------
        # 2. Phase 4 Emotional State Machine Update
        # ---------------------------------------------------------

        # Optional: reset emotional state for testing (neutral baseline)
        if self.context.debug_flags.get("reset_emotion_each_message"):
            self.emotional_state = EmotionalState()  # fresh baseline

        # Compute delta from the new message
        delta = build_delta_from_labels(raw_state)

        # Update emotional state with EI‑2.0 inertia + decay
        self.emotional_state = update_emotional_state(self.emotional_state, delta)

        print("DEBUG EmotionalState:", self.emotional_state.as_dict())

        # ---------------------------------------------------------
        # 3. Senate deliberation
        # ---------------------------------------------------------
        ranked_proposals = self.senate.deliberate(self.context, message, self)
        self.last_ranked_proposals = ranked_proposals

        # 4. Jury adjudication version EI‑2.0
        final_proposal = self.jury.adjudicate(
            ranked_proposals,
            message=message,
            user_emotion=self.emotional_memory.get_smoothed_state(),  # EI‑2.0
            memory_summary=self.context.get_memory_summary(),
            emotional_state=EmotionalState.from_dict(self.emotional_state.as_dict()),
        )

        self.last_final_proposal = final_proposal

        # 5. Winning actor generates final response
        actor_name = final_proposal.get("actor")
        actor = self.actors.get(actor_name)

        self.meta_persona.voice = self.persona_settings["voice"]
        self.context.debug_flags["show_meta_persona"] = self.persona_settings["show_meta_persona"]

        if not actor:
            return "The Continuum encountered an error: unknown actor."

        final_text = actor.respond(
            context=self.context,
            proposal=final_proposal,
            emotional_memory=self.emotional_memory,
            emotional_state=EmotionalState.from_dict(self.emotional_state.as_dict()),
        )
        self.last_raw_actor_output = final_text

        # Meta-persona rewrite
        rewritten = self.meta_persona.render(
            final_text,
            self.context,
            self.emotional_state,
            self.emotional_memory,
        )

        # Store the rewritten version (not the raw actor output)
        self.context.add_assistant_message(rewritten)

        # Store per-turn metadata for timeline
        self.turn_history.append({
            "user": message,
            "emotion": {
                "dominant": dominant_emotion,
                "intensity": intensity,
                "raw_state": raw_state,
            },
            "final_proposal": final_proposal,
            "assistant": rewritten,
        })

        # ⭐ return the rewritten output
        return rewritten