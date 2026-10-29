"""
Resilience primitives for external calls (timeouts, retries, simple circuit breaker).
Used by scrapers and optional LLM providers — not for in-process DB calls.
"""
from __future__ import annotations
import logging
import random
import time
from dataclasses import dataclass, field
from typing import Callable, TypeVar

logger = logging.getLogger("priceloop.resilience")
T = TypeVar("T")


@dataclass
class CircuitBreaker:
    """Open circuit after `failure_threshold` failures; half-open after `recovery_seconds`."""
    name: str
    failure_threshold: int = 5
    recovery_seconds: float = 30.0
    failures: int = 0
    opened_at: float | None = None
    state: str = "closed"  # closed | open | half_open

    def allow(self) -> bool:
        if self.state == "closed":
            return True
        if self.state == "open":
            if self.opened_at and (time.time() - self.opened_at) >= self.recovery_seconds:
                self.state = "half_open"
                logger.info("circuit half_open name=%s", self.name)
                return True
            return False
        return True  # half_open: allow one probe

    def record_success(self) -> None:
        self.failures = 0
        self.state = "closed"
        self.opened_at = None

    def record_failure(self) -> None:
        self.failures += 1
        if self.failures >= self.failure_threshold:
            self.state = "open"
            self.opened_at = time.time()
            logger.warning("circuit open name=%s failures=%s", self.name, self.failures)


def retry_with_backoff(
    fn: Callable[[], T],
    *,
    max_attempts: int = 3,
    base_delay: float = 0.5,
    max_delay: float = 8.0,
    retry_on: tuple[type[Exception], ...] = (Exception,),
    jitter: bool = True,
) -> T:
    last: Exception | None = None
    for attempt in range(1, max_attempts + 1):
        try:
            return fn()
        except retry_on as exc:
            last = exc
            if attempt >= max_attempts:
                break
            delay = min(max_delay, base_delay * (2 ** (attempt - 1)))
            if jitter:
                delay *= 0.5 + random.random()
            logger.warning("retry attempt=%s delay=%.2f error=%s", attempt, delay, type(exc).__name__)
            time.sleep(delay)
    assert last is not None
    raise last
