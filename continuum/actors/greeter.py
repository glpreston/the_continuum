from continuum.actors.base_llm_actor import BaseLLMActor
import os

class Greeter(BaseLLMActor):
    actor_name = "Greeter"

    def __init__(self, controller):
        prompt_file = os.path.join(
            os.path.dirname(__file__),
            "prompts",          # folder must be "prompts"
            "greeter_prompt.txt"
        )

        super().__init__(
            name="Greeter",
            prompt_file=prompt_file,
            persona="greeter",
            system_prompt="You are the Greeter actor. Keep responses short, friendly, and simple.",
            temperature=0.4,
            max_tokens=256,
            controller=controller,
        )

    def build_prompt(self, user_message: str, context: dict) -> str:
        return f"""
You are the Greeter actor in the Continuum.

Your job is to produce a short, simple proposal for greetings,
small talk, or light factual requests.

Rules:
- Keep responses brief.
- Do NOT analyze deeply.
- Do NOT use the Architect's structural style.
- Do NOT produce long explanations.
- Do NOT adopt a persona; Aira will rewrite the final output.

User message: {user_message}

Respond with a short proposal only.
"""