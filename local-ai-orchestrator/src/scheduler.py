"""
scheduler.py — decide which lanes run, when, and how often.

Lanes are independent units of work (content, video factory, futures). The
scheduler evaluates each lane against its time windows, cooldown, and priority,
then yields the run decisions. Keeping lanes independent means a failure in one
can't take down the others — the core reliability decision of the platform.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, time
from typing import Any, Dict, Iterable, List, Optional

try:
    import yaml
except Exception:  # pragma: no cover
    yaml = None


@dataclass
class Lane:
    name: str
    priority: int = 50
    windows: List[str] = field(default_factory=lambda: ["00:00-23:59"])
    cooldown_min: int = 30
    last_run: Optional[datetime] = None


def _in_window(now: time, window: str) -> bool:
    start_s, end_s = window.split("-")
    start = time(*map(int, start_s.split(":")))
    end = time(*map(int, end_s.split(":")))
    return start <= now <= end


class Scheduler:
    def __init__(self, lanes: List[Lane], tick_seconds: int = 180):
        self.lanes = lanes
        self.tick_seconds = tick_seconds

    @classmethod
    def from_config(cls, path: str) -> "Scheduler":
        if yaml is None:
            raise RuntimeError("PyYAML required to load config")
        cfg = yaml.safe_load(open(path, encoding="utf-8"))
        lanes = [Lane(name=l["name"], priority=l.get("priority", 50),
                      windows=l.get("windows", ["00:00-23:59"]),
                      cooldown_min=l.get("cooldown_min", 30))
                 for l in cfg.get("lanes", [])]
        return cls(lanes, cfg.get("scheduler", {}).get("tick_seconds", 180))

    def evaluate_once(self, now: Optional[datetime] = None) -> List[Dict[str, Any]]:
        """Return one run-decision per lane, highest priority first."""
        now = now or datetime.now()
        decisions: List[Dict[str, Any]] = []
        for lane in sorted(self.lanes, key=lambda l: -l.priority):
            eligible, reason = self._eligible(lane, now)
            decisions.append({"lane": lane.name, "eligible": eligible,
                              "priority": lane.priority, "reason": reason})
        return decisions

    def _eligible(self, lane: Lane, now: datetime):
        if not any(_in_window(now.time(), w) for w in lane.windows):
            return False, "outside time window"
        if lane.last_run is not None:
            mins = (now - lane.last_run).total_seconds() / 60
            if mins < lane.cooldown_min:
                return False, f"cooldown ({mins:.0f}/{lane.cooldown_min} min)"
        return True, "in window, cooldown elapsed"
