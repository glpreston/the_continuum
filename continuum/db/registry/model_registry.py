# continuum/db/registry/model_registry.py

from sqlalchemy import text
from .base_registry import BaseRegistry
from .routing import RoutingMixin

class ModelRegistry(BaseRegistry, RoutingMixin):

    def get_all_nodes(self):
        return self.nodes 
    
class ModelRegistry(BaseRegistry, RoutingMixin):

    def get_all_nodes(self):
        return self.nodes

    def assign_model_to_node(self, model_name: str, node_id: int):
        """
        Assigns a model to a node by inserting into model_nodes.
        Modern, ORM-aligned implementation.
        """

        # Validate model exists
        model = self.models_by_name.get(model_name)
        if not model:
            raise ValueError(f"Model '{model_name}' not found in registry.")

        # Validate node exists
        node = self.nodes_by_id.get(node_id)
        if not node:
            raise ValueError(f"Node ID {node_id} not found in registry.")

        # Insert into model_nodes (avoid duplicates)
        self.db.execute(
            text("""
                INSERT INTO model_nodes (model_id, node_id)
                VALUES (:model_id, :node_id)
                ON DUPLICATE KEY UPDATE node_id = node_id;
            """),
            {"model_id": model.id, "node_id": node_id}
        )

        self.db.commit()

        # Refresh registry lookup tables
        self.refresh()