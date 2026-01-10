# continuum/persona/sentiment.py

from textblob import TextBlob

def detect_sentiment(text: str):
    """
    Returns a sentiment polarity between -1.0 (negative) and +1.0 (positive).
    """
    blob = TextBlob(text)
    return blob.sentiment.polarity


def classify_sentiment(polarity: float):
    """
    Map raw polarity into expressive emotional bands.
    """
    if polarity <= -0.6:
        return "strong_negative"
    elif polarity <= -0.2:
        return "negative"
    elif polarity < 0.2:
        return "neutral"
    elif polarity < 0.6:
        return "positive"
    else:
        return "strong_positive"


def nonlinear_scale(value: float, factor: float = 0.5):
    """
    Compresses extremes so emotional shifts feel natural.
    """
    return 1.0 + (value - 1.0) * factor


SENTIMENT_PROFILES = {
    "strong_negative": {
        "speed": 0.85,
        "energy": 0.75,
        "pitch": 0.90,
    },
    "negative": {
        "speed": 0.92,
        "energy": 0.85,
        "pitch": 0.95,
    },
    "neutral": {
        "speed": 1.00,
        "energy": 1.00,
        "pitch": 1.00,
    },
    "positive": {
        "speed": 1.08,
        "energy": 1.12,
        "pitch": 1.05,
    },
    "strong_positive": {
        "speed": 1.15,
        "energy": 1.25,
        "pitch": 1.12,
    },
}


def sentiment_to_emotion(polarity: float):
    """
    Convert sentiment polarity into expressive emotional modifiers.
    Uses:
    - sentiment band classification
    - emotional profiles
    - nonlinear scaling for naturalness
    """
    band = classify_sentiment(polarity)
    profile = SENTIMENT_PROFILES[band]

    return {
        "speed": nonlinear_scale(profile["speed"]),
        "energy": nonlinear_scale(profile["energy"]),
        "pitch": nonlinear_scale(profile["pitch"]),
    }