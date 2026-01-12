# continuum/persona/meta_voice.py

def blend_emotion(weights, actor_emotions):
    """
    Blend emotional parameters based on actor weights.
    weights: dict of actor_name -> weight (confidence or normalized score)
    actor_emotions: dict of actor_name -> {speed, energy, pitch}
    """
    total = sum(weights.values())
    if total == 0:
        return {"speed": 1.0, "energy": 1.0, "pitch": 1.0}

    blended = {"speed": 0.0, "energy": 0.0, "pitch": 0.0}

    for actor, w in weights.items():
        emo = actor_emotions.get(actor, {})
        blended["speed"] += emo.get("speed", 1.0) * (w / total)
        blended["energy"] += emo.get("energy", 1.0) * (w / total)
        blended["pitch"] += emo.get("pitch", 1.0) * (w / total)
    
    return blended