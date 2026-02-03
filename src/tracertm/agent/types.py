"""Agent and sandbox type definitions.

Adapted from atomsAgent sandbox/types.py; adds sandbox_root for local FS.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import StrEnum
from typing import Any


class SandboxStatus(StrEnum):
    """Sandbox lifecycle status."""

    CREATING = "creating"
    READY = "ready"
    EXECUTING = "executing"
    COMPLETED = "completed"
    FAILED = "failed"
    CLEANING_UP = "cleaning_up"
    CLEANED = "cleaned"


@dataclass
class SandboxConfig:
    """Sandbox configuration."""

    vcpus: int = 4
    memory_mb: int = 8192
    timeout_seconds: int = 600
    max_turns: int = 10
    environment: dict[str, str] = field(default_factory=dict)
    dependencies: list[str] = field(default_factory=list)
    sandbox_root: str | None = None  # set by provider for local FS
    project_id: str | None = None  # optional project for DB/NATS context


@dataclass
class SandboxMetadata:
    """Sandbox metadata."""

    sandbox_id: str
    status: SandboxStatus
    created_at: datetime
    started_at: datetime | None = None
    completed_at: datetime | None = None
    vcpus: int = 4
    memory_mb: int = 8192
    timeout_seconds: int = 600
    sandbox_root: str | None = None  # path for local FS
    error: str | None = None


@dataclass
class ExecutionRequest:
    """Agent execution request."""

    prompt: str
    tools: list[str] = field(default_factory=list)
    config: SandboxConfig = field(default_factory=SandboxConfig)
    context: dict[str, Any] = field(default_factory=dict)
    max_retries: int = 3


@dataclass
class ExecutionResult:
    """Agent execution result."""

    sandbox_id: str
    status: SandboxStatus
    output: str
    metadata: dict[str, Any] = field(default_factory=dict)
    error: str | None = None
    execution_time_ms: float = 0.0
    tokens_used: int = 0
