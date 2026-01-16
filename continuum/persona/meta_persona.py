# continuum/persona/meta_persona.py
# version EI‑2.0 (refactored with voiceprint + validator integration)

from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, Any
import re

from continuum.meta.aria_emotional_blending import compute_aria_style
from continuum.emotion.emotional_memory_influence import emotional_memory_modifiers
from continuum.persona.voiceprint_loader import voiceprint_loader
from continuum.validators.voiceprint_validator import validate_output
from continuum.debug.meta_persona_panel import MetaPersonaDebugPanel


@dataclass
class MetaPersona:
    """
    The unified voice of The Continuum.
    Transforms actor output into a coherent, emotionally aware response.
    """

    name: str
    voice: str
    traits: Dict[str, str]

    # ---------------------------------------------------------
    # Core emotional helpers
    # ---------------------------------------------------------
    def _compute_dominant_emotion(self, emotional_state) -> str:
        state_dict = emotional_state.as_dict()
        filtered = {k: v for k, v in state_dict.items() if k != "fatigue"}

        values = list(filtered.values())
        max_val = max(values)
        min_val = min(values)

        if max_val - min_val < 0.02:
            return "neutral"

        return max(filtered, key=filtered.get)

    def _tone_prefix(self, dominant: str, volatility: float, confidence: float) -> str:
        if volatility > 0.55:
            return "Let’s slow down and take this step by step. "

        if dominant in ("sadness", "fatigue"):
            return "I’m moving gently with you here. "

        if dominant == "confusion":
            return "Let’s bring some clarity to this. "

        if dominant in ("anxiety", "nervousness"):
            return "We can keep things grounded. "

        if dominant == "curiosity":
            return "Let’s explore this together. "

        return ""

    # ---------------------------------------------------------
    # Step 3 — Style rewrite (EI‑2.0)
    # ---------------------------------------------------------
    def apply_style(self, text: str, style: Dict[str, float]) -> str:
        warmth = style["warmth"]
        clarity = style["clarity"]
        brevity = style["brevity"]
        creativity = style["creativity"]
        softness = style["softness"]

        if warmth > 1.1:
            text = text.replace("I interpret this as", "I understand this as")
            text = text.replace("Here is", "Let’s explore")

        if clarity > 1.1:
            text = re.sub(r"\band\b", "and also", text)

        if brevity > 1.1:
            words = text.split()
            if len(words) > 140:
                text = " ".join(words[:140]) + "..."

        if creativity > 1.1:
            text = text.replace("integrated perspective", "woven perspective")
            text = text.replace("common ground", "shared horizon")

        if softness > 1.1:
            text = text.replace("resolve tensions", "ease the strain")
            text = text.replace("unified path", "gentle next step")

        return text

    # ---------------------------------------------------------
    # Step 4 — Micro‑Tone Modulation
    # ---------------------------------------------------------
    def _microtone(self, text: str, emotional_state) -> str:
        state = emotional_state.as_dict()

        curiosity = state.get("curiosity", 0)
        calm = state.get("calm", 0)
        tension = state.get("tension", 0)
        confidence = state.get("confidence", 0)
        fatigue = state.get("fatigue", 0)

        if curiosity > 0.45:
            text = re.sub(r"\bHere is\b", "Here’s one way to see this", text)
            text = re.sub(r"\bThis\b", "One angle on this", text, count=1)

        if calm > 0.45:
            text = text.replace("However", "At the same time")
            text = text.replace("But", "That said")

        if tension > 0.45:
            text = re.sub(r"\bThis means\b", "This suggests", text)
            text = re.sub(r"\bIt is\b", "It may be", text)

        if confidence > 0.45:
            text = re.sub(r"\bperhaps\b", "clearly", text)
            text = re.sub(r"\bmaybe\b", "notably", text)

        if fatigue > 0.35:
            text = re.sub(r"\. (?=[A-Z])", ".\n\n", text)

        return text

    # ---------------------------------------------------------
    # Step 5 — Memory & user emotion tone
    # ---------------------------------------------------------
    def _apply_memory_tone(self, text: str, memory_mods: Dict[str, float]) -> str:
        if memory_mods.get("warmth_boost", 0) > 0.25:
            text = text.replace("Let’s", "Let’s take a bright look at this and")
            text = text.replace("This suggests", "This opens up the sense that")

        if memory_mods.get("pacing_slowdown", 0) > 0.15:
            text = re.sub(r"\. (?=[A-Z])", ".\n\n", text)
            text = text.replace("Let’s", "We can move gently as we")

        if memory_mods.get("grounding_boost", 0) > 0.25:
            text = text.replace("clearly", "steadily")
            text = text.replace("notably", "meaningfully")

        return text

    def _apply_user_emotion_tone(self, text: str, emotional_state) -> str:
        state = emotional_state.as_dict()
        values = list(state.values())
        max_val = max(values)
        min_val = min(values)

        if max_val - min_val < 0.02:
            dominant = "neutral"
        else:
            dominant = max(state, key=state.get)

        if dominant == "sadness":
            text = "I’m right here with you. " + text

        if dominant == "confusion":
            text = text.replace("Let’s explore", "Let’s make this clearer and explore")

        if dominant == "excitement":
            text = text.replace("Let’s", "Alright, let’s dive in and")

        if dominant == "anger":
            text = text.replace("We can keep things grounded", "We can steady the moment together")

        return text

    # ---------------------------------------------------------
    # Volatility & stochastic modulation
    # ---------------------------------------------------------
    def _apply_volatility_modulation(self, text: str, volatility: float) -> str:
        if volatility > 0.55:
            text = re.sub(r"\bperhaps\b", "let’s take this one step at a time", text)
            text = re.sub(r"\bclearly\b", "we can see", text)
            return text

        if volatility < 0.25:
            text = text.replace("—", " — ")
            text = text.replace(". ", ".\n")

        return text

    def _apply_stochastic_variation(self, text: str, style: Dict[str, float]) -> str:
        import random
        variants = []

        if style["warmth"] > 1.0:
            variants.append(lambda t: t.replace("Let’s", random.choice([
                "Let’s", "We can", "Together, let’s", "It may help to"
            ])))

        if style["creativity"] > 1.0:
            variants.append(lambda t: t.replace("This suggests", random.choice([
                "This opens the possibility that",
                "This hints at the idea that",
                "One way to see this is that"
            ])))

        if style["softness"] > 1.0:
            variants.append(lambda t: t.replace("We can", random.choice([
                "We can", "We might", "It’s okay if we", "We’re free to"
            ])))

        if variants:
            for fn in random.sample(variants, k=min(2, len(variants))):
                text = fn(text)

        return text

    # ---------------------------------------------------------
    # Voiceprint constraints (light integration)
    # ---------------------------------------------------------
    def _apply_voiceprint_constraints(self, text: str, dominant_emotion: str) -> str:
        pacing_rules = voiceprint_loader.get_pacing_rules()
        forbidden = voiceprint_loader.get_forbidden_elements()

        # Light forbidden element mitigation
        for term in forbidden:
            if term.lower() in text.lower():
                text = text.replace("obviously", "notably")
                text = text.replace("clearly you", "it may seem")

        # Pacing: high emotion → allow more line breaks if voiceprint permits
        if dominant_emotion in ("sadness", "fatigue", "tension"):
            if pacing_rules.get("high_emotion_line_breaks", False):
                text = re.sub(r"\. (?=[A-Z])", ".\n\n", text)

        return text

    # ---------------------------------------------------------
    # Final rewrite orchestration
    # ---------------------------------------------------------
    def _final_rewrite(
        self,
        text: str,
        emotional_state,
        emotional_memory,
        style: Dict[str, float],
        memory_mods: Dict[str, float],
        dominant: str,
    ) -> str:
        text = self._apply_memory_tone(text, memory_mods)
        text = self._apply_user_emotion_tone(text, emotional_state)
        text = self._apply_volatility_modulation(text, emotional_memory.volatility)
        text = self._apply_stochastic_variation(text, style)
        text = self._apply_voiceprint_constraints(text, dominant)
        return text

    # ---------------------------------------------------------
    # Validation hook
    # ---------------------------------------------------------
    def _validate_voiceprint_alignment(
        self,
        text: str,
        emotional_state,
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

    # ---------------------------------------------------------
    # EI‑2.0 Meta‑Persona Rendering
    # ---------------------------------------------------------
    def render(self, actor_output: str, context: Any, emotional_state, emotional_memory) -> str:
        prefix = ""

        if context.debug_flags.get("show_meta_persona"):
            prefix += f"{self.name}: "

        if context.debug_flags.get("show_actor_name") and context.last_final_proposal:
            actor = context.last_final_proposal.get("actor", "unknown")
            prefix += f"[{actor}] "

        # Emotional signals
        dominant = self._compute_dominant_emotion(emotional_state)
        volatility = emotional_memory.volatility
        confidence = emotional_memory.confidence

        print("DEBUG PREFIX DOMINANT:", dominant)

        # Emotional memory influence
        memory_mods = emotional_memory_modifiers(emotional_memory)
        emotional_prefix = self._tone_prefix(dominant, volatility, confidence)

        # Style blending
        style = compute_aria_style(emotional_state)
        style["warmth"] += memory_mods["warmth_boost"]
        style["clarity"] += memory_mods["clarity_boost"]
        style["softness"] += memory_mods["grounding_boost"]
        style["brevity"] += memory_mods["pacing_slowdown"]

        blended = self.apply_style(actor_output, style)

        if memory_mods["pacing_slowdown"] > 0.1:
            blended = re.sub(r"\. (?=[A-Z])", ".\n\n", blended)

        blended = self._microtone(blended, emotional_state)

        if emotional_prefix and blended and blended[0].islower():
            blended = blended[0].upper() + blended[1:]

        if emotional_prefix:
            emotional_prefix = emotional_prefix.rstrip() + " — "

        blended = self._final_rewrite(
            blended,
            emotional_state,
            emotional_memory,
            style,
            memory_mods,
            dominant,
        )

        # Optional voiceprint validation (returns report)
        report = None
        if context.debug_flags.get("validate_voiceprint"):
            report = validate_output(
                blended,
                emotional_state.as_dict(),
                voiceprint_loader.voiceprint
            )

        # Optional debug panel
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

        return f"{prefix}{emotional_prefix}{blended}"