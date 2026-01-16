# continuum/orchestrator/continuum_controller.py
# updated for EI 2.0 + modular Fusion/Arc

import uuid
from typing import Any, List, Dict

from ..core.context import ContinuumContext
from .senate import Senate
from .jury import Jury
from continuum.tools.tool_registry import ToolRegistry
from continuum.persona.meta_persona import MetaPersona

from continuum.actors.senate_architect import SenateArchitect
from continuum.actors.senate_storyweaver import SenateStoryweaver
from continuum.actors.senate_analyst import SenateAnalyst
from continuum.actors.senate_synthesizer import SenateSynthesizer

from continuum.persona.emotional_memory import EmotionalMemory
from continuum.memory.semantic import embed as get_embedding

from continuum.emotion.mappings import build_delta_from_labels
from continuum.emotion.state_machine import update_emotional_state, EmotionalState
from continuum.emotion.emotional_arc_engine import EmotionalArcEngine
from continuum.emotion.emotional_momentum import apply_emotional_momentum

from .fusion_smoothing import FusionSmoother
from .fusion_engine import fused_response

# Actors mindset imports
from continuum.actors.storyweaver import Storyweaver
from continuum.actors.analyst import Analyst
from continuum.actors.synthesizer import Synthesizer
from continuum.actors.architect import Architect


class ContinuumController:
    """
    The orchestrator of The Continuum.
    Coordinates:
      - context management
      - Senate deliberation
      - Jury adjudication
      - Fusion 2.0
      - Meta‑Persona rewrite
      - Emotional arcs (Phase 4D)
    """

    def __init__(self, *args, **kwargs):

        # ---------------------------------------------------------
        # Core state
        # ---------------------------------------------------------
        self.turn_history = []

        # Emotional memory
        self.emotional_memory = EmotionalMemory(max_events=20)

        # Persistent emotional state
        self.emotional_state = EmotionalState()

        # Emotional Arc Engine
        self.emotional_arc_engine = EmotionalArcEngine()

        # Fusion smoothing
        self.fusion_smoother = FusionSmoother(alpha=0.6)

        # Lazy-loaded emotion model
        self.emotion_model = None

        # Narrator mode
        self.narrator_mode = False

        # ---------------------------------------------------------
        # ACTORS: Senate (Phase 3) + LLM Actors (Phase 4)
        # ---------------------------------------------------------

        # Senate actors
        self.senate_actors = [
            SenateArchitect(),
            SenateStoryweaver(),
            SenateAnalyst(),
            SenateSynthesizer(),
        ]

        # LLM actors
        self.llm_actors = {
            "Storyweaver": Storyweaver(),
            "Analyst": Analyst(),
            "Synthesizer": Synthesizer(),
            "Architect": Architect(),
        }

        self.senate_to_llm_map = {
            "SenateArchitect": "Architect",
            "SenateStoryweaver": "Storyweaver",
            "SenateAnalyst": "Analyst",
            "SenateSynthesizer": "Synthesizer",
        }

        # Senate orchestrator
        self.senate = Senate(self.senate_actors)

        # Jury
        self.jury = Jury()

        # Controller-level actor lookup
        self.actors = self.llm_actors

        # ---------------------------------------------------------
        # Context
        # ---------------------------------------------------------
        self.context = ContinuumContext(conversation_id=str(uuid.uuid4()))

        # ---------------------------------------------------------
        # Embedding function wiring (FIXED)
        # ---------------------------------------------------------
        # Define embedding function FIRST
        self.embed_fn = get_embedding

        # Then inject into Jury
        self.jury.embed_fn = self.embed_fn

        # ---------------------------------------------------------
        # Tools
        # ---------------------------------------------------------
        self.tool_registry = ToolRegistry()

        # Persona settings
        self.persona_settings = {
            "voice": "Warm, precise, collaborative",
            "show_actor_name": False,
            "show_meta_persona": False,
        }

        # Theme settings
        self.theme_settings = {
            "font_size": "medium",
            "density": "comfortable",
            "accent_color": "blue",
            "mode": "Continuum",
        }

        # Actor settings
        self.actor_settings = {
            "SenateArchitect": {"enabled": True, "weight": 1.0},
            "SenateStoryweaver": {"enabled": True, "weight": 1.0},
            "SenateAnalyst": {"enabled": True, "weight": 1.0},
            "SenateSynthesizer": {"enabled": True, "weight": 1.0},
        }

        # Debug traces
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
        Full Continuum pipeline (Fusion 2.0 + Emotional Arcs):
        1. Detect emotion + store in EmotionalMemory
        2. Update Emotional State
        3. Senate deliberation
        4. Jury adjudication → fusion_weights
        5. Fusion 2.0 (with smoothing + emotional momentum)
        6. Meta‑Persona rewrite
        7. Emotional Arc snapshot
        """

        # 1. Emotion detection
        raw_state: Dict[str, float] = {}
        dominant_emotion = ""
        intensity = 0.0

        try:
            override = self.keyword_emotion_override(message)
            if override:
                label, score = override
                raw_state = {label: score}
                dominant_emotion = label
                intensity = score
            else:
                raw = self.get_emotion_model()(message)[0]
                raw_state = {entry["label"]: entry["score"] for entry in raw}
                dominant_emotion = max(raw_state, key=raw_state.get)
                intensity = raw_state[dominant_emotion]
        except Exception as e:
            print("DEBUG emotion detection failed:", e)
            raw_state = {"neutral": 0.0}
            dominant_emotion = "neutral"
            intensity = 0.0

        self.emotional_memory.add_event(
            raw_state=raw_state,
            dominant_emotion=dominant_emotion,
            metadata={"source": "model"},
        )

        # 2. Emotional state update
        if self.context.debug_flags.get("reset_emotion_each_message"):
            self.emotional_state = EmotionalState()

        delta = build_delta_from_labels(raw_state)
        self.emotional_state = update_emotional_state(self.emotional_state, delta)

        self.last_emotional_state = self.emotional_state
        self.last_emotional_memory = self.emotional_memory

        # 3. Senate deliberation
        ranked_proposals = self.senate.deliberate(
            context=self.context,
            message=message,
            controller=self,
            emotional_state=self.emotional_state,
            emotional_memory=self.emotional_memory,
        )
        self.last_ranked_proposals = ranked_proposals

        # 4. Jury adjudication
        final_proposal = self.jury.adjudicate(
            ranked_proposals,
            message=message,
            user_emotion=self.emotional_memory.get_smoothed_state(),
            memory_summary=self.context.get_memory_summary(),
            emotional_state=EmotionalState.from_dict(self.emotional_state.as_dict()),
        )
        self.last_final_proposal = final_proposal

        raw_fusion_weights = final_proposal.get("metadata", {}).get("fusion_weights")

        # 5. Fusion smoothing + emotional momentum
        fusion_weights = self.fusion_smoother.smooth(raw_fusion_weights or {})
        fusion_weights = apply_emotional_momentum(
            fusion_weights or {}, self.emotional_arc_engine.get_history()
        )

        # 6. Fusion or single actor
        self.meta_persona.voice = self.persona_settings["voice"]
        self.context.debug_flags["show_meta_persona"] = self.persona_settings[
            "show_meta_persona"
        ]

        if fusion_weights:
            final_text = fused_response(
                fusion_weights=fusion_weights,
                ranked_proposals=ranked_proposals,
                controller=self,
            )
        else:
            actor_name = final_proposal.get("actor")
            llm_name = self.senate_to_llm_map.get(actor_name, actor_name)
            actor = self.actors.get(llm_name)

            if not actor:
                return "The Continuum encountered an error: unknown actor."

            final_text = actor.respond(
                context=self.context,
                selected_proposal=final_proposal,
                emotional_memory=self.emotional_memory,
                emotional_state=self.emotional_state,
            )
            self.last_raw_actor_output = final_text

            # Update Meta-Persona emotional continuity
            self.meta_persona.set_emotional_continuity(
                volatility=self.emotional_state.volatility,
                confidence=self.emotional_state.confidence,
                arc_label=self.emotional_arc_engine.classify_arc(),
            )

        # 7. Meta‑Persona rewrite
        rewritten = self.meta_persona.render(
            final_text,
            self,
            self.context,
            self.emotional_state,
            self.emotional_memory
        )
        self.context.add_assistant_message(rewritten)

        # 8. Emotional Arc snapshot
        self.emotional_arc_engine.record_snapshot(
            emotional_state=self.emotional_state,
            dominant_emotion=dominant_emotion,
            fusion_weights=fusion_weights or {},
        )

        # 9. Turn timeline logging
        self.turn_history.append(
            {
                "user": message,
                "emotion": {
                    "dominant": dominant_emotion,
                    "intensity": intensity,
                    "raw_state": raw_state,
                },
                "final_proposal": final_proposal,
                "assistant": rewritten,
            }
        )

        return rewritten