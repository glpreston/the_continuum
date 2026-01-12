# continuum/actors/base_actor.py

import io
from abc import ABC
from typing import Any, Dict, Optional

import soundfile as sf

from continuum.audio.tts_engine import tts_engine
from continuum.persona.actor_speakers import ACTOR_SPEAKERS


class BaseActor(ABC):
    """
    The foundational actor class for The Continuum.
    Every actor—specialist or meta—derives from this.
    """

    def __init__(self, name: str, persona: Optional[Dict[str, Any]] = None):
        self.name = name
        self.persona = persona or {}

    # ---------------------------------------------------------
    # PROPOSAL GENERATION
    # ---------------------------------------------------------
    def propose(self, context, message: str) -> Dict[str, Any]:
        """
        Phase 3: Unified proposal pipeline.
        1. Generate reasoning steps
        2. Convert steps into a proposal
        3. Compute dynamic confidence
        """
        steps = self.reason(context, message)
        content = self.generate_proposal_from_steps(steps, message)
        confidence = self.compute_confidence(steps)

        return {
            "actor": self.name,
            "content": content,
            "confidence": confidence,
            "reasoning": steps,
            "metadata": {
                "type": "phase3",
                "persona": self.persona,
            },
        }

    # ---------------------------------------------------------
    # FINAL RESPONSE GENERATION
    # ---------------------------------------------------------
    def respond(self, context, selected_proposal: Dict[str, Any]) -> str:
        """
        Converts the selected proposal into a final user-facing response.
        Subclasses may override this to apply persona tone, formatting,
        or additional reasoning.
        """
        return selected_proposal.get("content", "")

    # ---------------------------------------------------------
    # OPTIONAL HOOKS
    # ---------------------------------------------------------
    def load_memory(self, memory_system):
        """Optional hook for actors that need memory access."""
        self.memory = memory_system

    def load_tools(self, tool_registry):
        """Optional hook for actors that need tool access."""
        self.tools = tool_registry

    def summarize_reasoning(self, proposal: dict) -> str:
        """
        Safe, abstracted explanation of why this actor proposed what they did.
        Does NOT reveal chain-of-thought. Uses persona traits only.
        """
        persona = self.persona

        persona_style = persona.get("style", "general")
        goal = persona.get("goal", "provide helpful guidance")

        return (
            f"This proposal reflects the actor's style of {persona_style}, "
            f"aimed at {goal}. It focuses on the key elements the actor "
            f"considers most relevant to the user's message."
        )

    # ---------------------------------------------------------
    # PHASE 3: MULTI-STEP REASONING FRAMEWORK
    # ---------------------------------------------------------
    def reason(self, context, message: str) -> list:
        """
        Multi-step reasoning chain.
        Subclasses override this to express their cognitive style.
        Default implementation provides a generic 3-step chain.
        """
        return [
            "Step 1: Interpreting the user's intent.",
            "Step 2: Identifying relevant knowledge or perspectives.",
            "Step 3: Formulating a coherent response strategy."
        ]

    def generate_proposal_from_steps(self, steps: list, message: str) -> str:
        """
        Converts a reasoning chain into a final proposal.
        Actors may override this for more expressive output.
        """
        joined = " ".join(steps)
        return (
            f"{joined} Final interpretation of the message: '{message}'."
        )

    def compute_confidence(self, steps: list) -> float:
        """
        Computes confidence dynamically based on reasoning depth.
        Default: base confidence grows slightly with number of steps.
        Actors may override for personality-specific scoring.
        """
        base = 0.70
        bonus = min(len(steps) * 0.03, 0.15)  # cap bonus
        return round(base + bonus, 3)        

    # ---------------------------------------------------------
    # AUDIO: actor-specific voice
    # ---------------------------------------------------------
    def speak(self, text: str):
        """Generate audio for this actor using its assigned speaker."""
        speaker = ACTOR_SPEAKERS.get(self.name, "p225")

        # 1. Generate raw audio (numpy array or list)
        wav_array = tts_engine.synthesize(
            text,
            speaker=speaker,
            speed=1.0,
            energy=1.0,
            pitch=1.0,
        )

        # 2. Convert to WAV bytes for Streamlit
        buffer = io.BytesIO()
        sf.write(buffer, wav_array, 22050, format="WAV")
        buffer.seek(0)

        return buffer.read()