"""Unit tests for tracertm.agent.types."""

from datetime import UTC, datetime

import pytest

from tests.test_constants import COUNT_FOUR, COUNT_TEN, COUNT_THREE
from tracertm.agent.types import (
    ExecutionRequest,
    ExecutionResult,
    SandboxConfig,
    SandboxMetadata,
    SandboxStatus,
)

pytestmark = pytest.mark.unit


class TestSandboxStatus:
    """Test SandboxStatus enum."""

    def test_status_values(self) -> None:
        assert SandboxStatus.CREATING == "creating"
        assert SandboxStatus.READY == "ready"
        assert SandboxStatus.EXECUTING == "executing"
        assert SandboxStatus.COMPLETED == "completed"
        assert SandboxStatus.FAILED == "failed"
        assert SandboxStatus.CLEANING_UP == "cleaning_up"
        assert SandboxStatus.CLEANED == "cleaned"


class TestSandboxConfig:
    """Test SandboxConfig dataclass."""

    def test_defaults(self) -> None:
        cfg = SandboxConfig()
        assert cfg.vcpus == COUNT_FOUR
        assert cfg.memory_mb == 8192
        assert cfg.timeout_seconds == 600
        assert cfg.max_turns == COUNT_TEN
        assert cfg.environment == {}
        assert cfg.dependencies == []
        assert cfg.sandbox_root is None
        assert cfg.project_id is None

    def test_project_id_optional(self) -> None:
        cfg = SandboxConfig(project_id="proj-123")
        assert cfg.project_id == "proj-123"

    def test_environment_and_dependencies(self) -> None:
        cfg = SandboxConfig(
            environment={"FOO": "bar"},
            dependencies=["dep1"],
        )
        assert cfg.environment == {"FOO": "bar"}
        assert cfg.dependencies == ["dep1"]


class TestSandboxMetadata:
    """Test SandboxMetadata dataclass."""

    def test_required_fields(self) -> None:
        now = datetime.now(UTC)
        meta = SandboxMetadata(
            sandbox_id="s1",
            status=SandboxStatus.READY,
            created_at=now,
            sandbox_root="/tmp/s1",
        )
        assert meta.sandbox_id == "s1"
        assert meta.status == SandboxStatus.READY
        assert meta.created_at == now
        assert meta.sandbox_root == "/tmp/s1"
        assert meta.started_at is None
        assert meta.completed_at is None
        assert meta.error is None

    def test_default_vcpus_memory(self) -> None:
        now = datetime.now(UTC)
        meta = SandboxMetadata(
            sandbox_id="s1",
            status=SandboxStatus.READY,
            created_at=now,
        )
        assert meta.vcpus == COUNT_FOUR
        assert meta.memory_mb == 8192
        assert meta.timeout_seconds == 600


class TestExecutionRequest:
    """Test ExecutionRequest dataclass."""

    def test_minimal(self) -> None:
        req = ExecutionRequest(prompt="Hello")
        assert req.prompt == "Hello"
        assert req.tools == []
        assert req.max_retries == COUNT_THREE
        assert req.context == {}

    def test_with_tools_and_config(self) -> None:
        cfg = SandboxConfig(project_id="p1")
        req = ExecutionRequest(
            prompt="Run",
            tools=["read_file"],
            config=cfg,
            context={"key": "val"},
        )
        assert req.tools == ["read_file"]
        assert req.config.project_id == "p1"
        assert req.context == {"key": "val"}


class TestExecutionResult:
    """Test ExecutionResult dataclass."""

    def test_minimal(self) -> None:
        res = ExecutionResult(
            sandbox_id="s1",
            status=SandboxStatus.COMPLETED,
            output="done",
        )
        assert res.sandbox_id == "s1"
        assert res.status == SandboxStatus.COMPLETED
        assert res.output == "done"
        assert res.metadata == {}
        assert res.error is None
        assert res.execution_time_ms == 0.0
        assert res.tokens_used == 0
