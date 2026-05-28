# Self-Healing & Observability

"Autonomous" is only trustworthy if the system can notice its own failures. The
platform runs three checks every cycle (`src/health_monitor.py`).

## 1. Heartbeat staleness
Each module records when it last did work. A module silent for longer than the
threshold (default 20 min) is flagged `stale` — surfaced, not hidden.

## 2. Silent-failure detection
A lane that *ran* but produced nothing is suspicious. `lane.run_lane` contains
exceptions as failed results so they show up in state instead of vanishing.

## 3. Code-drift detection (the important one)
A load-once loop imports its modules at startup and never reloads them. If you
edit a source file *while the loop is running*, the process keeps executing the
old code and parts of the telemetry can silently freeze.

`detect_code_drift` compares each source file's mtime to the loop start time and
raises `restart_required` when anything changed:

```json
{
  "restart_required": true,
  "modules": ["futures_lane.py", "execution_analytics.py", "system_summary.py"],
  "reason": "5 modules modified since loop start"
}
```

### Real incident
This check caught exactly that situation in practice: modules were edited under a
running loop, telemetry froze, and the monitor flagged `restart_required`. A
clean restart (single-instance lock cleared, state verified uncorrupted via the
atomic store) resolved it with zero data loss — **the system caught its own
problem before a human did.**

## Health snapshot
`health_monitor.evaluate(...)` composes the three checks into a single
`{status, score, ...}` snapshot (see `observability/sample_ecosystem_health.json`).
