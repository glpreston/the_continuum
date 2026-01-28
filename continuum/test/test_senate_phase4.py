from continuum.orchestrator.senate import Senate
from continuum.actors.senate_architect import SenateArchitect
from continuum.actors.senate_storyweaver import SenateStoryweaver
from continuum.actors.senate_analyst import SenateAnalyst
from continuum.actors.senate_synthesizer import SenateSynthesizer

from continuum.actors.architect import Architect
from continuum.actors.storyweaver import Storyweaver
from continuum.actors.analyst import Analyst
from continuum.actors.synthesizer import Synthesizer

from continuum.core.context import ContinuumContext

import uuid


# ---------------------------------------------------------
# Dummy controller + registry for Phase‑4 Senate testing
# ---------------------------------------------------------

class DummyModelNode:
    """A fake LLM backend that returns a clean string."""
    def generate(self, prompt, temperature, max_tokens):
        return f"[DUMMY OUTPUT for prompt: {prompt[:60]}...]"
    


class DummyRegistry:
    def __init__(self):
        self.models = {}
        self.actors = {}

    def get(self, key, default=None):
        return self.models.get(key, default)


class DummyContext:
    def __init__(self):
        self.debug_flags = {}


class DummyController:
    def __init__(self):
        self.registry = DummyRegistry()
        self.context = DummyContext()
        self.actor_settings = {}
        self.actor_voice_mode = False

        # Register a fake model so BaseLLMActor can run end‑to‑end
        self.registry.models["gpt-4.1"] = type(
            "ModelInfo",
            (),
            {
                "name": "gpt-4.1",
                "node": DummyModelNode()
            }
        )()

    def select_model(self, actor_name, role, default_model):
        return default_model


# ---------------------------------------------------------
# Dummy actor config builder
# ---------------------------------------------------------

def dummy_actor_config(name, controller):
    return dict(
        name=name,
        model_name="gpt-4.1",
        fallback_model="gpt-3.5",
        personality={"role": f"{name} role", "style": "neutral"},
        system_prompt=f"You are the {name} actor.",
        temperature=0.7,
        max_tokens=500,
        controller=controller,
    )


# ---------------------------------------------------------
# Phase‑4 Senate Test
# ---------------------------------------------------------

def run_phase4_senate_test():
    print("\n=== Initializing Senate (Phase‑4) ===")

    # Shared controller for all actors AND the Senate
    shared_controller = DummyController()

    # Build LLM actors
    architect = Architect(**dummy_actor_config("Architect", shared_controller))
    storyweaver = Storyweaver(**dummy_actor_config("Storyweaver", shared_controller))
    analyst = Analyst(**dummy_actor_config("Analyst", shared_controller))
    synthesizer = Synthesizer(**dummy_actor_config("Synthesizer", shared_controller))

    # Wrap them in Senate wrappers
    senate = Senate(
        actors=[
            SenateArchitect(architect),
            SenateStoryweaver(storyweaver),
            SenateAnalyst(analyst),
            SenateSynthesizer(synthesizer),
        ]
    )

    # Senate uses the same shared controller
    controller = shared_controller

    context = ContinuumContext(conversation_id=str(uuid.uuid4()))
    message = "Explain how a city could redesign its public spaces to improve community connection."

    memory = {}
    emotional_state = {"mood": "curious", "intensity": 0.4}
    emotional_memory = {}
    voiceprint = {"style": "neutral"}
    metadata = {}
    telemetry = {}

    print("\n=== Running Senate Cycle ===")

    result = senate.deliberate(
        context=context,
        message=message,
        controller=controller,
        memory=memory,
        emotional_state=emotional_state,
        emotional_memory=emotional_memory,
        voiceprint=voiceprint,
        metadata=metadata,
        telemetry=telemetry,
    )

    print("\n=== Senate Output ===")
    print(result)

    print("\n=== Test Complete ===")


if __name__ == "__main__":
    run_phase4_senate_test()