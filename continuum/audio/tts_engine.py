from TTS.api import TTS
import torch

class CoquiEngine:
    def __init__(self):
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.model_name = "tts_models/en/vctk/vits"
        self.tts = TTS(self.model_name).to(self.device)
        self.speakers = self.tts.speakers

    def synthesize(self, text: str, speaker: str, speed=1.0, energy=1.0, pitch=1.0):
        wav = self.tts.tts(
            text=text,
            speaker=speaker,
            speed=speed,
            energy=energy,
            pitch=pitch,
        )
        return wav

# 🔥 Global instance used by all panels
tts_engine = CoquiEngine()