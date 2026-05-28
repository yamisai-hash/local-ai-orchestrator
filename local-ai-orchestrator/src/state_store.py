"""
state_store.py — append-only JSON state.

State is kept as plain JSON so it is human-readable and inspectable: open any
file and see exactly what the platform believed at a point in time. Writes are
atomic (write temp, then replace) so a crash mid-write can't corrupt state.
"""
from __future__ import annotations

import json
import os
import tempfile
from datetime import datetime
from typing import Any, Dict, List


def write_atomic(path: str, obj: Any) -> None:
    """Write JSON atomically: temp file then os.replace."""
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=os.path.dirname(path) or ".", suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(obj, f, indent=2, default=str)
        os.replace(tmp, path)          # atomic on the same filesystem
    finally:
        if os.path.exists(tmp):
            os.remove(tmp)


def append_event(path: str, event: Dict[str, Any], cap: int = 2000) -> List[Dict[str, Any]]:
    """Append an event to an append-only JSON log, capped to the last ``cap``."""
    log: List[Dict[str, Any]] = []
    if os.path.exists(path):
        try:
            log = json.load(open(path, encoding="utf-8"))
        except Exception:
            log = []                    # tolerate a bad file rather than crash
    event = {"ts": datetime.now().isoformat(timespec="seconds"), **event}
    log.append(event)
    log = log[-cap:]
    write_atomic(path, log)
    return log
