#continuum/orchestrator/controller/intent_classifier.py
INTENT_LABELS = [
    "greeting",
    "light_task",
    "chitchat",
    "analysis",
    "fact",
    "story",
    "code",
    "task",
    "big_idea",
]

INTENT_CLASSIFIER_PROMPT = """
You are an intent classifier.
Given a user message, respond with ONLY ONE of the following labels:

- greeting
- light_task
- chitchat
- fact
- analysis
- story
- code
- task
- big_idea

Definitions:

- greeting: salutations or social openings such as "hi", "hello", "good morning".
- light_task: simple factual or procedural requests that require no deep reasoning, such as "where is Timbuktu" or "give me a recipe".
- chitchat: casual conversational reactions such as "lol", "thanks", "nice", "got it".
- analysis: requests for structured reasoning, decomposition, or explanation.
- fact: direct factual questions requiring a precise answer.
- story: requests for narrative, fiction, or imaginative content.
- code: requests for programming help or code generation.
- task: actionable instructions or requests for step-by-step help.
- big_idea: broad conceptual, strategic, or visionary questions requiring multi‑actor reasoning.

Return only the label.
User message: "{user_message}"

Respond with ONLY the label. No explanation.
""".strip()


def build_intent_prompt(user_message):
    return INTENT_CLASSIFIER_PROMPT.format(user_message=user_message)