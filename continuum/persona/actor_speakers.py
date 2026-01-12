# continuum/persona/actor_speakers.py

"""
ACTOR_SPEAKERS = {
    "senate_architect": "p225",   # calm, neutral
    "senate_storyweaver": "p240", # warm, expressive
    "senate_analyst": "p260",     # precise, masculine
    "senate_synthesizer": "p283", # smooth, balanced
}
"""

from continuum.persona.actor_voice_timbre import ACTOR_TIMBRE

ACTOR_SPEAKERS = {
    "senate_architect": {
        "speaker_id": "p225",
        "timbre": ACTOR_TIMBRE.get("senate_architect"),
    },
    "senate_storyweaver": {
        "speaker_id": "p260",
        "timbre": ACTOR_TIMBRE.get("senate_storyweaver"),
    },
    "senate_analyst": {
        "speaker_id": "p243",
        "timbre": ACTOR_TIMBRE.get("senate_analyst"),
    },
    "senate_synthesizer": {
        "speaker_id": "p231",
        "timbre": ACTOR_TIMBRE.get("senate_synthesizer"),
    },
}