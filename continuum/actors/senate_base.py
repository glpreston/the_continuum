# continuum/actors/senate_base.py

class SenateBase:
    """
    Shared base class for all Senate wrappers.
    Provides common utilities like summarize_reasoning().
    """

    def __init__(self, name: str, llm_actor):
        self.name = name
        self.llm_actor = llm_actor

    def summarize_reasoning(self, proposal):
        return self.llm_actor.summarize_reasoning(proposal)

