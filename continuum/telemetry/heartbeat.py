#continuum/telemetry/heartbeat.py
while state in {STARTUP_WARMUP, ACTIVE_MONITORING}:
    probe_all_nodes()
    sleep(config.heartbeat_interval_seconds)