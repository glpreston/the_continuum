# continuum/audio/tts_engine.py

import asyncio
import edge_tts
from continuum.audio.timbre_backend import TimbreBackend


class EdgeTTSEngine:
    def __init__(self):
        # Default neural voice (you can change this per speaker)
        self.default_voice = "en-US-AriaNeural"
        self.timbre_backend = TimbreBackend()

    async def _synthesize_async(
        self,
        text: str,
        voice: str,
        rate: float,
        pitch: float,
        timbre: dict | None,
    ):
        # Edge‑TTS expects rate/pitch as percentages
        rate_pct = f"{int((rate - 1.0) * 100)}%"
        pitch_pct = f"{int((pitch - 1.0) * 100)}%"

        communicate = edge_tts.Communicate(
            text=text,
            voice=voice,
            rate=rate_pct,
            pitch=pitch_pct,
        )

        audio_chunks = []
        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                audio_chunks.append(chunk["data"])

        wav = b"".join(audio_chunks)

        # Apply timbre shaping (your backend)
        wav = self.timbre_backend.apply_timbre(wav, timbre)
        return wav

    def synthesize(
        self,
        text: str,
        speaker: str = None,
        speed: float = 1.0,
        energy: float = 1.0,   # Edge‑TTS doesn't use energy, but we keep the API stable
        pitch: float = 1.0,
        timbre: dict | None = None,
    ):
        """
        Windows‑friendly neural TTS engine using Edge‑TTS.
        Fully compatible with the original CoquiEngine API.
        """

        # Map your speaker names to neural voices if you want
        voice = speaker or self.default_voice

        # Log timbre metadata (same behavior as before)
        if timbre:
            print("TIMBRE PROFILE:", timbre)

        # Run async TTS inside sync API
        return asyncio.run(
            self._synthesize_async(
                text=text,
                voice=voice,
                rate=speed,
                pitch=pitch,
                timbre=timbre,
            )
        )


# 🔥 Global instance used by all panels
tts_engine = EdgeTTSEngine()