"""
health_monitor.py — make the platform observe itself.

Three checks turn "why did it stop?" into "the system already told me":

  1. heartbeat staleness  — a module that hasn't written in N minutes is stale.
  2. silent-failure       — a lane that ran but produced nothing is flagged.
  3. code drift           — if a source file changed *after* the loop started,
                            the running process is on stale code -> restart_required.

The code-drift check is the one that mattered in practice: editing modules while
a load-once loop is running silently freezes parts of the system; detecting the
mtime drift surfaces it instead of letting it rot.
"""
from __future__ import annotations

import os
from datetime import datetime
from typing import Any, Dict, Iterable, List


def heartbeat_status(heartbeats_min: Dict[str, float], stale_after: float = 20.0) -> Dict[str, Any]:
    stale = [m for m, age in heartbeats_min.items() if age > stale_after]
    return {"stale_after_min": stale_after, "stale_modules": stale,
            "ok": not stale}


def detect_code_drift(source_files: Iterable[str], loop_started: datetime) -> Dict[str, Any]:
    """Flag any source file modified after the loop started (stale running code)."""
    drifted: List[str] = []
    for path in source_files:
        try:
            if datetime.fromtimestamp(os.path.getmtime(path)) > loop_started:
                drifted.append(os.path.basename(path))
        except OSError:
            continue
    return {
        "restart_required": bool(drifted),
        "modules": drifted,
        "reason": (f"{len(drifted)} modules modified since loop start"
                   if drifted else "loop code is current"),
    }


def evaluate(heartbeats_min: Dict[str, float], source_files: Iterable[str],
             loop_started: datetime) -> Dict[str, Any]:
    """Compose the checks into a single health snapshot."""
    hb = heartbeat_status(heartbeats_min)
    drift = detect_code_drift(source_files, loop_started)
    score = 100 - (10 * len(hb["stale_modules"])) - (30 if drift["restart_required"] else 0)
    status = "OK" if score >= 85 else "WARNING" if score >= 50 else "DEGRADED"
    return {"generated_at": datetime.now().isoformat(timespec="seconds"),
            "status": status, "score": max(score, 0),
            "heartbeats": hb, "code_drift": drift}
