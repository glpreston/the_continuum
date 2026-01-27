# aira/logging.py

from dataclasses import dataclass, asdict
from typing import Optional, Dict, Any

from continuum.core.logger import log_debug, log_error


# -----------------------------
# Metrics Data Structure
# -----------------------------

@dataclass
class RewritePassMetrics:
    pass_index: int
    original_length: int
    rewritten_length: int
    diff_ratio: float
    temperature_used: float
    early_stop_triggered: bool = False
    notes: Optional[str] = None


# -----------------------------
# Logging Helpers
# -----------------------------

def log_rewrite_pass_start(pass_index: int, temperature: float):
    log_debug(
        f"[AIRA][PASS {pass_index}] Starting rewrite pass "
        f"(temperature={temperature:.4f})"
    )


def log_rewrite_pass_end(
    pass_index: int,
    original: str,
    rewritten: str,
    diff_text: str,
    diff_ratio: float,
):
    log_debug(
        f"[AIRA][PASS {pass_index}] Completed rewrite pass\n"
        f"  original_len={len(original)}\n"
        f"  rewritten_len={len(rewritten)}\n"
        f"  diff_ratio={diff_ratio:.4f}\n"
        f"  diff:\n{diff_text}"
    )


def log_early_stop(pass_index: int, diff_ratio: float, threshold: float):
    log_debug(
        f"[AIRA][PASS {pass_index}] Early stop triggered "
        f"(diff_ratio={diff_ratio:.4f} >= threshold={threshold})"
    )


def log_safety_clamp(reason: str, pass_index: int):
    log_error(
        f"[AIRA][PASS {pass_index}] Safety clamp activated: {reason}"
    )


# -----------------------------
# Metrics Collector
# -----------------------------

class MetricsCollector:
    """
    Collects per-pass metrics for Aira's rewrite loop.
    This can later be fed into UI panels or monitoring dashboards.
    """

    def __init__(self):
        self.passes: Dict[int, RewritePassMetrics] = {}

    def record_pass(
        self,
        pass_index: int,
        original_length: int,
        rewritten_length: int,
        diff_ratio: float,
        temperature_used: float,
        early_stop: bool = False,
        notes: Optional[str] = None,
    ):
        metrics = RewritePassMetrics(
            pass_index=pass_index,
            original_length=original_length,
            rewritten_length=rewritten_length,
            diff_ratio=diff_ratio,
            temperature_used=temperature_used,
            early_stop_triggered=early_stop,
            notes=notes,
        )
        self.passes[pass_index] = metrics

        log_debug(
            f"[AIRA][PASS {pass_index}] Metrics recorded: "
            f"{asdict(metrics)}"
        )

    def export(self) -> Dict[str, Any]:
        """
        Export metrics as a dict for UI or debugging.
        """
        return {
            f"pass_{idx}": asdict(m)
            for idx, m in self.passes.items()
        }