# continuum/persona/actor_voice_personality.py

"""
Actor-specific voice personalities.

These define how each actor tends to "sound" emotionally:
- speed: speaking tempo bias
- energy: intensity / loudness bias
- pitch: tonal height bias
"""

ACTOR_VOICE_PERSONALITY = {
    "senate_architect": {
        "speed": 0.96,
        "energy": 0.95,
        "pitch": 0.98,
    },
    "senate_storyweaver": {
        "speed": 1.04,
        "energy": 1.08,
        "pitch": 1.05,
    },
    "senate_analyst": {
        "speed": 1.02,
        "energy": 0.92,
        "pitch": 0.96,
    },
    "senate_synthesizer": {
        "speed": 1.00,
        "energy": 1.00,
        "pitch": 1.00,
    },
}
    # Add more actors here as needed
