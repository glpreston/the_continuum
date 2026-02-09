# continuum/persona/meta_persona.py
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Any
import re

from continuum.core.logger import log_info, log_debug, log_error
from continuum.meta.aria_emotional_blending import compute_aria_style
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


# ============================================================
# Sentence splitting (punctuation‑preserving)
# ============================================================
def split_sentences_preserve_punct(text: str):
    """
    Split text into sentences while preserving punctuation.
    This replaces the old Phase‑3/4 destructive splitter.
    """
    text = text.replace("\n", " ").strip()
    parts = re.split(r"(?<=[.!?])\s+", text)
    return [p.strip() for p in parts if p.strip()]

# ============================================================
# Updated fragment detection (enumeration‑safe)
# ============================================================
def is_enumeration(sentence: str) -> bool:
    """
    Detects enumerated list items like:
    '1. Something', '2) Something', '3 - Something'
    """
    return bool(re.match(r"^\s*\d+[\.\)\-]\s+", sentence))


def is_short_valid(sentence: str) -> bool:
    """
    Allows short but valid sentences like:
    'Yes.', 'No.', 'Indeed.', 'Absolutely.'
    """
    return len(sentence.split()) <= 3 and sentence.endswith((".", "!", "?"))

# ---------------------------------------------------------
# Fragment + meta/safety detection
# ---------------------------------------------------------
def is_fragment(sentence: str) -> bool:
    """
    Improved fragment detection:
    - Allows enumerations
    - Allows short valid sentences
    - Avoids removing list items
    """
    s = sentence.strip()

    if not s:
        return True

    if is_enumeration(s):
        return False

    if is_short_valid(s):
        return False

    # Original fragment logic
    if len(s.split()) < 4:
        return True

    if not re.search(
        r"\b(is|are|was|were|be|being|been|has|have|had|do|does|did|can|could|will|would|should|may|might)\b",
        s,
    ):
        return True

    if s.endswith(("and", "or", "but", "so", "because", "as")):
        return True

    return False



@dataclass
class MetaPersona:
    """
    Meta‑Persona 2.0 — Phase‑5 canonical persona engine.
    Fully backward‑compatible with Phase‑4 positional calls.
    """
    name: str
    voice: str
    traits: Dict[str, str]

    # ---------------------------------------------------------
    # Voiceprint validation (debug only)
    # ---------------------------------------------------------
    def _validate_voiceprint_alignment(self, text, emotional_state, context):
        if not getattr(context, "debug_flags", {}).get("validate_voiceprint"):
            return

        report = validate_output(
            text,
            emotional_state.as_dict(),
            voiceprint_loader.voiceprint,
        )

        log_info("\n=== Voiceprint Validation Report ===", phase="meta_persona")
        log_info(report, phase="meta_persona")
        log_info("====================================\n", phase="meta_persona")

    # ---------------------------------------------------------
    # Rewrite strength computation
    # ---------------------------------------------------------
    def _compute_rewrite_strength(self, emotional_state, emotional_memory, actor_name):
        dominant = compute_dominant_emotion(emotional_state)
        volatility = emotional_memory.volatility
        confidence = emotional_memory.confidence
        actor_lower = (actor_name or "").lower()

        if volatility > 0.7:
            strength = "strong"
        elif volatility > 0.4:
            strength = "moderate"
        else:
            strength = "subtle"

        if confidence < 0.3 and strength != "strong":
            strength = "moderate"
        if confidence > 0.8 and strength == "strong":
            strength = "moderate"

        if "story" in actor_lower or "weaver" in actor_lower:
            if strength == "strong":
                strength = "moderate"

        if "analyst" in actor_lower:
            if strength == "strong":
                strength = "moderate"

        if dominant in ("sad", "tender", "anxious"):
            if strength == "strong":
                strength = "moderate"

        return strength
   
    def _sentence_is_meta_or_safety(self, s: str) -> bool:
        lower = s.lower()

        META_PATTERNS = [
            r"\bthe user\b",
            r"\bthis prompt\b",
            r"\bthis message\b",
            r"\bthe request\b",
            r"\bcan be broken down\b",
            r"\bthe core intent\b",
            r"\bthe user is\b",
            r"\bin summary\b",
            r"\boverall\b",
        ]

        SAFETY_PATTERNS = [
            r"\bi cannot provide\b",
            r"\bconsult a professional\b",
            r"\bmedical advice\b",
            r"\blegal advice\b",
        ]

        SCAFFOLD_PATTERNS = [
            r"\bhere\'s a breakdown\b",
            r"\blet\'s explore\b",
        ]

        for pattern in META_PATTERNS + SAFETY_PATTERNS + SCAFFOLD_PATTERNS:
            if re.search(pattern, lower):
                return True

        return False

    # ---------------------------------------------------------
    # Rule‑based rewrite (punctuation‑preserving)
    # ---------------------------------------------------------
    def _rule_based_rewrite(self, text, emotional_state, emotional_memory, actor_name):
        strength = self._compute_rewrite_strength(
            emotional_state,
            emotional_memory,
            actor_name,
        )

        log_debug(
            f"[MetaPersona] _rule_based_rewrite (strength={strength})",
            phase="meta_persona",
        )

        text = re.sub(r"\s+", " ", text).strip()
        if not text:
            return text

        # NEW: punctuation‑preserving sentence splitting
        sentences = split_sentences_preserve_punct(text)

        cleaned = []
        seen = set()

        for s in sentences:
            if self._sentence_is_meta_or_safety(s):
                continue
            if is_fragment(s):
                continue

            key = s.lower().strip()
            if key in seen:
                continue

            seen.add(key)
            cleaned.append(s)

        if not cleaned:
            cleaned = sentences

        # Preserve punctuation and spacing
        return " ".join(cleaned).strip()
        
    # ---------------------------------------------------------
    # Semantic rewrite
    # ---------------------------------------------------------
    def _semantic_rewrite(self, text, emotional_state, emotional_memory, actor_name):
        rewritten = self._rule_based_rewrite(
            text,
            emotional_state,
            emotional_memory,
            actor_name,
        )

        if not rewritten.strip():
            return text

        return rewritten

    # ---------------------------------------------------------
    # BACKWARD‑COMPATIBLE RENDER
    # ---------------------------------------------------------
    def render(
        self,
        *args,
        text=None,
        persona_name=None,
        emotion=None,
        controller=None,
        context=None,
        emotional_state=None,
        emotional_memory=None,
        actor_name=None,
        **kwargs,
    ) -> str:

        # -----------------------------------------------------
        # 1. Legacy positional signatures
        # -----------------------------------------------------
        if args:
            if text is None:
                text = args[0]

            if len(args) > 1 and controller is None:
                controller = args[1]

            if len(args) > 2 and context is None:
                context = args[2]

            if len(args) > 3 and emotional_state is None:
                emotional_state = args[3]

            if len(args) > 4 and emotional_memory is None:
                emotional_memory = args[4]

        # -----------------------------------------------------
        # 2. TEXT NORMALIZATION
        # -----------------------------------------------------
        if not isinstance(text, str):
            try:
                if isinstance(text, dict):
                    text = (
                        text.get("content")
                        or text.get("text")
                        or text.get("message")
                        or text.get("raw_response")
                        or str(text)
                    )
                elif isinstance(text, (list, tuple, set)):
                    text = " ".join(str(item) for item in text if item is not None)
                else:
                    text = str(text)
            except Exception:
                text = ""

        if text is None:
            text = ""

        # -----------------------------------------------------
        # 3. Fallback emotional state + memory
        # -----------------------------------------------------
        if emotional_state is None and controller is not None:
            emotional_state = getattr(controller, "emotion_state", None)

        if emotional_memory is None and controller is not None:
            emotional_memory = getattr(controller, "emotion_memory", None)

        if emotional_state is None or emotional_memory is None:
            log_error("[AIRA][meta_persona] Missing emotional_state or emotional_memory; returning text unchanged")
            return text

        # -----------------------------------------------------
        # 4. Fallback context
        # -----------------------------------------------------
        if context is None and controller is not None:
            context = getattr(controller, "context", None)

        if context is None:
            class _DummyContext:
                debug_flags = {}
            context = _DummyContext()

        # -----------------------------------------------------
        # 5. Actor resolution
        # -----------------------------------------------------
        if actor_name is None and controller is not None:
            proposal = getattr(controller, "last_final_proposal", None)
            if isinstance(proposal, dict):
                actor_name = proposal.get("actor", "unknown")

        actor_name = actor_name or "unknown"

        # -----------------------------------------------------
        # 6. Voiceprint + debug prefix
        # -----------------------------------------------------
        system_voiceprint = voiceprint_loader.get_active_system_voiceprint()

        log_debug(
            "[AIRA][meta_persona] Using SystemVoiceprint "
            f"version={system_voiceprint.version}, baseline_tone={system_voiceprint.baseline_tone}",
            phase="meta_persona",
        )

        prefix = ""
        if getattr(context, "debug_flags", {}).get("show_meta_persona"):
            prefix += f"{persona_name or self.name}: "

        if context.debug_flags.get("show_actor_name") and getattr(controller, "last_final_proposal", None):
            prefix += f"[{controller.last_final_proposal.get('actor', 'unknown')}] "

        # -----------------------------------------------------
        # 7. Emotional + memory context
        # -----------------------------------------------------
        dominant = compute_dominant_emotion(emotional_state)
        volatility = emotional_memory.volatility
        confidence = emotional_memory.confidence

        memory_mods = emotional_memory.apply_memory_influence()
        emotional_prefix = tone_prefix(dominant, volatility, confidence)

        style = compute_aria_style(emotional_state)
        style["warmth"] += memory_mods["warmth_boost"]
        style["clarity"] += memory_mods["clarity_boost"]
        style["softness"] += memory_mods["grounding_boost"]
        style["brevity"] += memory_mods["pacing_slowdown"]

        # -----------------------------------------------------
        # 8. Semantic rewrite (skip for Storyweaver)
        # -----------------------------------------------------
        is_storyweaver = (
            "story" in actor_name.lower()
            or "weaver" in actor_name.lower()
        )

        if not is_storyweaver:
            rewritten_core = self._semantic_rewrite(
                text,
                emotional_state,
                emotional_memory,
                actor_name,
            )
        else:
            rewritten_core = text

        # -----------------------------------------------------
        # 9. Style + tonal pipeline
        # -----------------------------------------------------
        blended = apply_style(
            rewritten_core,
            style,
            system_voiceprint=system_voiceprint,
        ) or rewritten_core

        # Paragraph preservation (Option A)
        if memory_mods["pacing_slowdown"] > 0.1 and "\n\n" not in blended:
            blended = re.sub(r"\. (?=[A-Z])", ".\n\n", blended)

        blended = apply_microtone(blended, emotional_state) or blended
        blended = apply_memory_tone(blended, memory_mods) or blended
        blended = apply_user_emotion_tone(blended, emotional_state) or blended
        blended = apply_volatility_modulation(blended, emotional_memory) or blended
        blended = apply_stochastic_variation(blended, style) or blended
        blended = apply_voiceprint_constraints(blended, dominant) or blended

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

        # -----------------------------------------------------
        # 10. Prefix + final assembly
        # -----------------------------------------------------
        if emotional_prefix and blended and blended[0].islower():
            blended = blended[0].upper() + blended[1:]

        if emotional_prefix:
            emotional_prefix = emotional_prefix.rstrip() + " — "

        prefix = prefix.rstrip() + " " if prefix else ""

        final_text = f"{prefix}{emotional_prefix}{blended}".strip()

        # -----------------------------------------------------
        # 11. Optional debug + validation
        # -----------------------------------------------------
        self._validate_voiceprint_alignment(final_text, emotional_state, context)

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
                    None,
                )
            )

        return final_text