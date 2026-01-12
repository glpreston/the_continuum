# continuum/audio/timbre_backend.py


import numpy as np
import scipy.signal as signal

class TimbreBackend:
    """
    Applies acoustic shaping based on actor timbre profiles.
    This layer sits between the TTS engine and final audio output.
    """

    def __init__(self):
        pass

    # ---------------------------------------------------------
    # Public API
    # ---------------------------------------------------------
    def apply_timbre(self, wav: np.ndarray, timbre: dict | None):
        if timbre is None:
            return wav

        shaped = wav.copy()

        # Apply brightness shaping
        shaped = self._apply_brightness(shaped, timbre.get("brightness"))

        # Apply resonance shaping
        shaped = self._apply_resonance(shaped, timbre.get("resonance"))

        # Apply vocal weight (compression / gain)
        shaped = self._apply_vocal_weight(shaped, timbre.get("vocal_weight"))

        # Apply texture (noise shaping)
        shaped = self._apply_texture(shaped, timbre.get("texture"))

        # Apply smoothness (low‑pass smoothing)
        shaped = self._apply_smoothness(shaped, timbre.get("smoothness"))

        return shaped

    # ---------------------------------------------------------
    # DSP Modules
    # ---------------------------------------------------------

    def _apply_brightness(self, wav, brightness):
        if brightness == "warm_bright":
            # gentle high‑shelf boost
            return self._high_shelf(wav, gain_db=2.0)
        if brightness == "neutral_dark":
            # gentle high‑cut
            return self._low_pass(wav, cutoff=6000)
        return wav

    def _apply_resonance(self, wav, resonance):
        if resonance == "chest":
            return self._low_shelf(wav, gain_db=3.0)
        if resonance == "head":
            return self._high_shelf(wav, gain_db=3.0)
        return wav

    def _apply_vocal_weight(self, wav, weight):
        if weight == "medium_heavy":
            return self._compress(wav, ratio=2.0)
        if weight == "light":
            return self._compress(wav, ratio=1.1)
        return wav

    def _apply_texture(self, wav, texture):
        if texture and texture > 0:
            noise = np.random.normal(0, texture * 0.005, len(wav))
            return wav + noise
        return wav

    def _apply_smoothness(self, wav, smoothness):
        if smoothness and smoothness > 0.8:
            return self._low_pass(wav, cutoff=8000)
        return wav

    # ---------------------------------------------------------
    # DSP Helpers
    # ---------------------------------------------------------

    def _low_pass(self, wav, cutoff):
        b, a = signal.butter(4, cutoff / 24000, btype="low")
        return signal.lfilter(b, a, wav)

    def _high_shelf(self, wav, gain_db):
        # simple high‑shelf approximation
        factor = 10 ** (gain_db / 20)
        fft = np.fft.rfft(wav)
        freqs = np.fft.rfftfreq(len(wav), 1 / 48000)
        fft[freqs > 4000] *= factor
        return np.fft.irfft(fft)

    def _low_shelf(self, wav, gain_db):
        factor = 10 ** (gain_db / 20)
        fft = np.fft.rfft(wav)
        freqs = np.fft.rfftfreq(len(wav), 1 / 48000)
        fft[freqs < 300] *= factor
        return np.fft.irfft(fft)

    def _compress(self, wav, ratio):
        return np.tanh(wav * ratio)