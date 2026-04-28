"""
Data models for unified progress tracking.
"""

from __future__ import annotations

import time
from collections import deque
from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class TaskStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CACHED = "cached"
    SKIPPED = "skipped"


class TaskPriority(Enum):
    LOW = 1
    NORMAL = 2
    HIGH = 3
    CRITICAL = 4


@dataclass
class TaskMetrics:
    cpu_percent: float = 0.0
    memory_mb: float = 0.0
    network_kb: float = 0.0
    disk_io_mb: float = 0.0
    custom: dict[str, Any] = field(default_factory=dict)


@dataclass
class Task:
    id: str
    description: str
    total: int
    current: int = 0
    status: TaskStatus = TaskStatus.PENDING
    priority: TaskPriority = TaskPriority.NORMAL
    parent_id: str | None = None
    children: list[str] = field(default_factory=list)
    category: str | None = None
    tool: str | None = None
    tags: list[str] = field(default_factory=list)
    start_time: float | None = None
    end_time: float | None = None
    duration_ms: float = 0.0
    metrics: TaskMetrics = field(default_factory=TaskMetrics)
    error: str | None = None
    retry_count: int = 0
    max_retries: int = 0
    cache_hit: bool = False
    cache_key: str | None = None
    fields: dict[str, Any] = field(default_factory=dict)
    history: deque[float] = field(default_factory=lambda: deque(maxlen=20))

    @property
    def percent(self) -> float:
        if self.total == 0:
            return 100.0 if self.status in {TaskStatus.COMPLETED, TaskStatus.CACHED} else 0.0
        return min(100.0, (self.current / self.total) * 100)

    @property
    def elapsed_seconds(self) -> float:
        if not self.start_time:
            return 0.0
        end_time = self.end_time or time.time()
        return max(0.0, end_time - self.start_time)

    @property
    def eta_seconds(self) -> float:
        if self.status == TaskStatus.COMPLETED or self.total == 0 or self.current == 0:
            return 0.0
        rate = self.current / self.elapsed_seconds if self.elapsed_seconds > 0 else 0
        if rate <= 0:
            return float("inf")
        remaining = self.total - self.current
        return remaining / rate

    @property
    def speed(self) -> float:
        if self.elapsed_seconds == 0:
            return 0.0
        return self.current / self.elapsed_seconds

    @property
    def throughput(self) -> str:
        s = self.speed
        if s >= 1:
            return f"{s:.2f}/s"
        return f"{s * 60:.2f}/m"

    @staticmethod
    def format_time(seconds: float) -> str:
        if seconds == float("inf"):
            return "∞"
        if seconds <= 0:
            return "0s"
        if seconds < 60:
            return f"{seconds:.1f}s"
        minutes = seconds / 60
        if minutes < 60:
            return f"{minutes:.1f}m"
        hours = minutes / 60
        return f"{hours:.1f}h"

    @property
    def eta_formatted(self) -> str:
        return self.format_time(self.eta_seconds)

    @property
    def elapsed_formatted(self) -> str:
        return self.format_time(self.elapsed_seconds)

    def add_history_point(self, value: float | None = None) -> None:
        self.history.append(self.percent if value is None else value)

    def get_sparkline(self, width: int = 10) -> str:
        if not self.history or len(self.history) < 2:
            return "─" * width
        block_chars = ["▁", "▂", "▃", "▄", "▅", "▆", "▇", "█"]
        values = list(self.history)[-width:]
        min_val = min(values)
        max_val = max(values)
        if max_val == min_val:
            return block_chars[len(block_chars) // 2] * len(values)
        sparkline = []
        for value in values:
            normalized = (value - min_val) / (max_val - min_val)
            index = int(normalized * (len(block_chars) - 1))
            sparkline.append(block_chars[index])
        return "".join(sparkline)


@dataclass
class CategoryStats:
    name: str
    total: int = 0
    completed: int = 0
    passed: int = 0
    failed: int = 0
    skipped: int = 0
    cached: int = 0

    @property
    def running(self) -> int:
        return self.total - self.completed

    @property
    def pass_rate(self) -> float:
        if self.completed == 0:
            return 0.0
        return (self.passed / self.completed) * 100

    @property
    def cache_hit_rate(self) -> float:
        if self.total == 0:
            return 0.0
        return (self.cached / self.total) * 100


__all__ = ["CategoryStats", "Task", "TaskMetrics", "TaskPriority", "TaskStatus"]
