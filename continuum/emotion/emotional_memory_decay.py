# continuum/emotion/emotional_memory_decay.py

from __future__ import annotations
from typing import Dict, Any
import math
import time


def decay_value(value: float, half_life_seconds: float, dt: float) -> float:
    """
    Exponential decay function.
    After one half-life, the value is reduced by 50%.
    """
    if half_life_seconds <= 0:
        return value
    decay_factor = 0.5 ** (dt / half_life_seconds)
    return value * decay_factor


def apply_emotional_decay(memory_state: Dict[str, float],
                          last_update_ts: float,
                          half_life_seconds: float = 180.0) -> Dict[str, float]:
    """
    Apply exponential decay to each emotion in the memory state.
    Default half-life: 3 minutes (180 seconds).
    """
    now = time.time()
    dt = now - last_update_ts
    if dt <= 0:
        return memory_state

    decayed = {}
    for emotion, value in memory_state.items():
        decayed[emotion] = decay_value(value, half_life_seconds, dt)

    return decayed


def apply_recovery_boost(memory_state: Dict[str, float],
                         recovery_rate: float = 0.05) -> Dict[str, float]:
    """
    Slowly push emotional memory back toward neutral over time.
    Recovery rate is small to avoid abrupt changes.
    """
    recovered = {}
    for emotion, value in memory_state.items():
        # Move slightly toward zero (neutral)
        if value > 0:
            recovered[emotion] = max(0.0, value - recovery_rate)
        else:
            recovered[emotion] = value
    return recovered


def update_emotional_memory(memory_state: Dict[str, float],
                            last_update_ts: float,
                            half_life_seconds: float = 180.0,
                            recovery_rate: float = 0.05) -> Dict[str, float]:
    """
    Step F‑3: Apply decay + recovery to emotional memory.
    This should be called once per turn.
    """
    # 1. Apply exponential decay
    decayed = apply_emotional_decay(memory_state, last_update_ts, half_life_seconds)

    # 2. Apply gentle recovery toward neutral
    recovered = apply_recovery_boost(decayed, recovery_rate)

    return recovered