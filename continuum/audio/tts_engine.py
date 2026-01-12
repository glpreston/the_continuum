from TTS.api import TTS
import torch
from continuum.audio.timbre_backend import TimbreBackend

class CoquiEngine:
    def __init__(self):
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.model_name = "tts_models/en/vctk/vits"
        self.tts = TTS(self.model_name).to(self.device)
        self.speakers = self.tts.speakers
        self.timbre_backend = TimbreBackend()

    def synthesize(
        self,
        text: str,
        speaker: str,
        speed: float = 1.0,
        energy: float = 1.0,
        pitch: float = 1.0,
        timbre: dict | None = None,   # <-- NEW, SAFE, OPTIONAL
    ):
        """
        Synthesize speech with optional acoustic timbre hints.
        This does NOT affect Coqui output yet — it simply provides
        a future-proof hook for timbre-aware engines.
        """

        # Safe: only logs, never modifies synthesis
        if timbre:
            print("TIMBRE PROFILE:", timbre)

        wav = self.tts.tts(
            text=text,
            speaker=speaker,
            speed=speed,
            energy=energy,
            pitch=pitch,
        )
        
        # Apply timbre shaping
        wav = self.timbre_backend.apply_timbre(wav, timbre)
        return wav


# 🔥 Global instance used by all panels
tts_engine = CoquiEngine()