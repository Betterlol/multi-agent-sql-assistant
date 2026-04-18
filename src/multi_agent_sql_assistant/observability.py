from __future__ import annotations

import json
import logging
import threading
from dataclasses import dataclass, field
from time import time


def build_logger(level: str = "INFO") -> logging.Logger:
    logger = logging.getLogger("multi_agent_sql_assistant")
    if logger.handlers:
        logger.setLevel(level)
        return logger

    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter("%(message)s"))
    logger.addHandler(handler)
    logger.setLevel(level)
    logger.propagate = False
    return logger


def log_event(logger: logging.Logger, level: int, event: str, **fields: object) -> None:
    payload = {"ts": round(time(), 3), "event": event, **fields}
    logger.log(level, json.dumps(payload, ensure_ascii=False))


@dataclass
class MetricsStore:
    uploads_total: int = 0
    uploads_failed: int = 0
    queries_total: int = 0
    queries_success: int = 0
    queries_failed: int = 0
    llm_enabled_queries: int = 0
    llm_fallback_queries: int = 0
    _latencies_ms: list[float] = field(default_factory=list)
    _lock: threading.Lock = field(default_factory=threading.Lock)

    def record_upload(self, success: bool) -> None:
        with self._lock:
            self.uploads_total += 1
            if not success:
                self.uploads_failed += 1

    def record_query(self, success: bool, latency_ms: float, llm_enabled: bool, llm_fallback: bool) -> None:
        with self._lock:
            self.queries_total += 1
            if success:
                self.queries_success += 1
            else:
                self.queries_failed += 1
            if llm_enabled:
                self.llm_enabled_queries += 1
            if llm_fallback:
                self.llm_fallback_queries += 1
            self._latencies_ms.append(latency_ms)
            if len(self._latencies_ms) > 5000:
                self._latencies_ms = self._latencies_ms[-5000:]

    def snapshot(self, uploads_active: int) -> dict[str, object]:
        with self._lock:
            latencies = sorted(self._latencies_ms)
            p50 = _percentile(latencies, 50)
            p95 = _percentile(latencies, 95)
            avg = round(sum(latencies) / len(latencies), 2) if latencies else 0.0

            return {
                "uploads_total": self.uploads_total,
                "uploads_failed": self.uploads_failed,
                "uploads_active": uploads_active,
                "queries_total": self.queries_total,
                "queries_success": self.queries_success,
                "queries_failed": self.queries_failed,
                "llm_enabled_queries": self.llm_enabled_queries,
                "llm_fallback_queries": self.llm_fallback_queries,
                "latency_ms": {"avg": avg, "p50": p50, "p95": p95, "samples": len(latencies)},
            }


def _percentile(data: list[float], p: int) -> float:
    if not data:
        return 0.0
    if len(data) == 1:
        return round(data[0], 2)
    rank = (len(data) - 1) * (p / 100.0)
    lower = int(rank)
    upper = min(lower + 1, len(data) - 1)
    fraction = rank - lower
    value = data[lower] + (data[upper] - data[lower]) * fraction
    return round(value, 2)
