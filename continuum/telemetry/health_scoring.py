# continuum/telemetry/health_scoring.py

from datetime import datetime
from continuum.telemetry.health_score_result import HealthScoreResult
from continuum.telemetry.probe_result import ProbeResult


class HealthScoringEngine:
    """
    Computes the rolling health score for a node based on:
    - probe result (success/failure, latency)
    - previous node health state
    - telemetry configuration parameters
    """

    def __init__(self, config):
        self.config = config

    def score(self, probe: ProbeResult, previous):
        """
        previous: NodeHealth row or None if first time
        """

        # Initialize counters if first heartbeat
        failure_count = previous.failure_count if previous else 0
        success_count = previous.success_count if previous else 0
        failure_streak = previous.failure_streak if previous else 0
        success_streak = previous.success_streak if previous else 0

        # -----------------------------------------------------
        # Update counters and streaks
        # -----------------------------------------------------
        if probe.success:
            success_count += 1
            success_streak += 1
            failure_streak = 0
        else:
            failure_count += 1
            failure_streak += 1
            success_streak = 0

        # -----------------------------------------------------
        # Compute base score
        # -----------------------------------------------------
        score = 1.0
        reason = None

        # -----------------------------------------------------
        # Direct failure penalty
        # -----------------------------------------------------
        if not probe.success:
            score -= self.config.max_failure_penalty
            reason = probe.error_message or "probe failed"

        # -----------------------------------------------------
        # Latency penalty (only if success)
        # -----------------------------------------------------
        if probe.success and probe.latency_ms is not None:
            if probe.latency_ms > self.config.max_latency_ms_for_full_score:
                over = probe.latency_ms - self.config.max_latency_ms_for_full_score
                penalty = min(over / 1000.0, self.config.max_latency_penalty)
                score -= penalty
                reason = f"latency {probe.latency_ms:.1f}ms too high"

        # -----------------------------------------------------
        # Failure streak penalty
        # -----------------------------------------------------
        if failure_streak > 0:
            penalty = failure_streak * self.config.failure_streak_penalty_per_failure
            penalty = min(penalty, self.config.max_failure_penalty)
            score -= penalty

        # -----------------------------------------------------
        # Success streak bonus
        # -----------------------------------------------------
        if success_streak > 0:
            bonus = success_streak * self.config.success_streak_bonus_per_success
            bonus = min(bonus, self.config.max_success_bonus)
            score += bonus

        # -----------------------------------------------------
        # Staleness penalty
        # -----------------------------------------------------
        if previous and previous.last_heartbeat_at:
            age = (datetime.utcnow() - previous.last_heartbeat_at).total_seconds()
            if age > self.config.staleness_penalty_seconds:
                score -= 0.2
                reason = "stale heartbeat"

        # -----------------------------------------------------
        # Clamp score to [0.0, 1.0]
        # -----------------------------------------------------
        score = max(0.0, min(score, 1.0))

        # -----------------------------------------------------
        # Determine status
        # -----------------------------------------------------
        # -----------------------------------------------------
        # Determine status (DB enum values)
        # -----------------------------------------------------
        if probe.success:
            status = "online"
        elif probe.status_code in (500, 503):
            status = "offline"
        else:
            status = "degraded"
        # -----------------------------------------------------
        # Quarantine logic
        # -----------------------------------------------------
        quarantined = False

        if score < self.config.quarantine_threshold:
            quarantined = True
            reason = reason or "score below quarantine threshold"

        if previous and previous.quarantined:
            if score > self.config.recovery_threshold:
                quarantined = False
                reason = "recovered above threshold"
            else:
                quarantined = True
                reason = "still below recovery threshold"

        return HealthScoreResult(
            node_id=probe.node_id,
            health_score=score,
            status=status,
            failure_count=failure_count,
            success_count=success_count,
            failure_streak=failure_streak,
            success_streak=success_streak,
            quarantined=quarantined,
            reason=reason,
        )