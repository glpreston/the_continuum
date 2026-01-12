
# continuum/persona/actor_voice_timbre.py

"""
Actor Acoustic Timbre Profiles
J14 — Defines the physical/acoustic qualities of each actor's voice.

These traits shape how the actor *sounds* at the TTS level:
- vocal_weight: light / medium / heavy
- brightness: bright / neutral / dark
- resonance: head / chest / mixed
- clarity: crisp / soft / smooth
- texture: 0.0–1.0 (grain / roughness)
- smoothness: 0.0–1.0 (legato / fluidity)
- emotional_range: narrow / medium / wide
"""

ACTOR_TIMBRE = {

    # ---------------------------------------------------------
    # Architect — The Structural Thinker
    # ---------------------------------------------------------
    "senate_architect": {
        "vocal_weight": "medium_heavy",
        "brightness": "neutral_dark",
        "resonance": "chest",
        "clarity": "crisp",

        # expressive micro‑traits
        "texture": 0.3,
        "smoothness": 0.8,

        # emotional boundaries
        "emotional_range": "narrow",
        "allowed_emotions": ["calm", "focused", "concerned", "confident"],
        "forbidden_emotions": ["excited", "dramatic", "high_energy", "whispery"],
    },

    # ---------------------------------------------------------
    # Storyweaver — The Narrative Intuition
    # ---------------------------------------------------------
    "senate_storyweaver": {
    "vocal_weight": "light",
    "brightness": "warm_bright",
    "resonance": "mixed",
    "clarity": "soft",

    "texture": 0.1,
    "smoothness": 0.95,

    "emotional_range": "wide",
    "allowed_emotions": ["warm", "curious", "excited", "wistful", "hopeful", "dreamy"],
    "forbidden_emotions": ["flat", "clinical", "sharp", "monotone"],
    },

    # ---------------------------------------------------------
    # Analyst — The Logical Examiner
    # ---------------------------------------------------------
    "senate_analyst": {
    "vocal_weight": "medium",
    "brightness": "neutral",
    "resonance": "head",
    "clarity": "crisp",

    "texture": 0.0,
    "smoothness": 0.6,

    "emotional_range": "narrow",
    "allowed_emotions": ["focused", "neutral", "concerned", "evaluative"],
    "forbidden_emotions": ["dramatic", "melodic", "high_energy", "wistful", "dreamy", "warm"],
    },

    # ---------------------------------------------------------
    # Synthesizer — The Integrative Mind
    # ---------------------------------------------------------
    "senate_synthesizer": {
        "vocal_weight": "medium_light",
        "brightness": "neutral_warm",
        "resonance": "mixed",
        "clarity": "smooth",

        "texture": 0.15,
        "smoothness": 0.9,

        "emotional_range": "medium",
        "allowed_emotions": ["balanced", "reflective", "warm", "thoughtful", "empathetic"],
        "forbidden_emotions": ["sharp", "aggressive", "overly_bright", "dramatic"],
    },
}