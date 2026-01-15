# continuum/emotion/actor_profiles.py

from typing import Dict

ActorProfile = Dict[str, float]

ACTOR_MODULATION_PROFILES: Dict[str, ActorProfile] = {
    # Analyst: high structure, moderate assertiveness, low creativity
    "senate_analyst": {
        "warmth": 0.0,
        "creativity": -0.2,
        "assertiveness": +0.3,
        "structure": +0.6,
        "verbosity": -0.1,
    },

    # Architect: very high structure, moderate assertiveness, low verbosity
    "senate_architect": {
        "warmth": -0.1,
        "creativity": -0.1,
        "assertiveness": +0.2,
        "structure": +0.8,
        "verbosity": -0.2,
    },

    # Storyweaver: high creativity, high warmth, higher verbosity
    "senate_storyweaver": {
        "warmth": +0.3,
        "creativity": +0.7,
        "assertiveness": -0.1,
        "structure": -0.1,
        "verbosity": +0.4,
    },

    # Synthesizer: balanced, warm, moderately structured
    "senate_synthesizer": {
        "warmth": +0.2,
        "creativity": +0.2,
        "assertiveness": +0.1,
        "structure": +0.3,
        "verbosity": +0.1,
    },
}