# continuum/audio/meta_speech.py

from continuum.audio.tts_engine import tts_engine
from continuum.persona.voice_emotion import ACTOR_EMOTION
from continuum.persona.meta_voice import blend_emotion
from continuum.persona.topics import detect_topic, TOPIC_ACTOR_WEIGHTS
from continuum.persona.sentiment import (
    detect_sentiment,
    sentiment_to_emotion,
    classify_sentiment,
)
from continuum.persona.emotion_model import (
    detect_emotions,
    emotion_to_voice_modifiers,
)

META_SPEAKER = "p225"  # neutral, pleasant base voice


def _ensure_weights(weights: dict) -> dict:
    """
    Ensure we always have some weights to work with.
    If Senate weights are missing or empty, fall back to equal weights.
    """
    if not weights:
        return {actor: 1.0 for actor in ACTOR_EMOTION.keys()}
    return weights


def synthesize_meta_voice(text: str, weights: dict):
    """
    Generate long-form Meta-Persona speech using:
    - Senate emotional blending
    - Topic-aware tone shaping
    - Sentiment-based emotional tuning
    - Advanced emotion model blending
    """

    # 1) Ensure we have valid base weights
    base_weights = _ensure_weights(weights)

    # 2) Base emotional blend from Senate
    blended = blend_emotion(base_weights, ACTOR_EMOTION)

    # 3) Topic detection and actor influence
    topic = detect_topic(text)
    topic_weights = TOPIC_ACTOR_WEIGHTS.get(topic, {})

    adjusted_weights = {
        actor: base_weights.get(actor, 0.0) * topic_weights.get(actor, 1.0)
        for actor in base_weights
    }

    # 4) Re-blend with topic influence
    blended_topic = blend_emotion(adjusted_weights, ACTOR_EMOTION)

    # 5) Sentiment detection and emotional modulation
    polarity = detect_sentiment(text)
    sentiment_mod = sentiment_to_emotion(polarity)

    # 6) Advanced emotion model
    emotions = detect_emotions(text)
    emotion_mod = emotion_to_voice_modifiers(emotions)

    # 7) Combine all emotional layers
    final = {
        "speed": blended_topic["speed"]
        * sentiment_mod["speed"]
        * emotion_mod["speed"],

        "energy": blended_topic["energy"]
        * sentiment_mod["energy"]
        * emotion_mod["energy"],

        "pitch": blended_topic["pitch"]
        * sentiment_mod["pitch"]
        * emotion_mod["pitch"],
    }

    # 8) Synthesize with Coqui
    wav = tts_engine.synthesize(
        text,
        speaker=META_SPEAKER,
        speed=final["speed"],
        energy=final["energy"],
        pitch=final["pitch"],
    )

    # 9) Return audio + diagnostics
    return {
        "audio": wav,
        "topic": topic,
        "sentiment_polarity": polarity,
        "sentiment_band": classify_sentiment(polarity),
        "emotions": emotions,
        "final_modifiers": final,
    }


def speak_final_answer(controller, final_text: str):
    """
    Convenience helper: pull Senate weights from the controller
    and synthesize the Meta-Persona voice for the final answer.
    """
    proposals = getattr(controller, "last_ranked_proposals", None)

    if not proposals:
        weights = {actor: 1.0 for actor in ACTOR_EMOTION.keys()}
    else:
        weights = {
            p["actor"]: p["confidence"]
            for p in proposals
        }

    return synthesize_meta_voice(final_text, weights)