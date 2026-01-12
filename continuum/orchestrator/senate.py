# continuum/orchestrator/senate.py

from typing import List, Dict, Any
from sklearn.feature_extraction.text import TfidfVectorizer
from continuum.persona.topics import detect_topic, TOPIC_ACTOR_WEIGHTS



class Senate:
    """
    The Senate gathers proposals from all actors, filters out empty ones,
    ranks them by confidence, and forwards the strongest proposals to the Jury.
    """

    def __init__(self, actors: List[Any]):
        self.actors = actors

    # ---------------------------------------------------------
    # COLLECT PROPOSALS
    # ---------------------------------------------------------
    def gather_proposals(self, context, message: str, controller) -> List[Dict[str, Any]]:
        proposals: List[Dict[str, Any]] = []

        for actor in self.actors:
            # Skip disabled actors (J7)
            if not controller.actor_settings.get(actor.name, {}).get("enabled", True):
                continue

            try:
                # 1) Generate the proposal text + metadata
                proposal = actor.propose(context, message)

                # 2) Apply actor weight (J7)
                weight = controller.actor_settings.get(actor.name, {}).get("weight", 1.0)
                proposal["confidence"] = proposal.get("confidence", 0) * weight

                # 3) J9 Layer 3: reasoning summary
                proposal["summary"] = actor.summarize_reasoning(proposal)

                # 4) Optional: attach audio if actor voice mode is enabled
                if getattr(controller, "actor_voice_mode", False):
                    if hasattr(actor, "speak_proposal"):
                        proposal_audio = actor.speak_proposal(proposal["content"])
                        proposal["audio"] = proposal_audio

                proposals.append(proposal)

            except Exception as e:
                proposals.append({
                    "actor": actor.name,
                    "content": None,
                    "confidence": 0.0,
                    "metadata": {
                        "type": "error",
                        "error": str(e),
                    },
                })

        return proposals

    # ---------------------------------------------------------
    # FILTER PROPOSALS
    # ---------------------------------------------------------
    def filter_proposals(self, proposals: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Remove proposals with no content or zero confidence.
        """
        return [
            p for p in proposals
            if p.get("content") and p.get("confidence", 0) > 0
        ]

    # ---------------------------------------------------------
    # RANK PROPOSALS
    # ---------------------------------------------------------
    def rank_proposals(self, proposals: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Sort proposals by confidence, descending.
        """
        return sorted(proposals, key=lambda p: p.get("confidence", 0), reverse=True)

    # ---------------------------------------------------------
    # J11: SIMILARITY MATRIX
    # ---------------------------------------------------------
    def compute_similarity_matrix(self, proposals):
        """
        Computes cosine similarity between actor proposal contents.
        Returns a dict with:
          - 'actors': list of actor names
          - 'matrix': 2D list of similarity scores
        """

        actors = [p.get("actor", "unknown") for p in proposals]
        texts = [p.get("content", "") or "" for p in proposals]

        if len(texts) < 2:
            return {"actors": actors, "matrix": [[1.0]]}

        vectorizer = TfidfVectorizer()
        tfidf = vectorizer.fit_transform(texts)

        sim_matrix = (tfidf * tfidf.T).toarray()

        return {
            "actors": actors,
            "matrix": sim_matrix.tolist(),
        }

    # ---------------------------------------------------------
    # MAIN ENTRYPOINT
    # ---------------------------------------------------------
    def deliberate(self, context, message: str, controller) -> List[Dict[str, Any]]:
        """
        Full Senate pipeline:
        1. Gather proposals
        2. Filter out empty ones
        3. Rank by confidence
        4. Compute similarity matrix (J11)
        5. Return the ranked list to the Jury
        """        
        # 1. Gather proposals
        proposals = self.gather_proposals(context, message, controller)
        controller.context.debug_flags["raw_proposals"] = proposals #J(9)

        # 2. Filter proposals
        filtered = self.filter_proposals(proposals)
        controller.context.debug_flags["filtered_proposals"] = filtered #J(9)

        # ---------------------------------------------------------
        # NEW: Topic detection + topic-aware confidence shaping
        # ---------------------------------------------------------
        topic = detect_topic(message)
        topic_weights = TOPIC_ACTOR_WEIGHTS.get(topic, {})

        for p in filtered:
            actor = p.get("actor")
            bias = topic_weights.get(actor, 1.0)
            p["confidence"] *= bias

        controller.context.debug_flags["topic"] = topic
        controller.context.debug_flags["topic_weights"] = topic_weights

        # 3. Rank proposals
        ranked = self.rank_proposals(filtered)

        # 4. Similarity matrix
        similarity = self.compute_similarity_matrix(ranked)
        controller.context.debug_flags["similarity_matrix"] = similarity

        return ranked        