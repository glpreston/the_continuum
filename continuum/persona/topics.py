# continuum/persona/topics.py

def detect_topic(text: str):
    text_lower = text.lower()

    for topic, keywords in TOPIC_KEYWORDS.items():
        if any(k in text_lower for k in keywords):
            return topic

    return "general"

TOPIC_KEYWORDS = {
    "technical": [
        "debug", "explain", "analyze", "code", "function", "error",
        "algorithm", "technical", "compute", "optimize"
    ],
    "creative": [
        "story", "imagine", "describe", "poem", "narrative",
        "creative", "fantasy", "dream", "character"
    ],
    "planning": [
        "plan", "structure", "organize", "outline", "roadmap",
        "steps", "process", "workflow", "design"
    ],
    "reflective": [
        "why", "meaning", "purpose", "reflect", "think about",
        "philosophy", "life", "understand"
    ],
}

TOPIC_ACTOR_WEIGHTS = {
    "technical": {
        "senate_analyst": 1.3,
        "senate_architect": 1.0,
        "senate_storyweaver": 0.8,
        "senate_synthesizer": 1.0,
    },
    "creative": {
        "senate_storyweaver": 1.3,
        "senate_synthesizer": 1.1,
        "senate_architect": 0.9,
        "senate_analyst": 0.8,
    },
    "planning": {
        "senate_architect": 1.3,
        "senate_analyst": 1.1,
        "senate_synthesizer": 1.0,
        "senate_storyweaver": 0.9,
    },
    "reflective": {
        "senate_synthesizer": 1.3,
        "senate_storyweaver": 1.1,
        "senate_architect": 1.0,
        "senate_analyst": 0.9,
    },
    "general": {
        "senate_architect": 1.0,
        "senate_storyweaver": 1.0,
        "senate_analyst": 1.0,
        "senate_synthesizer": 1.0,
    },
}
