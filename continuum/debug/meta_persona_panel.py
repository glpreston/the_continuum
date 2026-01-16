# continuum/debug/meta_persona_panel.py

from dataclasses import dataclass
from typing import Dict, Any


@dataclass
class MetaPersonaDebugPanel:
    """
    Displays a structured, human-readable snapshot of MetaPersona’s
    emotional state, rewrite parameters, and voiceprint alignment.
    """

    def render(
        self,
        emotional_state,
        emotional_memory,
        style_vector: Dict[str, float],
        memory_mods: Dict[str, float],
        dominant: str,
        voiceprint_loader,
        validator_report,
    ) -> str:

        state_dict = emotional_state.as_dict()

        pacing_rules = voiceprint_loader.get_pacing_rules()
        metaphor_rules = voiceprint_loader.get_metaphor_density_rules()
        forbidden = voiceprint_loader.get_forbidden_elements()

        lines = []

        lines.append("\n================ META‑PERSONA DEBUG PANEL ================\n")

        # -----------------------------------------------------
        # Emotional State
        # -----------------------------------------------------
        lines.append("EMOTIONAL STATE")
        lines.append(f"  Dominant Emotion: {dominant}")
        lines.append(f"  Raw Vector: {state_dict}")
        lines.append(f"  Volatility: {emotional_memory.volatility:.3f}")
        lines.append(f"  Confidence: {emotional_memory.confidence:.3f}")
        lines.append("")

        # -----------------------------------------------------
        # Memory Modifiers
        # -----------------------------------------------------
        lines.append("MEMORY MODIFIERS")
        for k, v in memory_mods.items():
            lines.append(f"  {k}: {v:.3f}")
        lines.append("")

        # -----------------------------------------------------
        # ARIA Style Vector
        # -----------------------------------------------------
        lines.append("ARIA STYLE VECTOR")
        for k, v in style_vector.items():
            lines.append(f"  {k}: {v:.3f}")
        lines.append("")

        # -----------------------------------------------------
        # Voiceprint Parameters
        # -----------------------------------------------------
        lines.append("VOICEPRINT PARAMETERS")
        lines.append(f"  Pacing Rules: {pacing_rules}")
        lines.append(f"  Metaphor Density: {metaphor_rules}")
        lines.append(f"  Forbidden Elements: {forbidden}")
        lines.append("")

        # -----------------------------------------------------
        # Validator Report
        # -----------------------------------------------------
        if validator_report:
            lines.append("VOICEPRINT VALIDATION")
            lines.append(f"  Overall: {validator_report.overall}")
            lines.append(f"  Tone: {validator_report.tone}")
            lines.append(f"  Pacing: {validator_report.pacing}")
            lines.append(f"  Density: {validator_report.density}")
            lines.append(f"  Signature Phrasing: {validator_report.signature_phrasing}")
            lines.append(f"  Forbidden Elements: {validator_report.forbidden_elements}")
            lines.append(f"  Metaphor Density: {validator_report.metaphor_density}")
            lines.append(f"  Grounding: {validator_report.grounding}")
            lines.append(f"  Softness/Crispness: {validator_report.softening_crispness_balance}")
            lines.append("")
            lines.append("  DETAILS")
            for k, v in validator_report.details.items():
                lines.append(f"    {k}: {v}")
            lines.append("")

        lines.append("==========================================================\n")

        return "\n".join(lines)