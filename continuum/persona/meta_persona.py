# continuum/persona/meta_persona.py
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

    # ---------------------------------------------------------
    # Meta‑Persona 2.0: Adaptive semantic rewrite (hybrid)
    # ---------------------------------------------------------
    def _compute_rewrite_strength(
        self,
        emotional_state: EmotionalState,
        emotional_memory: EmotionalMemory,
        actor_name: str,
    ) -> str:
        """
        Returns one of: 'subtle', 'moderate', 'strong'
        based on emotional state, volatility, confidence, and actor.
        """

        dominant = compute_dominant_emotion(emotional_state)
        volatility = emotional_memory.volatility
        confidence = emotional_memory.confidence

        actor_lower = (actor_name or "").lower()

        # Base strength from emotional volatility
        if volatility > 0.7:
            strength = "strong"
        elif volatility > 0.4:
            strength = "moderate"
        else:
            strength = "subtle"

        # Confidence can soften or intensify
        if confidence < 0.3 and strength != "strong":
            strength = "moderate"
        if confidence > 0.8 and strength == "strong":
            strength = "moderate"

        # Actor‑based nudges
        if "storyweaver" in actor_lower or "story" in actor_lower:
            # Preserve more narrative texture
            if strength == "strong":
                strength = "moderate"
        if "analyst" in actor_lower:
            # Keep structure, avoid over‑poetic rewrite
            if strength == "strong":
                strength = "moderate"

        # Emotion‑based nudges
        if dominant in ("sad", "tender", "anxious"):
            # Softer, less aggressive rewriting
            if strength == "strong":
                strength = "moderate"

        return strength

    def _is_fragment(self, sentence: str) -> bool:
        s = sentence.strip().rstrip(",;:")

        if not s:
            return True

        # Too short
        if len(s.split()) < 4:
            return True

        # Must contain a verb
        if not re.search(
            r"\b(is|are|was|were|be|being|been|has|have|had|do|does|did|can|could|will|would|should|may|might)\b",
            s,
        ):
            return True

        # Dangling endings
        if s.endswith(("and", "or", "but", "so", "because", "as")):
            return True

        # NEW: clipped endings (no punctuation + last word obviously cut)
        if not s.endswith((".", "!", "?")):
            last = s.split()[-1]
            if len(last) <= 4 and not re.search(r"[aeiou]", last):
                return True

        return False

    def _sentence_is_meta_or_safety(self, s: str) -> bool:
        lower = s.lower()

        META_PATTERNS = [
            r"\bthe user\b",
            r"\bthe user\'s\b",
            r"\bthe request\b",
            r"\bthis prompt\b",
            r"\bthis message\b",
            r"\bthe message can be broken down\b",
            r"\bcan be broken down into\b",
            r"\bthe logical structure of\b",
            r"\bthe core intent\b",
            r"\bthe user is experiencing\b",
            r"\bthe user expresses\b",
            r"\bthe user is expressing\b",
            r"\bthe user is asking\b",
            r"\bto fulfill this request\b",
            r"\bto provide relevant information\b",
            r"\bi would need to clarify\b",
            r"\bit would be necessary to gather\b",
            r"\bthis can be broken down\b",
            r"\bthis statement\b",
            r"\bthe statement is\b",
            r"\bthe question is\b",
            r"\bin summary\b",
            r"\boverall\b",
        ]

        SAFETY_PATTERNS = [
            r"\bi cannot provide\b",
            r"\bi can\'t provide\b",
            r"\bi am unable to\b",
            r"\bi must ensure\b",
            r"\byou should consult\b",
            r"\bconsult a professional\b",
            r"\bmedical advice\b",
            r"\blegal advice\b",
        ]

        SCAFFOLD_PATTERNS = [
            r"\bhere\'s a breakdown\b",
            r"\blet\'s explore\b",
            r"\bthere are several factors\b",
            r"\bthis can be broken down\b",
        ]

        for pattern in META_PATTERNS + SAFETY_PATTERNS + SCAFFOLD_PATTERNS:
            if re.search(pattern, lower):
                return True

        return False
    
    def _rule_based_rewrite(
        self,
        text: str,
        emotional_state: EmotionalState,
        emotional_memory: EmotionalMemory,
        controller: Any,
        actor_name: str,
    ) -> str:
        """
        Core rule‑based rewrite:
          - remove meta, safety, scaffolding, fragments
          - deduplicate
          - unify into a single coherent paragraph
        """

        strength = self._compute_rewrite_strength(
            emotional_state,
            emotional_memory,
            actor_name,
        )

        # Normalize whitespace
        text = re.sub(r"\s+", " ", text).strip()
        if not text:
            return text

        # Split into rough sentences
        sentences = [s.strip() for s in re.split(r"(?<=[.!?])\s+", text) if s.strip()]

        cleaned = []
        seen = set()

        for s in sentences:
            if not s:
                continue

            # Remove meta / safety / scaffolding
            if self._sentence_is_meta_or_safety(s):
                continue

            # Remove fragments
            if self._is_fragment(s):
                continue

            key = s.lower().strip()
            if key in seen:
                continue
            seen.add(key)
            cleaned.append(s)

        if not cleaned:
            cleaned = sentences

        # Strength handling: subtle/moderate/strong all end as one paragraph,
        # but stronger levels are more willing to drop extra sentences.
        """if strength == "subtle":
            # Keep most of the cleaned content
            core = cleaned
        elif strength == "moderate":
            # Keep first 3–4 meaningful sentences
            core = []
            for s in cleaned:
                if len(s.split()) < 3:
                    continue
                core.append(s)
                if len(core) >= 4:
                    break
            if not core:
                core = cleaned[:4]
        else:
            # strong: compress to the most essential 2–3 sentences
            core = []
            for s in cleaned:
                if len(s.split()) < 4:
                    continue
                core.append(s)
                if len(core) >= 3:
                    break
            if not core:
                core = cleaned[:3] """
        
        core = cleaned

        return " ".join(core).strip()

    def _semantic_rewrite(
        self,
        text: str,
        emotional_state: EmotionalState,
        emotional_memory: EmotionalMemory,
        controller: Any,
        actor_name: str,
    ) -> str:
        """
        Meta‑Persona 2.0 hybrid rewrite:
          1. Rule‑based cleanup and unification into a single coherent paragraph.
          2. Optional LLM rewrite pass (if enabled in controller/context).
        """

        # Step 1: rule‑based rewrite
        rewritten = self._rule_based_rewrite(
            text,
            emotional_state,
            emotional_memory,
            controller,
            actor_name,
        )

        # Step 2: optional LLM rewrite hook
        # Convention:
        #   - controller.meta_rewrite_llm: callable or client for LLM rewriting
        #   - context.debug_flags["enable_meta_llm"] or controller.flags["enable_meta_llm"]
        try:
            enable_llm = False
            if hasattr(controller, "flags"):
                enable_llm = controller.flags.get("enable_meta_llm", False)
            if hasattr(controller, "context") and hasattr(controller.context, "debug_flags"):
                enable_llm = enable_llm or controller.context.debug_flags.get("enable_meta_llm", False)

            if enable_llm and hasattr(controller, "meta_rewrite_llm") and controller.meta_rewrite_llm:
                # The LLM should be instructed with the Continuum voice charter
                # in its own prompt/template. Here we just pass the cleaned core.
                llm_fn = controller.meta_rewrite_llm
                llm_output = llm_fn(
                    core_text=rewritten,
                    emotional_state=emotional_state.as_dict(),
                )
                if isinstance(llm_output, str) and llm_output.strip():
                    return llm_output.strip()
        except Exception as e:
            # Fail safe: never break the pipeline because of the LLM hook
            print(f"[MetaPersona] LLM rewrite hook failed: {e}")

        return rewritten

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
        actor = controller.last_final_proposal.get("actor", "unknown") if controller.last_final_proposal else "unknown"

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

        # ---------------------------------------------------------
        # Meta‑Persona 2.0: semantic rewrite before style filters
        # ---------------------------------------------------------
        if not is_storyweaver:
            rewritten_core = self._semantic_rewrite(
                actor_output,
                emotional_state,
                emotional_memory,
                controller,
                actor,
            )
        else:
            rewritten_core = actor_output

        # Style application on top of semantic rewrite
        blended = apply_style(rewritten_core, style)

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