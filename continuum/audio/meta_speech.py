# continuum/audio/meta_speech.py

from continuum.audio.tts_engine import tts_engine
from continuum.persona.voice_emotion import ACTOR_EMOTION
from continuum.persona.actor_voice_timbre import ACTOR_TIMBRE
from continuum.persona.meta_voice import blend_emotion
from continuum.persona.topics import detect_topic, TOPIC_ACTOR_WEIGHTS
from continuum.persona.actor_voice_personality import ACTOR_VOICE_PERSONALITY
from continuum.persona.sentiment import (
    detect_sentiment,
    sentiment_to_emotion,
    classify_sentiment,
)
from continuum.persona.emotion_model import (
    detect_emotions,
    emotion_to_voice_modifiers,
)
from continuum.persona.meta_persona_profile import (
    PERSONALITY_PRESETS,
    DEFAULT_PERSONALITY,
)


META_SPEAKER = "p225"       # Meta‑Persona voice
NARRATOR_SPEAKER = "p260"   # Narrator Mode voice


# ---------------------------------------------------------
# Helpers
# ---------------------------------------------------------

def _ensure_weights(weights: dict) -> dict:
    """Ensure we always have some weights to work with."""
    if not weights:
        return {actor: 1.0 for actor in ACTOR_EMOTION.keys()}
    return weights


def _apply_personality(final_modifiers: dict, personality: dict) -> dict:
    """Apply personality shaping to the final modifiers."""

    def react(base_value, modifier, factor):
        return base_value * (1.0 + (modifier - 1.0) * factor)

    shaped = {
        "speed": react(
            final_modifiers["speed"],
            final_modifiers["speed"],
            personality["sentiment_reactivity"],
        ),
        "energy": react(
            final_modifiers["energy"],
            final_modifiers["energy"],
            personality["emotion_reactivity"],
        ),
        "pitch": react(
            final_modifiers["pitch"],
            final_modifiers["pitch"],
            personality["emotion_reactivity"],
        ),
    }

    shaped["speed"] *= personality["base_speed"]
    shaped["energy"] *= personality["base_energy"]
    shaped["pitch"] *= personality["base_pitch"]

    return shaped


def _blend_actor_voice_personality(weights: dict) -> dict:
    """Weighted blend of actor voice personalities."""
    total_weight = sum(weights.values()) or 1.0

    acc = {"speed": 0.0, "energy": 0.0, "pitch": 0.0}
    for actor, w in weights.items():
        personality = ACTOR_VOICE_PERSONALITY.get(actor)
        if personality:
            acc["speed"] += personality["speed"] * w
            acc["energy"] += personality["energy"] * w
            acc["pitch"] += personality["pitch"] * w

    return {
        "speed": acc["speed"] / total_weight,
        "energy": acc["energy"] / total_weight,
        "pitch": acc["pitch"] / total_weight,
    }


def _apply_emotional_memory(emotion_mod: dict, emotional_state: dict | None):
    """Blend long‑term emotional memory into the emotion modifiers."""
    if emotional_state is None:
        return emotion_mod

    avg_sentiment = emotional_state["avg_sentiment"]
    avg_emotions = emotional_state["avg_emotions"]

    memory_factor = 0.15
    sentiment_bias = 1.0 + (avg_sentiment * memory_factor)

    if avg_emotions:
        emotion_bias = 1.0 + (sum(avg_emotions.values()) / len(avg_emotions) * 0.1)
    else:
        emotion_bias = 1.0

    emotion_mod["energy"] *= sentiment_bias * emotion_bias
    emotion_mod["pitch"] *= sentiment_bias

    return emotion_mod


# ---------------------------------------------------------
# Main synthesis pipeline
# ---------------------------------------------------------

def synthesize_meta_voice(
    text: str,
    weights: dict,
    emotional_state: dict | None,
    personality: dict,
    speaker: str,
):
    """
    Generate long‑form Meta‑Persona or Narrator speech using:
    - Senate emotional blending
    - Topic‑aware tone shaping
    - Sentiment‑based emotional tuning
    - Advanced emotion model blending
    - Actor voice personalities
    - Dynamic emotional memory
    - Personality presets
    """

    # 1) Ensure valid weights
    base_weights = _ensure_weights(weights)

    # 1.5) Actor voice personality blend
    actor_voice = _blend_actor_voice_personality(base_weights)
    print("ACTOR VOICE:", actor_voice)
    
    # 1.6) Dominant actor timbre (for Meta‑Persona / Narrator shaping)
    dominant_actor = max(base_weights, key=base_weights.get)
    timbre = ACTOR_TIMBRE.get(dominant_actor)
    print("DOMINANT ACTOR:", dominant_actor)
    print("TIMBRE:", timbre)

    # 2) Senate emotional blend
    blended = blend_emotion(base_weights, ACTOR_EMOTION)

    # 3) Topic detection
    topic = detect_topic(text)
    topic_weights = TOPIC_ACTOR_WEIGHTS.get(topic, {})

    adjusted_weights = {
        actor: base_weights.get(actor, 0.0) * topic_weights.get(actor, 1.0)
        for actor in base_weights
    }

    # 4) Topic‑influenced blend
    blended_topic = blend_emotion(adjusted_weights, ACTOR_EMOTION)

    # 5) Sentiment shaping
    polarity = detect_sentiment(text)
    sentiment_mod = sentiment_to_emotion(polarity)

    # 6) Emotion model shaping
    emotions = detect_emotions(text)
    emotion_mod = emotion_to_voice_modifiers(emotions)

    # 6.5) Emotional memory shaping
    emotion_mod = _apply_emotional_memory(emotion_mod, emotional_state)

    # 7) Combine all layers
    raw_final = {
        "speed": blended_topic["speed"]
        * sentiment_mod["speed"]
        * emotion_mod["speed"]
        * actor_voice["speed"],

        "energy": blended_topic["energy"]
        * sentiment_mod["energy"]
        * emotion_mod["energy"]
        * actor_voice["energy"],

        "pitch": blended_topic["pitch"]
        * sentiment_mod["pitch"]
        * emotion_mod["pitch"]
        * actor_voice["pitch"],
    }

    # 8) Apply personality shaping
    final = _apply_personality(raw_final, personality)

    # 9) Synthesize audio
    wav = tts_engine.synthesize(
        text,
        speaker=speaker,
        speed=final["speed"],
        energy=final["energy"],
        pitch=final["pitch"],
        timbre=timbre,  # <-- new
    )

    # 10) Return diagnostics
    return {
        "audio": wav,
        "topic": topic,
        "sentiment_polarity": polarity,
        "sentiment_band": classify_sentiment(polarity),
        "emotions": emotions,
        "final_modifiers": final,
        "personality": personality["label"],
        "emotional_memory": emotional_state,
    }


# ---------------------------------------------------------
# Controller‑aware wrapper
# ---------------------------------------------------------

def speak_final_answer(controller, final_text: str):
    """Synthesize Meta‑Persona or Narrator speech based on controller state."""

    proposals = getattr(controller, "last_ranked_proposals", None)

    if not proposals:
        weights = {actor: 1.0 for actor in ACTOR_EMOTION.keys()}
    else:
        weights = {p["actor"]: p["confidence"] for p in proposals}

    # Emotional memory
    if hasattr(controller, "emotional_memory") and not controller.emotional_memory.is_empty():
        emotional_state = controller.emotional_memory.get_smoothed_state()
    else:
        emotional_state = None

    # Narrator Mode toggle
    if getattr(controller, "narrator_mode", False):
        personality = PERSONALITY_PRESETS["narrator_mode"]
        speaker = NARRATOR_SPEAKER
    else:
        personality = PERSONALITY_PRESETS[DEFAULT_PERSONALITY]
        speaker = META_SPEAKER

    # Synthesize
    result = synthesize_meta_voice(
        final_text,
        weights,
        emotional_state,
        personality,
        speaker,
    )

    # Update emotional memory
    if hasattr(controller, "emotional_memory"):
        controller.emotional_memory.add_event(
            sentiment_polarity=result["sentiment_polarity"],
            emotions=result["emotions"],
        )

    print("FINAL MODIFIERS:", result["final_modifiers"])

    return result