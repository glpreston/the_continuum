from typing import List, Dict, Any
from sklearn.feature_extraction.text import TfidfVectorizer
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
        model,
        temperature,
        max_tokens,
        system_prompt,
        memory,
        emotional_state,
        voiceprint,
        metadata,
        telemetry,
    ) -> List[Dict[str, Any]]:

        proposals: List[Dict[str, Any]] = []

        log_error("🔥🔥🔥 ENTERED gather_proposals() 🔥🔥🔥", phase="senate")
        log_info("[SENATE] Gathering proposals from actors", phase="senate")

        for actor in self.actors:

            # Skip disabled actors
            if not controller.actor_settings.get(actor.name, {}).get("enabled", True):
                log_debug(f"[SENATE] Actor {actor.name} is disabled — skipping", phase="senate")
                continue

            try:
                # -------------------------------------------------
                # 0) Adaptive model selection
                # -------------------------------------------------
                selected_model = None

                if hasattr(controller, "select_model") and callable(controller.select_model):
                    try:
                        actor_name = actor.name
                        default_model = getattr(actor, "model_name", None)

                        log_debug(
                            f"[SENATE] Calling selector for actor={actor_name}, "
                            f"role='proposal', default_model={default_model}",
                            phase="senate",
                        )

                        selected_model = controller.select_model(
                            actor_name,
                            "proposal",
                            default_model,
                        )

                        log_debug(
                            f"[SENATE] Selector chose model '{selected_model}' for actor {actor_name}",
                            phase="senate",
                        )

                        controller.context.debug_flags[f"selected_model_{actor_name}"] = selected_model

                    except Exception as sel_err:
                        log_error(
                            f"🔥🔥🔥 ERROR in selector for actor {actor.name}: {sel_err} 🔥🔥🔥",
                            phase="senate",
                        )
                        selected_model = None

                # -------------------------------------------------
                # 1) Generate proposal (Phase‑4 signature)
                # -------------------------------------------------
                log_debug(f"[SENATE] Calling propose() on {actor.name}", phase="senate")

                proposal = actor.propose(
                    context=context,
                    message=message,
                    controller=controller,
                    model=selected_model or model,
                    temperature=temperature,
                    max_tokens=max_tokens,
                    system_prompt=system_prompt,
                    memory=memory,
                    emotional_state=emotional_state,
                    voiceprint=voiceprint,
                    metadata=metadata,
                    telemetry=telemetry,
                )

                log_debug(f"[SENATE] Raw proposal from {actor.name}: {proposal}", phase="senate")
                log_error(f"[FORENSICS] Senate received proposal type={type(proposal)} value={repr(proposal)}", phase="senate")

                # Ensure metadata exists
                metadata_obj = proposal.get("metadata") or {}
                proposal["metadata"] = metadata_obj

                # Attach selected model
                if selected_model is not None:
                    metadata_obj["selected_model"] = selected_model
                    metadata_obj.setdefault("model_selection", {})["source"] = "ts_selector"
                    metadata_obj["model_selection"]["actor"] = actor.name
                    metadata_obj["model_selection"]["role"] = "proposal"

                # -------------------------------------------------
                # 2) Apply actor weight
                # -------------------------------------------------
                weight = controller.actor_settings.get(actor.name, {}).get("weight", 1.0)
                proposal["confidence"] = proposal.get("confidence", 0) * weight

                # -------------------------------------------------
                # 3) Reasoning summary
                # -------------------------------------------------
                proposal["summary"] = actor.summarize_reasoning(proposal)

                # -------------------------------------------------
                # 4) Optional audio
                # -------------------------------------------------
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
        model,
        temperature,
        max_tokens,
        system_prompt,
        memory,
        emotional_state,
        voiceprint,
        metadata,
        telemetry,
    ) -> List[Dict[str, Any]]:

        log_error("🔥🔥🔥 ENTERED Senate.deliberate() 🔥🔥🔥", phase="senate")
        log_info("[SENATE] Starting Senate.deliberate()", phase="senate")

        # 1. Gather proposals
        proposals = self.gather_proposals(
            context=context,
            message=message,
            controller=controller,
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
            system_prompt=system_prompt,
            memory=memory,
            emotional_state=emotional_state,
            voiceprint=voiceprint,
            metadata=metadata,
            telemetry=telemetry,
        )

        controller.context.debug_flags["raw_proposals"] = proposals

        # 2. Filter proposals
        filtered = self.filter_proposals(proposals)
        controller.context.debug_flags["filtered_proposals"] = filtered

        log_error(f"🔥🔥🔥 FILTERED PROPOSALS COUNT = {len(filtered)} 🔥🔥🔥", phase="senate")

        # 3. Topic detection + topic-aware confidence shaping
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

        # 4. Rank proposals
        ranked = self.rank_proposals(filtered)

        # 5. Similarity matrix
        similarity = self.compute_similarity_matrix(ranked)
        controller.context.debug_flags["similarity_matrix"] = similarity

        log_error(f"🔥🔥🔥 SENATE RETURNING {len(ranked)} RANKED PROPOSALS 🔥🔥🔥", phase="senate")
        log_debug(f"[SENATE] Final ranked list: {ranked}", phase="senate")

        return ranked