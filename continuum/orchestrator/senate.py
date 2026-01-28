#continuum/orchestrator/senate.py
from typing import List, Dict, Any
from sklearn.feature_extraction.text import TfidfVectorizer
from concurrent.futures import ThreadPoolExecutor, as_completed
from continuum.persona.topics import detect_topic, TOPIC_ACTOR_WEIGHTS
from continuum.core.logger import log_info, log_debug, log_error


class Senate:
    """
    Phase‑4 Senate: gathers proposals from all actors, filters, ranks,
    computes similarity, and returns ranked proposals.
    """

    def __init__(self, actors: List[Any]):
        self.actors = actors
        log_error("🔥🔥🔥 SENATE.__init__() CALLED 🔥🔥🔥", phase="senate")
        log_debug(f"[SENATE] Initialized with actors: {[a.name for a in actors]}", phase="senate")

    # ---------------------------------------------------------
    # COLLECT PROPOSALS (Phase‑4)
    # ---------------------------------------------------------


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
    ) -> List[Dict[str, Any]]:

        proposals: List[Dict[str, Any]] = []

        log_error("🔥🔥🔥 ENTERED gather_proposals() 🔥🔥🔥", phase="senate")
        log_info("[SENATE] Gathering proposals from actors (parallel mode)", phase="senate")

        # ---------------------------------------------------------
        # PARALLEL EXECUTION OF ACTORS
        # ---------------------------------------------------------
        with ThreadPoolExecutor(max_workers=len(self.actors)) as executor:

            future_map = {}

            for actor in self.actors:

                # Skip disabled actors
                if not controller.actor_settings.get(actor.name, {}).get("enabled", True):
                    log_debug(f"[SENATE] Actor {actor.name} is disabled — skipping", phase="senate")
                    continue

                log_debug(f"[SENATE] Submitting {actor.name} to executor", phase="senate")

                future = executor.submit(
                    actor.propose,
                    context=context,
                    message=message,
                    controller=controller,
                    memory=memory,
                    emotional_state=emotional_state,
                    emotional_memory=emotional_memory,
                    voiceprint=voiceprint,
                    metadata=metadata,
                    telemetry=telemetry,
                )

                future_map[future] = actor

            # ---------------------------------------------------------
            # COLLECT RESULTS AS THEY COMPLETE
            # ---------------------------------------------------------
            for future in as_completed(future_map):
                actor = future_map[future]

                try:
                    proposal = future.result()

                    # Normalize non-dict proposals into dict form
                    if isinstance(proposal, str):
                        proposal = {
                            "actor": actor.name,
                            "content": proposal,
                            "confidence": 1.0,
                            "metadata": {},
                        }

                    if not isinstance(proposal, dict):
                        raise TypeError(
                            f"Proposal from {actor.name} is not a dict or str: {type(proposal)}"
                        )

                    log_debug(f"[SENATE] Raw proposal from {actor.name}: {proposal}", phase="senate")
                    log_error(f"[FORENSICS] Senate received proposal type={type(proposal)} value={repr(proposal)}", phase="senate")

                    # Ensure metadata exists
                    metadata_obj = proposal.get("metadata") or {}
                    proposal["metadata"] = metadata_obj

                    # Apply actor weight
                    weight = controller.actor_settings.get(actor.name, {}).get("weight", 1.0)
                    proposal["confidence"] = proposal.get("confidence", 0) * weight

                    # Reasoning summary
                    if hasattr(actor, "summarize_reasoning"):
                        proposal["summary"] = actor.summarize_reasoning(proposal)
                    else:
                        proposal["summary"] = "Summary unavailable."

                    # Optional audio
                    if getattr(controller, "actor_voice_mode", False):
                        if hasattr(actor, "speak_proposal"):
                            proposal_audio = actor.speak_proposal(proposal["content"])
                            proposal["audio"] = proposal_audio

                    proposals.append(proposal)

                except Exception as e:
                    log_error(f"🔥🔥🔥 ERROR in actor {actor.name}: {e} 🔥🔥🔥", phase="senate")
                    proposals.append({
                        "actor": actor.name,
                        "content": None,
                        "confidence": 0.0,
                        "metadata": {
                            "type": "error",
                            "error": str(e),
                        },
                    })

        log_error(f"🔥🔥🔥 gather_proposals() COMPLETE — {len(proposals)} proposals 🔥🔥🔥", phase="senate")
        return proposals
    # ---------------------------------------------------------
    # FILTER PROPOSALS
    # ---------------------------------------------------------
    def filter_proposals(self, proposals: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        filtered = [
            p for p in proposals
            if p.get("content") and p.get("confidence", 0) > 0
        ]

        log_debug(f"[SENATE] Filtered proposals: kept {len(filtered)} of {len(proposals)}", phase="senate")
        return filtered

    # ---------------------------------------------------------
    # RANK PROPOSALS
    # ---------------------------------------------------------
    def rank_proposals(self, proposals: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        ranked = sorted(proposals, key=lambda p: p.get("confidence", 0), reverse=True)
        log_debug(f"[SENATE] Ranked proposals (top first): {ranked}", phase="senate")
        return ranked

    # ---------------------------------------------------------
    # SIMILARITY MATRIX
    # ---------------------------------------------------------
    def compute_similarity_matrix(self, proposals):
        actors = [p.get("actor", "unknown") for p in proposals]
        texts = [p.get("content", "") or "" for p in proposals]

        if len(texts) < 2:
            log_debug("[SENATE] Only one proposal — similarity matrix trivial", phase="senate")
            return {"actors": actors, "matrix": [[1.0]]}

        vectorizer = TfidfVectorizer()
        tfidf = vectorizer.fit_transform(texts)

        sim_matrix = (tfidf * tfidf.T).toarray()

        log_debug(f"[SENATE] Similarity matrix computed: {sim_matrix}", phase="senate")

        return {
            "actors": actors,
            "matrix": sim_matrix.tolist(),
        }

    # ---------------------------------------------------------
    # MAIN ENTRYPOINT (Phase‑4)
    # ---------------------------------------------------------
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
    ) -> List[Dict[str, Any]]:

        log_error("🔥🔥🔥 ENTERED Senate.deliberate() 🔥🔥🔥", phase="senate")
        log_info("[SENATE] Starting Senate.deliberate()", phase="senate")

        # ---------------------------------------------------------
        # 1. Gather proposals (Phase‑4: actors choose their own model)
        # ---------------------------------------------------------
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
        )

        controller.context.debug_flags["raw_proposals"] = proposals

        # ---------------------------------------------------------
        # 2. Filter proposals
        # ---------------------------------------------------------
        filtered = self.filter_proposals(proposals)
        controller.context.debug_flags["filtered_proposals"] = filtered

        log_error(f"🔥🔥🔥 FILTERED PROPOSALS COUNT = {len(filtered)} 🔥🔥🔥", phase="senate")

        # ---------------------------------------------------------
        # 3. Topic detection + topic-aware confidence shaping
        # ---------------------------------------------------------
        topic = detect_topic(message)
        topic_weights = TOPIC_ACTOR_WEIGHTS.get(topic, {})

        log_debug(f"[SENATE] Detected topic: {topic}", phase="senate")
        log_debug(f"[SENATE] Topic weights: {topic_weights}", phase="senate")

        for p in filtered:
            actor = p.get("actor")
            bias = topic_weights.get(actor, 1.0)
            p["confidence"] *= bias

        controller.context.debug_flags["topic"] = topic
        controller.context.debug_flags["topic_weights"] = topic_weights

        # ---------------------------------------------------------
        # 4. Rank proposals
        # ---------------------------------------------------------
        ranked = self.rank_proposals(filtered)

        # ---------------------------------------------------------
        # 5. Similarity matrix
        # ---------------------------------------------------------
        similarity = self.compute_similarity_matrix(ranked)
        controller.context.debug_flags["similarity_matrix"] = similarity

        log_error(f"🔥🔥🔥 SENATE RETURNING {len(ranked)} RANKED PROPOSALS 🔥🔥🔥", phase="senate")
        log_debug(f"[SENATE] Final ranked list: {ranked}", phase="senate")

        return ranked