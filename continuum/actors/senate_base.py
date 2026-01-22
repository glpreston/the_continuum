# continuum/actors/senate_base.py

class SenateBase:
    """
    Shared base class for all Senate wrappers.
    Provides common utilities like summarize_reasoning().
    """

    def __init__(self, llm_actor, name: str):
        self.llm_actor = llm_actor
        self.name = name

    def summarize_reasoning(self, proposal):
        """
        Delegate reasoning summary to the underlying LLM actor.
        This is required because Senate calls actor.summarize_reasoning().
        """
        return self.llm_actor.summarize_reasoning(proposal)