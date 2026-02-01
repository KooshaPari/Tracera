"""Agent and sandbox type definitions.

Adapted from atomsAgent sandbox/types.py; adds sandbox_root for local FS.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional


class SandboxStatus(str, Enum):
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
    environment: Dict[str, str] = field(default_factory=dict)
    dependencies: List[str] = field(default_factory=list)
    sandbox_root: Optional[str] = None  # set by provider for local FS
    project_id: Optional[str] = None  # optional project for DB/NATS context


@dataclass
class SandboxMetadata:
    """Sandbox metadata."""

    sandbox_id: str
    status: SandboxStatus
    created_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    vcpus: int = 4
    memory_mb: int = 8192
    timeout_seconds: int = 600
    sandbox_root: Optional[str] = None  # path for local FS
    error: Optional[str] = None


@dataclass
class ExecutionRequest:
    """Agent execution request."""

    prompt: str
    tools: List[str] = field(default_factory=list)
    config: SandboxConfig = field(default_factory=SandboxConfig)
    context: Dict[str, Any] = field(default_factory=dict)
    max_retries: int = 3


@dataclass
class ExecutionResult:
    """Agent execution result."""

    sandbox_id: str
    status: SandboxStatus
    output: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    error: Optional[str] = None
    execution_time_ms: float = 0.0
    tokens_used: int = 0
