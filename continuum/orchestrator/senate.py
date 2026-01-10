from typing import List, Dict, Any
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer


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
        proposals = []

        for actor in self.actors:

            # Skip disabled actors (J7)
            if not controller.actor_settings.get(actor.name, {}).get("enabled", True):
                continue

            try:
                proposal = actor.propose(context, message)

                # Apply actor weight (J7)
                weight = controller.actor_settings.get(actor.name, {}).get("weight", 1.0)
                proposal["confidence"] = proposal.get("confidence", 0) * weight

                # J9 Layer 3: reasoning summary
                proposal["summary"] = actor.summarize_reasoning(proposal)

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
        controller.context.debug_flags["raw_proposals"] = proposals  # J9

        # 2. Filter proposals
        filtered = self.filter_proposals(proposals)
        controller.context.debug_flags["filtered_proposals"] = filtered  # J9

        # 3. Rank proposals
        ranked = self.rank_proposals(filtered)

        # 4. J11: Similarity matrix
        similarity = self.compute_similarity_matrix(ranked)
        controller.context.debug_flags["similarity_matrix"] = similarity

        return ranked