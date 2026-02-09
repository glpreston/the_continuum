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


def dummy_actor_config(name):
    return dict(
        name=name,
        model_name="gpt-4.1",
        fallback_model="gpt-3.5",
        personality="neutral",
        system_prompt=f"You are the {name} actor.",
        temperature=0.7,
        max_tokens=500,
        controller=None,
    )


def run_phase4_senate_test():
    print("\n=== Initializing Senate (Phase‑4) ===")

    # Build LLM actors with dummy configs
    architect = Architect(**dummy_actor_config("Architect"))
    storyweaver = Storyweaver(**dummy_actor_config("Storyweaver"))
    analyst = Analyst(**dummy_actor_config("Analyst"))
    synthesizer = Synthesizer(**dummy_actor_config("Synthesizer"))

    senate = Senate(
        actors=[
            SenateArchitect(architect),
            SenateStoryweaver(storyweaver),
            SenateAnalyst(analyst),
            SenateSynthesizer(synthesizer),
        ]
    )

    context = ContinuumContext()
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
        controller=None,
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