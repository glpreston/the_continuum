# continuum/orchestrator/model_selector.py

class ModelSelector:
    def __init__(self, controller):
        self.controller = controller

    def select_model(self, message, emotional_state, context):
        # Use the actor's DB model as the default
        return self.controller.default_model
