# continuum/persona/meta_persona_profile.py

"""
Meta-Persona Personality Presets

These define the emotional 'signature' of the unified Meta-Persona voice.
Each preset controls:
- baseline tone (speed, energy, pitch)
- emotional reactivity (how strongly the voice responds to sentiment/emotion)
- topic reactivity (how much topic influences tone)
"""

PERSONALITY_PRESETS = {

    "warm_empathic": {
        "label": "Warm & Empathic",
        "base_speed": 0.97,
        "base_energy": 0.95,
        "base_pitch": 1.05,
        "sentiment_reactivity": 0.8,
        "emotion_reactivity": 0.9,
        "topic_reactivity": 0.7,
    },

    "calm_wise": {
        "label": "Calm & Wise",
        "base_speed": 0.90,
        "base_energy": 0.85,
        "base_pitch": 0.98,
        "sentiment_reactivity": 0.5,
        "emotion_reactivity": 0.4,
        "topic_reactivity": 0.9,
    },

    "energetic_inspiring": {
        "label": "Energetic & Inspiring",
        "base_speed": 1.10,
        "base_energy": 1.20,
        "base_pitch": 1.08,
        "sentiment_reactivity": 0.9,
        "emotion_reactivity": 0.9,
        "topic_reactivity": 0.8,
    },

    "mystical_ethereal": {
        "label": "Mystical & Ethereal",
        "base_speed": 0.92,
        "base_energy": 0.80,
        "base_pitch": 1.15,
        "sentiment_reactivity": 0.7,
        "emotion_reactivity": 0.8,
        "topic_reactivity": 0.6,
    },

    "analytical_precise": {
        "label": "Analytical & Precise",
        "base_speed": 1.05,
        "base_energy": 1.00,
        "base_pitch": 0.95,
        "sentiment_reactivity": 0.3,
        "emotion_reactivity": 0.4,
        "topic_reactivity": 1.0,
    },
}

PERSONALITY_PRESETS["narrator_mode"] = {
    "label": "Narrator Mode",
    "base_speed": 0.92,          # slower, more deliberate pacing
    "base_energy": 0.85,         # softer, more intimate delivery
    "base_pitch": 0.97,          # slightly lower, more grounded tone
    "sentiment_reactivity": 0.40, # gentle emotional arcs
    "emotion_reactivity": 0.50,   # smoother, cinematic expression
}

# Default personality
DEFAULT_PERSONALITY = "warm_empathic"