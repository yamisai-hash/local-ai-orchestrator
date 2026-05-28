"""
lane.py — the unit of work the scheduler runs.

A lane wraps a callable plus its identity. Lanes are deliberately dumb: they do
one thing, write their result to the state store, and never reach into another
lane. The example lanes here are stubs that show the contract; the real lanes
call into the content pipeline, the video factory, and the futures desk.
"""
from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Any, Callable, Dict


@dataclass
class LaneResult:
    lane: str
    ok: bool
    detail: str
    duration_ms: float


def run_lane(name: str, work: Callable[[], Dict[str, Any]]) -> LaneResult:
    """Run a lane's work safely and time it. Exceptions become a failed result,
    not a crash — that is what keeps one lane from taking down the loop."""
    t0 = time.time()
    try:
        out = work() or {}
        return LaneResult(name, True, str(out.get("detail", "ok")),
                          round((time.time() - t0) * 1000, 1))
    except Exception as e:  # contained on purpose
        return LaneResult(name, False, f"{type(e).__name__}: {e}",
                          round((time.time() - t0) * 1000, 1))


# --- example lane stubs (real versions call the other systems) ---
def content_lane() -> Dict[str, Any]:
    return {"detail": "ideated + queued 1 (manual approval)"}


def video_factory_lane() -> Dict[str, Any]:
    return {"detail": "rendered 1 reel (FFmpeg + TTS)"}


def futures_lane() -> Dict[str, Any]:
    return {"detail": "paper tick: no_trade"}
