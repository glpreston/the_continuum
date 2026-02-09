# continuum/orchestrator/fusion_engine.py
# Phase‑5 Fusion Engine (Weighted Hybrid Fusion)

from continuum.core.logger import log_debug, log_error
import re


class FusionEngine:
    """
    Phase‑5 Fusion Engine.

    Responsibilities:
      - Combine proposals using intent‑aware fusion weights
      - Produce a single coherent fused paragraph
      - Remain model‑agnostic (Router decides model/node)
      - Accept routing metadata for future adaptive fusion
    """

    def __init__(self, controller):
        self.controller = controller

    # ---------------------------------------------------------
    # Main fusion entry point
    # ---------------------------------------------------------
    def run(self, fusion_weights, ranked_proposals, controller, routing=None):
        routing = routing or controller.last_routing_decision

        log_debug("🔥 FUSION ENGINE START (Phase‑5) 🔥", phase="fusion")

        # -----------------------------------------------------
        # 1. Extract weighted proposal texts
        # -----------------------------------------------------
        weighted_sentences = []

        for proposal in ranked_proposals:
            actor = proposal.get("actor", "Unknown")
            content = proposal.get("content", "") or ""
            weight = float(fusion_weights.get(actor, 0.0))

            # Skip actors with zero weight (e.g., Greeter on big_idea)
            if weight <= 0.0:
                continue

            log_debug(
                f"[FUSION] Actor={actor} Weight={weight:.3f} Preview={content[:60]}",
                phase="fusion",
            )

            # Split into sentences
            sentences = self._split_sentences(content)

            for s in sentences:
                weighted_sentences.append((s, weight, actor))

        if not weighted_sentences:
            log_error("[FUSION] No weighted sentences available", phase="fusion")
            return ""

        # -----------------------------------------------------
        # 2. Normalize weights
        # -----------------------------------------------------
        total_weight = sum(w for _, w, _ in weighted_sentences) or 1.0
        normalized = [(s, w / total_weight, a) for (s, w, a) in weighted_sentences]

        # -----------------------------------------------------
        # 3. Select top‑weighted sentences
        # -----------------------------------------------------
        normalized.sort(key=lambda x: x[1], reverse=True)

        # Keep top N sentences (Phase‑5 heuristic)
        TOP_N = 5
        selected = normalized[:TOP_N]

        # -----------------------------------------------------
        # 4. Merge into a single coherent paragraph
        # -----------------------------------------------------
        fused_text = " ".join(s for (s, _, _) in selected).strip()

        log_debug(f"[FUSION] Fused text (pre‑rewrite): {fused_text}", phase="fusion")
        log_debug(f"[FUSION] Routing metadata: {routing}", phase="fusion")

        log_debug("🔥 FUSION ENGINE COMPLETE 🔥", phase="fusion")
        return fused_text

    # ---------------------------------------------------------
    # Sentence splitter (simple but effective)
    # ---------------------------------------------------------
    def _split_sentences(self, text: str):
        text = text.replace("\n", " ").strip()
        parts = re.split(r"(?<=[.!?])\s+", text)
        return [p.strip() for p in parts if p.strip()]