# continuum/orchestrator/model_selector.py
# Simple Phase‑4 Python Model Selector

from continuum.core.logger import log_info, log_error



class ModelSelector:
    """
    Python-side model selector.
    Uses:
      - actor profile defaults
      - registry node availability
      - optional TS selector fallback
    """

    def __init__(self, controller):
        self.controller = controller

    def select_model(self, actor_name: str, requested_model: str = None, **kwargs):
        """
        Decide which model an actor should use.
        Priority:
          1. Explicit requested_model
          2. ActorProfile.model_name
          3. fallback_model

        Extra kwargs (e.g. role=...) are accepted for compatibility and ignored here.
        """

        registry = self.controller.registry

        try:
            profile = registry.actor_profiles.get(actor_name)
            if not profile:
                log_error(f"[ModelSelector] No profile for actor '{actor_name}'")
                return None

            # 1. Explicit request
            if requested_model:
                return requested_model

            # 2. Actor default
            if profile.model_name:
                return profile.model_name

            # 3. Fallback
            return profile.fallback_model

        except Exception as e:
            log_error(f"[ModelSelector] Error selecting model: {e}")
            return None


class old_ModelSelector:
    """
    Python-side model selector.
    Uses:
      - actor profile defaults
      - registry node availability
      - optional TS selector fallback
    """

    def __init__(self, controller):
        self.controller = controller

    def select_model(self, actor_name: str, requested_model: str = None):
        """
        Decide which model an actor should use.
        Priority:
          1. Explicit requested_model
          2. ActorProfile.model_name
          3. fallback_model
        """

        registry = self.controller.registry

        try:
            profile = registry.actor_profiles.get(actor_name)
            if not profile:
                log_error(f"[ModelSelector] No profile for actor '{actor_name}'")
                return None

            # 1. Explicit request
            if requested_model:
                return requested_model

            # 2. Actor default
            if profile.model_name:
                return profile.model_name

            # 3. Fallback
            return profile.fallback_model

        except Exception as e:
            log_error(f"[ModelSelector] Error selecting model: {e}")
            return None