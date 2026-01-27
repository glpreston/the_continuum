# continuum/db/registry/base_registry.py
from typing import List, Dict, Optional
from sqlalchemy.orm import Session

from continuum.db.models.nodes import Node
from continuum.db.models.models import Model
from continuum.db.models.actor_profiles import ActorProfile
from continuum.db.models.model_nodes import ModelNode


class BaseRegistry:
    """
    Loads nodes, models, actor profiles, and builds lookup tables.
    """

    def __init__(self, db_session: Session):
        self.db = db_session

        self.nodes: List[Node] = []
        self.models: List[Model] = []
        self.actor_profiles: Dict[str, ActorProfile] = {}

        self.model_to_nodes: Dict[str, List[int]] = {}
        self.node_to_models: Dict[int, List[str]] = {}

        self.refresh()

    def refresh(self):
        # Load nodes
        self.nodes = (
            self.db.query(Node)
            .filter(Node.enabled == True)
            .all()
        )

        # Load models
        self.models = self.db.query(Model).all()

        # Load model-node links
        self.model_nodes = self.db.query(ModelNode).all()

        # Load actor profiles
        profiles = self.db.query(ActorProfile).all()
        self.actor_profiles = {p.actor_name: p for p in profiles}

        # Lookup tables
        self.nodes_by_id = {n.id: n for n in self.nodes}
        self.models_by_name = {m.name: m for m in self.models}

        # model → nodes
        self.model_to_nodes = {}
        for link in self.model_nodes:
            self.model_to_nodes.setdefault(link.model_name, []).append(link.node_id)

        # node → models
        self.node_to_models = {}
        for link in self.model_nodes:
            self.node_to_models.setdefault(link.node_id, []).append(link.model_name)

    def get_node(self, node_id: int) -> Optional[Node]:
        return self.nodes_by_id.get(node_id)

    def get_nodes_for_model(self, model_name: str):
        return self.model_to_nodes.get(model_name, [])

    def get_models_for_node(self, node: Node):
        return self.node_to_models.get(node.id, [])