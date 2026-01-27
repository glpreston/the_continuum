# continuum/db/registry.py

from continuum.db.registry.base_registry import BaseRegistry
from continuum.db.registry.routing import RoutingMixin


class ModelRegistry(BaseRegistry, RoutingMixin):
    """
    The unified registry class used by the rest of the system.

    It combines:
    - BaseRegistry: loading nodes, models, profiles, and lookup tables
    - RoutingMixin: scoring, ranking, and best-node selection

    This keeps the public API identical:
        reg = ModelRegistry(db)
    """

    pass