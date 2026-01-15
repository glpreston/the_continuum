def get_emotional_tone(emotional_memory, emotional_state):
    """
    Returns a dict of emotional cues actors can use to modulate tone.
    """

    mem = emotional_memory.get_smoothed_state()

    return {
        "dominant": mem.get("dominant_emotion"),
        "confidence": mem.get("confidence"),
        "volatility": mem.get("volatility"),
        "smoothed": mem.get("smoothed_state", {}),
        "phase4": emotional_state.as_dict() if emotional_state else {},
    }