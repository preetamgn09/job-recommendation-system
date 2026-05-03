"""
Lightweight metrics collection — tracks response times per endpoint.
"""

import time
from collections import defaultdict
from dataclasses import dataclass, field


@dataclass
class EndpointMetrics:
    total_requests: int = 0
    total_time_ms: float = 0.0
    min_time_ms: float = float("inf")
    max_time_ms: float = 0.0

    @property
    def avg_time_ms(self) -> float:
        if self.total_requests == 0:
            return 0.0
        return round(self.total_time_ms / self.total_requests, 2)

    def record(self, duration_ms: float):
        self.total_requests += 1
        self.total_time_ms += duration_ms
        self.min_time_ms = min(self.min_time_ms, duration_ms)
        self.max_time_ms = max(self.max_time_ms, duration_ms)

    def to_dict(self) -> dict:
        return {
            "total_requests": self.total_requests,
            "avg_time_ms": self.avg_time_ms,
            "min_time_ms": round(self.min_time_ms, 2) if self.min_time_ms != float("inf") else 0,
            "max_time_ms": round(self.max_time_ms, 2),
        }


class MetricsCollector:
    """Global metrics collector singleton."""

    def __init__(self):
        self._endpoints: dict[str, EndpointMetrics] = defaultdict(EndpointMetrics)
        self._start_time = time.time()

    def record(self, endpoint: str, duration_ms: float):
        self._endpoints[endpoint].record(duration_ms)

    def get_all(self) -> dict:
        uptime = round(time.time() - self._start_time, 1)
        return {
            "uptime_seconds": uptime,
            "endpoints": {k: v.to_dict() for k, v in self._endpoints.items()},
        }

    def get_summary(self) -> dict:
        total_reqs = sum(e.total_requests for e in self._endpoints.values())
        avg_time = 0.0
        if total_reqs > 0:
            avg_time = sum(e.total_time_ms for e in self._endpoints.values()) / total_reqs
        return {
            "total_requests": total_reqs,
            "avg_response_time_ms": round(avg_time, 2),
            "uptime_seconds": round(time.time() - self._start_time, 1),
        }


# Global instance
metrics = MetricsCollector()
