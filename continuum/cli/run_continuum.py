"""
Command‑line interface for The Continuum.
Provides a simple interactive loop for testing the orchestrator.
"""

from __future__ import annotations
import uuid

from continuum.core.context import ContinuumContext
from continuum.orchestrator.continuum_controller import ContinuumController
from continuum.actors.base_actor import BaseActor
from continuum.config.personas import ACTOR_PROFILES


def build_default_controller() -> ContinuumController:
    """Create a controller with default actors."""
    actors = [
        BaseActor(name=actor_id, persona=profile)
        for actor_id, profile in ACTOR_PROFILES.items()
    ]
    return ContinuumController(actors)


def main() -> None:
    """Run an interactive Continuum session."""
    controller = build_default_controller()
    context = ContinuumContext(conversation_id=str(uuid.uuid4()))

    print("The Continuum is listening. Type 'exit' to quit.\n")

    while True:
        user_input = input("You: ").strip()
        if user_input.lower() in {"exit", "quit"}:
            print("Goodbye.")
            break

        result = controller.process_message(user_input)
        print(f"\nContinuum: {result}\n")


if __name__ == "__main__":
    main()