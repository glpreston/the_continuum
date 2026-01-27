#continuum/db/registry/__init__.py
from .base_registry import BaseRegistry
from .routing import RoutingMixin

class ModelRegistry(BaseRegistry, RoutingMixin):
    """
    Full registry composed of:
    - BaseRegistry: loads nodes/models + lookup tables
    - RoutingMixin: scoring + best-node selection
    """
    pass