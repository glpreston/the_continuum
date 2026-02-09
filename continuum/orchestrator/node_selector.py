# continuum/orchestrator/node_selector.py


import threading
from continuum.core.logger import log_error

_NODE_SELECTOR_LOCK = threading.Lock()


class NodeSelector:
    """
    Simple node selector that delegates to the ModelRegistry.
    """

    def __init__(self, controller):
        self.controller = controller

    def select_node(self, model_name: str, **kwargs):
        """
        Return the best node for a given model, using the registry.
        Extra kwargs are accepted for compatibility and ignored here.
        """

        # --- SERIALIZE NODE SELECTION TO PREVENT DB CORRUPTION ---
        with _NODE_SELECTOR_LOCK:
            try:
                registry = self.controller.registry
                if hasattr(registry, "get_best_node_for_model"):
                    return registry.get_best_node_for_model(model_name)

                # Fallback: if no such method, just return None
                return None

            except Exception as e:
                log_error(f"[NodeSelector] Error selecting node for model '{model_name}': {e}")
                return None
