"""Lightweight process metrics (no Prometheus dependency required)."""
from __future__ import annotations
import threading
import time
from collections import defaultdict
from typing import Any

_lock = threading.Lock()
_counters: dict[str, int] = defaultdict(int)
_started = time.time()


def incr(name: str, n: int = 1) -> None:
    with _lock:
        _counters[name] += n


def snapshot() -> dict[str, Any]:
    with _lock:
        counts = dict(_counters)
    return {
        "uptime_seconds": round(time.time() - _started, 1),
        "counters": counts,
    }
