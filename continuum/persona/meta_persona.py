# continuum/person/ameta_persona.py  
from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, Any
import re

from continuum.meta.aria_emotional_blending import compute_aria_style
from continuum.emotion.emotional_memory_influence import emotional_memory_modifiers
from continuum.persona.voiceprint_loader import voiceprint_loader
from continuum.validators.voiceprint_validator import validate_output
from continuum.debug.meta_persona_panel import MetaPersonaDebugPanel
from continuum.emotion.state_machine import EmotionalState
from continuum.persona.emotional_memory import EmotionalMemory

from .tone_prefix import compute_dominant_emotion, tone_prefix
from .style_rewrite import apply_style
from .microtone import apply_microtone
from .memory_tone import apply_memory_tone
from .user_emotion_tone import apply_user_emotion_tone
from .volatility_modulation import apply_volatility_modulation
from .stochastic_variation import apply_stochastic_variation
from .voiceprint_constraints import apply_voiceprint_constraints
from .continuity_modulation import apply_continuity_modulation


@dataclass
class MetaPersona:
    name: str
    voice: str
    traits: Dict[str, str]

    def _compute_dominant_emotion(self, emotional_state):
        from .tone_prefix import compute_dominant_emotion
        return compute_dominant_emotion(emotional_state)


    def set_emotional_continuity(self, volatility: float, confidence: float, arc_label: str):
        self.volatility = volatility
        self.confidence = confidence
        self.arc_label = arc_label

    def _validate_voiceprint_alignment(
        self,
        text: str,
        emotional_state: EmotionalState,
        context: Any,
    ) -> None:
        if not context.debug_flags.get("validate_voiceprint"):
            return

        report = validate_output(
            text,
            emotional_state.as_dict(),
            voiceprint_loader.voiceprint,
        )

        print("\n=== Voiceprint Validation Report ===")
        print(report)
        print("====================================\n")

    def render(
        self,
        actor_output: str,
        controller: Any,
        context: Any,
        emotional_state: EmotionalState,
        emotional_memory: EmotionalMemory,
    ) -> str:
        prefix = ""

        if context.debug_flags.get("show_meta_persona"):
            prefix += f"{self.name}: "

        # Show actor name if enabled
        if context.debug_flags.get("show_actor_name") and controller.last_final_proposal:
            actor = controller.last_final_proposal.get("actor", "unknown")
            prefix += f"[{actor}] "

        # Determine if the winning actor is Storyweaver (robust detection)
        actor = controller.last_final_proposal.get("actor", "unknown")
        # print("DEBUG ACTOR NAME:", actor)  # optional debug

        is_storyweaver = (
            "storyweaver" in actor.lower()
            or "story" in actor.lower()
            or "weaver" in actor.lower()
        )

        dominant = compute_dominant_emotion(emotional_state)
        volatility = emotional_memory.volatility
        confidence = emotional_memory.confidence

        print("DEBUG PREFIX DOMINANT:", dominant)

        memory_mods = emotional_memory_modifiers(emotional_memory)
        emotional_prefix = tone_prefix(dominant, volatility, confidence)

        style = compute_aria_style(emotional_state)
        style["warmth"] += memory_mods["warmth_boost"]
        style["clarity"] += memory_mods["clarity_boost"]
        style["softness"] += memory_mods["grounding_boost"]
        style["brevity"] += memory_mods["pacing_slowdown"]

        #blended = apply_style(actor_output, style)
        if not is_storyweaver:
            blended = apply_style(actor_output, style)
        else:
            blended = actor_output

        if memory_mods["pacing_slowdown"] > 0.1 and "\n\n" not in blended:
            blended = re.sub(r"\. (?=[A-Z])", ".\n\n", blended)

        blended = apply_microtone(blended, emotional_state)
        blended = apply_memory_tone(blended, memory_mods)
        blended = apply_user_emotion_tone(blended, emotional_state)
        blended = apply_volatility_modulation(blended, emotional_memory)
        blended = apply_stochastic_variation(blended, style)
        blended = apply_voiceprint_constraints(blended, dominant)

        arc_label = getattr(self, "arc_label", "Stable Emotional Arc")
        volatility_cont = getattr(self, "volatility", volatility)
        confidence_cont = getattr(self, "confidence", confidence)

        blended = apply_continuity_modulation(
            blended,
            volatility_cont,
            confidence_cont,
            arc_label,
            style,
        )

        if emotional_prefix and blended and blended[0].islower():
            blended = blended[0].upper() + blended[1:]

        if emotional_prefix:
            emotional_prefix = emotional_prefix.rstrip() + " — "

        prefix = prefix.rstrip() + " " if prefix else ""

        final_text = f"{prefix}{emotional_prefix}{blended}".strip()

        report = None
        if context.debug_flags.get("validate_voiceprint"):
            report = validate_output(
                final_text,
                emotional_state.as_dict(),
                voiceprint_loader.voiceprint,
            )

        if context.debug_flags.get("debug_meta_persona"):
            panel = MetaPersonaDebugPanel()
            print(
                panel.render(
                    emotional_state,
                    emotional_memory,
                    style,
                    memory_mods,
                    dominant,
                    voiceprint_loader,
                    report,
                )
            )

        return final_text