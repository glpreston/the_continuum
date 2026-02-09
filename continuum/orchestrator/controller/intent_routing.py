#continuum/orchestrator/controller/intent_routing.py
INTENT_TO_ACTORS = {
    # Greeter owns the lightweight band
    "greeting": ["Greeter"],
    "light_task": ["Greeter"],
    "chitchat": ["Greeter"],

    # Analyst handles precise factual questions
    "fact": ["Analyst"],

    # Architect + Analyst handle structured reasoning
    "analysis": ["Architect", "Analyst"],

    # Storyweaver handles narrative requests
    "story": ["Storyweaver"],

    # Synthesizer handles code
    "code": ["Synthesizer"],

    # Architect handles procedural tasks
    "task": ["Architect"],

    # Big ideas get multi‑actor reasoning
    "big_idea": ["Architect", "Analyst", "Storyweaver"],
}