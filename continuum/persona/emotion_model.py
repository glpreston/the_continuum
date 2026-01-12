# continuum/persona/emotion_model.py

from transformers import pipeline

# Load a small, efficient emotion classifier
emotion_classifier = pipeline(
    "text-classification",
    model="j-hartmann/emotion-english-distilroberta-base",
    return_all_scores=True
)

def detect_emotions(text: str):
    """
    Returns a dict of emotion → score.
    Example:
    {
        "joy": 0.72,
        "sadness": 0.10,
        "anger": 0.05,
        ...
    }
    """
    results = emotion_classifier(text)[0]
    return {item["label"].lower(): item["score"] for item in results}

EMOTION_VOICE_PROFILES = {
    "joy":      {"speed": 1.12, "energy": 1.20, "pitch": 1.10},
    "sadness":  {"speed": 0.88, "energy": 0.80, "pitch": 0.95},
    "anger":    {"speed": 1.15, "energy": 1.30, "pitch": 0.95},
    "fear":     {"speed": 0.92, "energy": 0.85, "pitch": 1.05},
    "surprise": {"speed": 1.18, "energy": 1.25, "pitch": 1.15},
    "disgust":  {"speed": 0.90, "energy": 0.75, "pitch": 0.90},
}

def emotion_to_voice_modifiers(emotions: dict):
    """
    Blend emotion profiles weighted by their scores.
    """
    total = sum(emotions.values()) or 1.0

    blended = {"speed": 1.0, "energy": 1.0, "pitch": 1.0}

    for emotion, score in emotions.items():
        profile = EMOTION_VOICE_PROFILES.get(emotion)
        if not profile:
            continue

        weight = score / total

        blended["speed"]  += (profile["speed"]  - 1.0) * weight
        blended["energy"] += (profile["energy"] - 1.0) * weight
        blended["pitch"]  += (profile["pitch"]  - 1.0) * weight

    # print("EMOTION MOD:", blended)
    return blended