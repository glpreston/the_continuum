# continuum/personauser_emotion_tone.py  

from continuum.emotion.state_machine import EmotionalState


def apply_user_emotion_tone(text: str, emotional_state: EmotionalState) -> str:
    state = emotional_state.as_dict()
    values = list(state.values()) or [0.0]
    max_val = max(values)
    min_val = min(values)

    if max_val - min_val < 0.02:
        dominant = "neutral"
    else:
        dominant = max(state, key=state.get)

    if dominant == "sadness":
        text = "I’m right here with you. " + text

    if dominant == "confusion":
        text = text.replace("Let’s explore", "Let’s make this clearer and explore")

    if dominant == "excitement":
        text = text.replace("Let’s", "Alright, let’s dive in and")

    if dominant == "anger":
        text = text.replace("We can keep things grounded", "We can steady the moment together")

    return text
