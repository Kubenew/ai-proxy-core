from __future__ import annotations

from dataclasses import dataclass, field
import time


@dataclass
class Backend:
    url: str
    healthy: bool = True

    active_requests: int = 0
    last_latency_ms: float = 9999.0
    error_count: int = 0

    disabled_until: float = 0.0
    last_seen: float = field(default_factory=lambda: time.time())

    def disabled(self) -> bool:
        return time.time() < self.disabled_until

    def score(self) -> float:
        penalty = self.error_count * 200.0
        concurrency = self.active_requests * 10.0
        return self.last_latency_ms + penalty + concurrency
