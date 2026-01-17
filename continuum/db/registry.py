# continuum/db/registry.py

from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from datetime import datetime

from continuum.db.models.nodes import Node, NodeStatus
from continuum.db.models.models import Model
from continuum.db.models.actor_profiles import ActorProfile


class ModelRegistry:
    """
    Dynamic registry of all compute nodes and their models.
    This is the Continuum's "map of the world" for distributed LLM selection.
    """

    def __init__(self, db_session: Session):
        self.db = db_session
        self.nodes: List[Node] = []
        self.models: List[Model] = []
        self.actor_profiles: Dict[str, ActorProfile] = {}

        self.refresh()

    # ---------------------------------------------------------
    # REFRESH REGISTRY FROM DATABASE
    # ---------------------------------------------------------
    def refresh(self):
        """Reload nodes, models, and actor profiles from the database."""
        self.nodes = (
            self.db.query(Node)
            .filter(Node.enabled == True)
            .all()
        )

        self.models = (
            self.db.query(Model)
            .join(Node)
            .filter(Node.enabled == True)
            .all()
        )

        profiles = self.db.query(ActorProfile).all()
        self.actor_profiles = {p.actor_name: p for p in profiles}

    # ---------------------------------------------------------
    # GET MODELS FOR A SPECIFIC NODE
    # ---------------------------------------------------------
    def get_models_for_node(self, node: Node) -> List[Model]:
        return [m for m in self.models if m.node_id == node.id]

    # ---------------------------------------------------------
    # FIND MODELS BY TAG
    # ---------------------------------------------------------
    def find_by_tag(self, tag: str) -> List[Model]:
        return [
            m for m in self.models
            if m.tags and tag in m.tags
        ]

    # ---------------------------------------------------------
    # FIND MODELS BY MULTIPLE TAGS
    # ---------------------------------------------------------
    def find_by_tags(self, tags: List[str]) -> List[Model]:
        return [
            m for m in self.models
            if m.tags and all(t in m.tags for t in tags)
        ]

    # ---------------------------------------------------------
    # FIND BEST MATCH FOR AN ACTOR
    # ---------------------------------------------------------
    def find_best_match(
        self,
        actor_name: str,
        require_online: bool = True,
        max_size_gb: Optional[float] = None,
    ) -> Optional[Model]:
        """
        Select the best model for a given actor based on:
        - actor capability profile
        - preferred tags
        - node availability
        - optional size constraints
        """

        profile = self.actor_profiles.get(actor_name)
        if not profile:
            return None

        preferred_tags = profile.preferred_tags or []
        capability = profile.capability

        # Step 1: filter by node status
        candidate_models = []
        for m in self.models:
            node = next((n for n in self.nodes if n.id == m.node_id), None)
            if not node:
                continue

            if require_online and node.status != NodeStatus.online:
                continue

            if max_size_gb and m.size_gb and m.size_gb > max_size_gb:
                continue

            candidate_models.append(m)

        # Step 2: filter by preferred tags
        if preferred_tags:
            tagged = [
                m for m in candidate_models
                if m.tags and any(t in m.tags for t in preferred_tags)
            ]
            if tagged:
                return tagged[0]

        # Step 3: fallback to capability tag
        capability_matches = [
            m for m in candidate_models
            if m.tags and capability in m.tags
        ]
        if capability_matches:
            return capability_matches[0]

        # Step 4: fallback to any available model
        return candidate_models[0] if candidate_models else None

    # ---------------------------------------------------------
    # GET NODE BY ID
    # ---------------------------------------------------------
    def get_node(self, node_id: int) -> Optional[Node]:
        return next((n for n in self.nodes if n.id == node_id), None)

    # ---------------------------------------------------------
    # MARK NODE ONLINE/OFFLINE
    # ---------------------------------------------------------
    def mark_node_status(self, node: Node, status: NodeStatus):
        node.status = status
        node.last_seen = datetime.utcnow()
        self.db.commit()
        