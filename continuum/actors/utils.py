# continuum/actors/utils.py

from typing import Any


def apply_voiceprint_style(text: str, voice: Any) -> str:
    """
    Light-touch stylistic transformation based on the actor's voiceprint.

    This does NOT change the core meaning of the text.
    It gently shapes:
      - tone (via a soft preface)
      - rhythm (spacing / flow)
      - lexical palette (a subtle anchor at the end)
    """

    styled = text.strip()

    # 1. Tone hint (soft preface, first descriptor only)
    if getattr(voice, "tone", None):
        primary_tone = voice.tone.split(",")[0].strip()
        styled = f"{primary_tone} in approach, {styled[0].lower()}{styled[1:]}"

    # 2. Rhythm hint (very gentle)
    rhythm = getattr(voice, "rhythm", "").lower()
    if "deliberate" in rhythm or "slow" in rhythm:
        # Ensure clearer pauses
        styled = styled.replace(", ", ", ").replace(". ", ".  ")
    elif "flowing" in rhythm or "lyrical" in rhythm:
        # Slightly soften with connective phrasing
        if not styled.endswith(("...", "…")):
            styled += " And the idea continues to unfold."

    # 3. Lexical palette anchor (subtle, single keyword)
    palette = getattr(voice, "lexical_palette", []) or []
    if palette:
        keyword = palette[0]
        if keyword.lower() not in styled.lower():
            styled += f" This connects back to {keyword}."

    return styled

def generate_voice_preview(actor):
    """
    Generates a short sample sentence in the actor's voice.
    """
    sample = "This is how I would express an idea in my natural voice."
    return apply_voiceprint_style(sample, actor.voice)

import io
from gtts import gTTS

def generate_voice_audio(text: str):
    """
    Converts preview text into an audio clip (MP3 bytes).
    """
    audio_buffer = io.BytesIO()
    tts = gTTS(text=text, lang="en")
    tts.write_to_fp(audio_buffer)
    audio_buffer.seek(0)
    return audio_buffer