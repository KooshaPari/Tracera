from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime


@dataclass(frozen=True)
class ProcessEvent:
    service_id: str
    process_id: str
    occurred_at: datetime = field(default_factory=datetime.utcnow)


@dataclass(frozen=True)
class ProcessStarted(ProcessEvent):
    command: str | None = None


@dataclass(frozen=True)
class ProcessStopped(ProcessEvent):
    reason: str | None = None


@dataclass(frozen=True)
class ProcessCrashed(ProcessEvent):
    reason: str
