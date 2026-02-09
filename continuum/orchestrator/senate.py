# continuum/orchestrator/senate.py
# Phase‑5 Senate: parallel actor proposals + ranking + similarity

import time
from typing import List, Dict, Any

from concurrent.futures import ThreadPoolExecutor, as_completed
from sklearn.feature_extraction.text import TfidfVectorizer

from continuum.persona.topics import detect_topic, TOPIC_ACTOR_WEIGHTS
from continuum.core.logger import log_info, log_debug, log_error


# ============================
# SENATE CONSTANTS (Phase‑5)
# ============================

# In Phase‑6, these will move to DB‑driven config.
MIN_CONFIDENCE_THRESHOLD = 0.0  # keep all non‑error proposals
DEFAULT_CONFIDENCE = 1.0
DEFAULT_SUMMARY = "Summary unavailable."


class Senate:
    """
    Phase‑5 Senate:
      - Runs selected actors in parallel
      - Applies topic-aware confidence shaping
      - Ranks proposals
      - Computes similarity matrix
    """

    def __init__(self, actors: List[Any]):
        self.actors = actors
        log_info(
            f"[SENATE] Initialized with actors: {[a.name for a in actors]}",
            phase="senate",
        )

    # ============================================================
    # Internal helpers
    # ============================================================
    @staticmethod
    def _normalize_proposal(
        actor_name: str,
        raw_proposal: Any,
        weight: float,
        duration: float,
        routing: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Normalize any actor output into a well‑formed proposal dict.
        """
        if isinstance(raw_proposal, str):
            proposal: Dict[str, Any] = {
                "actor": actor_name,
                "content": raw_proposal,
                "confidence": DEFAULT_CONFIDENCE,
                "metadata": {},
            }
        elif isinstance(raw_proposal, dict):
            proposal = dict(raw_proposal)  # shallow copy
            proposal.setdefault("actor", actor_name)
            proposal.setdefault("content", "")
            proposal.setdefault("confidence", DEFAULT_CONFIDENCE)
            proposal.setdefault("metadata", {})
        else:
            raise TypeError(
                f"Proposal from {actor_name} is not a dict or str: {type(raw_proposal)}"
            )

        # Ensure metadata is a dict
        metadata_obj = proposal.get("metadata") or {}
        proposal["metadata"] = metadata_obj

        # Apply actor weight
        base_conf = float(proposal.get("confidence", 0.0))
        proposal["confidence"] = base_conf * float(weight)

        # Optional reasoning summary
        if "summary" not in proposal:
            proposal["summary"] = DEFAULT_SUMMARY

        # Attach routing + timing info for downstream consumers
        proposal["routing"] = routing
        proposal["duration"] = duration
        proposal["tokens"] = len(proposal.get("content") or "")

        return proposal

    # ============================================================
    # Proposal collection
    # ============================================================
    def gather_proposals(
        self,
        context,
        message: str,
        controller,
        memory,
        emotional_state,
        emotional_memory,
        voiceprint,
        metadata,
        telemetry,
        actors_to_run: List[str] | None,
    ) -> List[Dict[str, Any]]:

        proposals: List[Dict[str, Any]] = []
        actor_timings: List[Dict[str, Any]] = []

        log_info("[SENATE] Gathering proposals", phase="senate")

        # ---------------------------------------------------------
        # 1. Determine which actors to run
        # ---------------------------------------------------------
        if actors_to_run is None:
            selected_actors = self.actors
            log_debug(
                "[SENATE] actors_to_run=None → running ALL actors",
                phase="senate",
            )
        else:
            selected_actors = [a for a in self.actors if a.name in actors_to_run]
            log_debug(
                f"[SENATE] actors_to_run={actors_to_run} → selected={[a.name for a in selected_actors]}",
                phase="senate",
            )

        if not selected_actors:
            log_error("[SENATE] No actors selected for proposals", phase="senate")
            return []

        # Try to recover intent from controller (Phase‑5: controller sets this)
        intent_name = None
        last_routing = getattr(controller, "last_routing_decision", None) or {}
        if isinstance(last_routing, dict):
            intent_name = last_routing.get("intent")

        # ---------------------------------------------------------
        # 2. Parallel proposal execution
        # ---------------------------------------------------------
        with ThreadPoolExecutor(max_workers=len(selected_actors)) as executor:
            future_map: Dict[Any, Any] = {}

            for actor in selected_actors:
                if not controller.actor_settings.get(actor.name, {}).get("enabled", True):
                    log_debug(
                        f"[SENATE] Actor {actor.name} is disabled — skipping",
                        phase="senate",
                    )
                    continue

                log_debug(
                    f"[SENATE] Routing + submitting {actor.name} to executor",
                    phase="senate",
                )

                routing = controller.router.route(
                    user_text=message,
                    actor_name=actor.name,
                    extra_context={"senate": True},
                    intent_name=intent_name,
                )

                start_time = time.perf_counter()

                future = executor.submit(
                    actor.propose,
                    context=context,
                    message=message,
                    controller=controller,
                    routing=routing,
                    memory=memory,
                    emotional_state=emotional_state,
                    emotional_memory=emotional_memory,
                    voiceprint=voiceprint,
                    metadata=metadata,
                    telemetry=telemetry,
                )

                future_map[future] = (actor, start_time, routing)

            for future in as_completed(future_map):
                actor, start_time, routing = future_map[future]
                end_time = time.perf_counter()
                duration = end_time - start_time

                actor_name = actor.name
                actor_weight = controller.actor_settings.get(actor_name, {}).get(
                    "weight", 1.0
                )

                try:
                    raw_proposal = future.result()
                    proposal = self._normalize_proposal(
                        actor_name=actor_name,
                        raw_proposal=raw_proposal,
                        weight=actor_weight,
                        duration=duration,
                        routing=routing,
                    )

                    proposals.append(proposal)

                    actor_timings.append(
                        {
                            "actor": actor_name,
                            "duration": duration,
                            "tokens": proposal.get("tokens", 0),
                            "model": routing["model_selection"]["selected_model"],
                            "node": routing["node_selection"]["selected_node"]["name"],
                            "error": None,
                        }
                    )

                except Exception as e:
                    log_error(
                        f"[SENATE] Error in actor {actor_name}: {e}",
                        phase="senate",
                    )

                    proposals.append(
                        {
                            "actor": actor_name,
                            "content": None,
                            "confidence": 0.0,
                            "metadata": {
                                "type": "error",
                                "error": str(e),
                            },
                            "summary": DEFAULT_SUMMARY,
                            "routing": routing,
                            "duration": duration,
                            "tokens": 0,
                        }
                    )

                    actor_timings.append(
                        {
                            "actor": actor_name,
                            "duration": duration,
                            "tokens": 0,
                            "model": routing["model_selection"]["selected_model"],
                            "node": routing["node_selection"]["selected_node"]["name"],
                            "error": str(e),
                        }
                    )

        # Persist actor timings into controller trace
        if not hasattr(controller, "last_trace") or controller.last_trace is None:
            controller.last_trace = {}

        controller.last_trace["actor_timings"] = actor_timings

        log_info(
            f"[SENATE] gather_proposals complete — {len(proposals)} proposals",
            phase="senate",
        )
        return proposals

    # ============================================================
    # Filtering
    # ============================================================
    def filter_proposals(self, proposals: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        filtered = [
            p
            for p in proposals
            if p.get("content") is not None
            and p.get("confidence", 0.0) > MIN_CONFIDENCE_THRESHOLD
        ]

        log_debug(
            f"[SENATE] Filtered proposals: kept {len(filtered)} of {len(proposals)}",
            phase="senate",
        )
        return filtered

    # ============================================================
    # Ranking
    # ============================================================
    def rank_proposals(self, proposals: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        ranked = sorted(
            proposals,
            key=lambda p: p.get("confidence", 0.0),
            reverse=True,
        )
        log_debug(
            f"[SENATE] Ranked proposals (top first): {[p.get('actor') for p in ranked]}",
            phase="senate",
        )
        return ranked

    # ============================================================
    # Similarity matrix
    # ============================================================
    def compute_similarity_matrix(self, proposals: List[Dict[str, Any]]) -> Dict[str, Any]:
        actors = [p.get("actor", "unknown") for p in proposals]
        texts = [p.get("content", "") or "" for p in proposals]

        if len(texts) < 2:
            log_debug(
                "[SENATE] Only one proposal — similarity matrix trivial",
                phase="senate",
            )
            return {"actors": actors, "matrix": [[1.0]]}

        vectorizer = TfidfVectorizer()
        tfidf = vectorizer.fit_transform(texts)
        sim_matrix = (tfidf * tfidf.T).toarray()

        log_debug("[SENATE] Similarity matrix computed", phase="senate")

        return {
            "actors": actors,
            "matrix": sim_matrix.tolist(),
        }

    # ============================================================
    # Main entrypoint
    # ============================================================
    def deliberate(
        self,
        context,
        message: str,
        controller,
        memory,
        emotional_state,
        emotional_memory,
        voiceprint,
        metadata,
        telemetry,
        actors_to_run: List[str] | None,
    ) -> List[Dict[str, Any]]:

        log_info("[SENATE] Starting Senate.deliberate()", phase="senate")

        # 1. Gather proposals
        proposals = self.gather_proposals(
            context=context,
            message=message,
            controller=controller,
            memory=memory,
            emotional_state=emotional_state,
            emotional_memory=emotional_memory,
            voiceprint=voiceprint,
            metadata=metadata,
            telemetry=telemetry,
            actors_to_run=actors_to_run,
        )

        controller.context.debug_flags["raw_proposals"] = proposals

        # 2. Filter
        filtered = self.filter_proposals(proposals)
        controller.context.debug_flags["filtered_proposals"] = filtered

        if not filtered:
            log_info("[SENATE] No valid proposals after filtering", phase="senate")
            controller.context.debug_flags["topic"] = None
            controller.context.debug_flags["topic_weights"] = {}
            controller.context.debug_flags["similarity_matrix"] = {
                "actors": [],
                "matrix": [],
            }
            return []

        # 3. Topic detection + biasing
        topic = detect_topic(message)
        topic_weights = TOPIC_ACTOR_WEIGHTS.get(topic, {})

        log_debug(f"[SENATE] Detected topic: {topic}", phase="senate")
        log_debug(f"[SENATE] Topic weights: {topic_weights}", phase="senate")

        for p in filtered:
            actor_name = p.get("actor")
            bias = topic_weights.get(actor_name, 1.0)
            p["confidence"] *= bias

        controller.context.debug_flags["topic"] = topic
        controller.context.debug_flags["topic_weights"] = topic_weights

        # 4. Rank
        ranked = self.rank_proposals(filtered)

        # 5. Similarity
        similarity = self.compute_similarity_matrix(ranked)
        controller.context.debug_flags["similarity_matrix"] = similarity

        log_info(
            f"[SENATE] Returning {len(ranked)} ranked proposals",
            phase="senate",
        )

        return ranked