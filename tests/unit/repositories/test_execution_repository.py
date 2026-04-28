"""Tests for ExecutionRepository, ExecutionArtifactRepository, and ExecutionEnvironmentConfigRepository.

Comprehensive tests covering execution tracking, artifacts, and environment configuration.
"""

from datetime import UTC, datetime
from typing import Any
from uuid import uuid4

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession

from tests.test_constants import COUNT_FIVE, COUNT_TEN, COUNT_THREE, COUNT_TWO
from tracertm.repositories.execution_repository import (
    ExecutionArtifactRepository,
    ExecutionEnvironmentConfigRepository,
    ExecutionRepository,
)
from tracertm.repositories.project_repository import ProjectRepository

# ==================== Fixtures ====================


@pytest_asyncio.fixture
async def project_setup(db_session: AsyncSession) -> None:
    """Create a project for execution tests."""
    project_repo = ProjectRepository(db_session)
    project = await project_repo.create(
        name="Test Project",
        description="Project for execution tests",
    )
    return {"project": project, "session": db_session}


@pytest_asyncio.fixture
async def execution_setup(project_setup: Any) -> None:
    """Create a project with an execution for testing."""
    session = project_setup["session"]
    project = project_setup["project"]
    repo = ExecutionRepository(session)

    execution = await repo.create(
        project_id=project.id,
        execution_type="playwright",
        trigger_source="manual",
    )

    return {
        "project": project,
        "execution": execution,
        "repo": repo,
        "session": session,
    }


# ==================== ExecutionRepository Tests ====================


class TestExecutionCreate:
    """Tests for ExecutionRepository.create."""

    @pytest.mark.asyncio
    async def test_create_minimal(self, project_setup: Any) -> None:
        """Test creating an execution with minimal fields."""
        session = project_setup["session"]
        project = project_setup["project"]
        repo = ExecutionRepository(session)

        execution = await repo.create(
            project_id=project.id,
            execution_type="vhs",
            trigger_source="manual",
        )

        assert execution is not None
        assert execution.id is not None
        assert execution.project_id == project.id
        assert execution.execution_type == "vhs"
        assert execution.trigger_source == "manual"
        assert execution.status == "pending"

    @pytest.mark.asyncio
    async def test_create_with_all_fields(self, project_setup: Any) -> None:
        """Test creating an execution with all optional fields."""
        session = project_setup["session"]
        project = project_setup["project"]
        repo = ExecutionRepository(session)

        execution = await repo.create(
            project_id=project.id,
            execution_type="playwright",
            trigger_source="github_pr",
            test_run_id=None,
            item_id=None,
            trigger_ref="refs/pull/123",
            config={"browser": "chromium", "headless": True},
        )

        assert execution.execution_type == "playwright"
        assert execution.trigger_source == "github_pr"
        assert execution.trigger_ref == "refs/pull/123"
        assert execution.config == {"browser": "chromium", "headless": True}

    @pytest.mark.asyncio
    async def test_create_different_types(self, project_setup: Any) -> None:
        """Test creating executions with different types."""
        session = project_setup["session"]
        project = project_setup["project"]
        repo = ExecutionRepository(session)

        types = ["vhs", "playwright", "codex", "custom"]
        for exec_type in types:
            execution = await repo.create(
                project_id=project.id,
                execution_type=exec_type,
                trigger_source="manual",
            )
            assert execution.execution_type == exec_type

    @pytest.mark.asyncio
    async def test_create_different_trigger_sources(self, project_setup: Any) -> None:
        """Test creating executions with different trigger sources."""
        session = project_setup["session"]
        project = project_setup["project"]
        repo = ExecutionRepository(session)

        sources = ["github_pr", "github_push", "webhook", "manual"]
        for source in sources:
            execution = await repo.create(
                project_id=project.id,
                execution_type="vhs",
                trigger_source=source,
            )
            assert execution.trigger_source == source


class TestExecutionGetById:
    """Tests for ExecutionRepository.get_by_id."""

    @pytest.mark.asyncio
    async def test_get_by_id_found(self, execution_setup: Any) -> None:
        """Test getting an execution by ID."""
        repo = execution_setup["repo"]
        execution = execution_setup["execution"]

        result = await repo.get_by_id(execution.id)

        assert result is not None
        assert result.id == execution.id
        assert result.execution_type == execution.execution_type

    @pytest.mark.asyncio
    async def test_get_by_id_not_found(self, execution_setup: Any) -> None:
        """Test getting a non-existent execution."""
        repo = execution_setup["repo"]

        result = await repo.get_by_id(str(uuid4()))

        assert result is None


class TestExecutionListByProject:
    """Tests for ExecutionRepository.list_by_project."""

    @pytest.mark.asyncio
    async def test_list_by_project_empty(self, project_setup: Any) -> None:
        """Test listing executions for project with no executions."""
        session = project_setup["session"]
        project = project_setup["project"]
        repo = ExecutionRepository(session)

        executions = await repo.list_by_project(project.id)

        assert executions == []

    @pytest.mark.asyncio
    async def test_list_by_project_multiple(self, project_setup: Any) -> None:
        """Test listing multiple executions."""
        session = project_setup["session"]
        project = project_setup["project"]
        repo = ExecutionRepository(session)

        # Create multiple executions
        for _i in range(5):
            await repo.create(
                project_id=project.id,
                execution_type="vhs",
                trigger_source="manual",
            )

        executions = await repo.list_by_project(project.id)

        assert len(executions) == COUNT_FIVE

    @pytest.mark.asyncio
    async def test_list_by_project_filter_status(self, project_setup: Any) -> None:
        """Test filtering executions by status."""
        session = project_setup["session"]
        project = project_setup["project"]
        repo = ExecutionRepository(session)

        # Create executions with different statuses
        exec1 = await repo.create(project_id=project.id, execution_type="vhs", trigger_source="manual")
        exec2 = await repo.create(project_id=project.id, execution_type="vhs", trigger_source="manual")

        # Update one to running
        await repo.update_status(exec2.id, "running")

        executions = await repo.list_by_project(project.id, status="pending")

        assert len(executions) == 1
        assert executions[0].id == exec1.id

    @pytest.mark.asyncio
    async def test_list_by_project_filter_type(self, project_setup: Any) -> None:
        """Test filtering executions by type."""
        session = project_setup["session"]
        project = project_setup["project"]
        repo = ExecutionRepository(session)

        await repo.create(project_id=project.id, execution_type="vhs", trigger_source="manual")
        await repo.create(project_id=project.id, execution_type="playwright", trigger_source="manual")
        await repo.create(project_id=project.id, execution_type="vhs", trigger_source="manual")

        executions = await repo.list_by_project(project.id, execution_type="vhs")

        assert len(executions) == COUNT_TWO

    @pytest.mark.asyncio
    async def test_list_by_project_pagination(self, project_setup: Any) -> None:
        """Test pagination of execution list."""
        session = project_setup["session"]
        project = project_setup["project"]
        repo = ExecutionRepository(session)

        # Create 10 executions
        for _i in range(10):
            await repo.create(project_id=project.id, execution_type="vhs", trigger_source="manual")

        # Get first page
        page1 = await repo.list_by_project(project.id, limit=3, offset=0)
        assert len(page1) == COUNT_THREE

        # Get second page
        page2 = await repo.list_by_project(project.id, limit=3, offset=3)
        assert len(page2) == COUNT_THREE

        # Ensure different results
        page1_ids = {e.id for e in page1}
        page2_ids = {e.id for e in page2}
        assert page1_ids.isdisjoint(page2_ids)


class TestExecutionUpdateStatus:
    """Tests for ExecutionRepository.update_status."""

    @pytest.mark.asyncio
    async def test_update_status_simple(self, execution_setup: Any) -> None:
        """Test updating execution status."""
        repo = execution_setup["repo"]
        execution = execution_setup["execution"]

        result = await repo.update_status(execution.id, "running")

        assert result is not None
        assert result.status == "running"

    @pytest.mark.asyncio
    async def test_update_status_with_container_info(self, execution_setup: Any) -> None:
        """Test updating status with container information."""
        repo = execution_setup["repo"]
        execution = execution_setup["execution"]

        result = await repo.update_status(
            execution.id,
            "running",
            container_id="abc123def456",
            container_image="node:20-alpine",
        )

        assert result.status == "running"
        assert result.container_id == "abc123def456"
        assert result.container_image == "node:20-alpine"

    @pytest.mark.asyncio
    async def test_update_status_with_timing(self, execution_setup: Any) -> None:
        """Test updating status with timing information."""
        repo = execution_setup["repo"]
        execution = execution_setup["execution"]

        now = datetime.now(UTC)
        result = await repo.update_status(
            execution.id,
            "running",
            started_at=now,
        )

        assert result.status == "running"
        # SQLite strips timezone, so just check it's set
        assert result.started_at is not None

    @pytest.mark.asyncio
    async def test_update_status_completed(self, execution_setup: Any) -> None:
        """Test updating to completed status with all fields."""
        repo = execution_setup["repo"]
        execution = execution_setup["execution"]

        now = datetime.now(UTC)
        result = await repo.update_status(
            execution.id,
            "passed",
            completed_at=now,
            duration_ms=5000,
            exit_code=0,
            output_summary="All tests passed successfully",
        )

        assert result.status == "passed"
        assert result.completed_at is not None
        assert result.duration_ms == 5000
        assert result.exit_code == 0
        assert result.output_summary == "All tests passed successfully"

    @pytest.mark.asyncio
    async def test_update_status_failed(self, execution_setup: Any) -> None:
        """Test updating to failed status with error message."""
        repo = execution_setup["repo"]
        execution = execution_setup["execution"]

        result = await repo.update_status(
            execution.id,
            "failed",
            exit_code=1,
            error_message="Test assertion failed: expected true, got false",
        )

        assert result.status == "failed"
        assert result.exit_code == 1
        assert "Test assertion failed" in result.error_message

    @pytest.mark.asyncio
    async def test_update_status_not_found(self, execution_setup: Any) -> None:
        """Test updating status for non-existent execution."""
        repo = execution_setup["repo"]

        result = await repo.update_status(str(uuid4()), "running")

        assert result is None


# ==================== ExecutionArtifactRepository Tests ====================


class TestArtifactCreate:
    """Tests for ExecutionArtifactRepository.create."""

    @pytest.mark.asyncio
    async def test_create_minimal(self, execution_setup: Any) -> None:
        """Test creating an artifact with minimal fields."""
        session = execution_setup["session"]
        execution = execution_setup["execution"]
        repo = ExecutionArtifactRepository(session)

        now = datetime.now(UTC)
        artifact = await repo.create(
            execution_id=execution.id,
            artifact_type="screenshot",
            file_path="/artifacts/screenshot.png",
            captured_at=now,
        )

        assert artifact is not None
        assert artifact.id is not None
        assert artifact.execution_id == execution.id
        assert artifact.artifact_type == "screenshot"
        assert artifact.file_path == "/artifacts/screenshot.png"

    @pytest.mark.asyncio
    async def test_create_with_all_fields(self, execution_setup: Any) -> None:
        """Test creating an artifact with all fields."""
        session = execution_setup["session"]
        execution = execution_setup["execution"]
        repo = ExecutionArtifactRepository(session)

        now = datetime.now(UTC)
        artifact = await repo.create(
            execution_id=execution.id,
            artifact_type="video",
            file_path="/artifacts/video.mp4",
            captured_at=now,
            item_id=None,
            thumbnail_path="/artifacts/video_thumb.jpg",
            file_size=1024000,
            mime_type="video/mp4",
            artifact_metadata={"duration": 30.5, "resolution": "1920x1080"},
        )

        assert artifact.artifact_type == "video"
        assert artifact.thumbnail_path == "/artifacts/video_thumb.jpg"
        assert artifact.file_size == 1024000
        assert artifact.mime_type == "video/mp4"
        assert artifact.artifact_metadata == {"duration": 30.5, "resolution": "1920x1080"}

    @pytest.mark.asyncio
    async def test_create_different_types(self, execution_setup: Any) -> None:
        """Test creating artifacts with different types."""
        session = execution_setup["session"]
        execution = execution_setup["execution"]
        repo = ExecutionArtifactRepository(session)

        now = datetime.now(UTC)
        types = ["screenshot", "video", "gif", "log", "trace", "tape"]
        for artifact_type in types:
            artifact = await repo.create(
                execution_id=execution.id,
                artifact_type=artifact_type,
                file_path=f"/artifacts/{artifact_type}.file",
                captured_at=now,
            )
            assert artifact.artifact_type == artifact_type


class TestArtifactGetById:
    """Tests for ExecutionArtifactRepository.get_by_id."""

    @pytest.mark.asyncio
    async def test_get_by_id_found(self, execution_setup: Any) -> None:
        """Test getting an artifact by ID."""
        session = execution_setup["session"]
        execution = execution_setup["execution"]
        repo = ExecutionArtifactRepository(session)

        now = datetime.now(UTC)
        artifact = await repo.create(
            execution_id=execution.id,
            artifact_type="screenshot",
            file_path="/artifacts/test.png",
            captured_at=now,
        )

        result = await repo.get_by_id(artifact.id)

        assert result is not None
        assert result.id == artifact.id

    @pytest.mark.asyncio
    async def test_get_by_id_not_found(self, execution_setup: Any) -> None:
        """Test getting a non-existent artifact."""
        session = execution_setup["session"]
        repo = ExecutionArtifactRepository(session)

        result = await repo.get_by_id(str(uuid4()))

        assert result is None


class TestArtifactListByExecution:
    """Tests for ExecutionArtifactRepository.list_by_execution."""

    @pytest.mark.asyncio
    async def test_list_by_execution_empty(self, execution_setup: Any) -> None:
        """Test listing artifacts when none exist."""
        session = execution_setup["session"]
        execution = execution_setup["execution"]
        repo = ExecutionArtifactRepository(session)

        artifacts = await repo.list_by_execution(execution.id)

        assert artifacts == []

    @pytest.mark.asyncio
    async def test_list_by_execution_multiple(self, execution_setup: Any) -> None:
        """Test listing multiple artifacts."""
        session = execution_setup["session"]
        execution = execution_setup["execution"]
        repo = ExecutionArtifactRepository(session)

        now = datetime.now(UTC)
        for i in range(5):
            await repo.create(
                execution_id=execution.id,
                artifact_type="screenshot",
                file_path=f"/artifacts/screenshot_{i}.png",
                captured_at=now,
            )

        artifacts = await repo.list_by_execution(execution.id)

        assert len(artifacts) == COUNT_FIVE

    @pytest.mark.asyncio
    async def test_list_by_execution_filter_type(self, execution_setup: Any) -> None:
        """Test filtering artifacts by type."""
        session = execution_setup["session"]
        execution = execution_setup["execution"]
        repo = ExecutionArtifactRepository(session)

        now = datetime.now(UTC)
        await repo.create(
            execution_id=execution.id,
            artifact_type="screenshot",
            file_path="/artifacts/s1.png",
            captured_at=now,
        )
        await repo.create(
            execution_id=execution.id,
            artifact_type="video",
            file_path="/artifacts/v1.mp4",
            captured_at=now,
        )
        await repo.create(
            execution_id=execution.id,
            artifact_type="screenshot",
            file_path="/artifacts/s2.png",
            captured_at=now,
        )

        artifacts = await repo.list_by_execution(execution.id, artifact_type="screenshot")

        assert len(artifacts) == COUNT_TWO


# ==================== ExecutionEnvironmentConfigRepository Tests ====================


class TestConfigGetByProject:
    """Tests for ExecutionEnvironmentConfigRepository.get_by_project."""

    @pytest.mark.asyncio
    async def test_get_by_project_not_found(self, project_setup: Any) -> None:
        """Test getting config when none exists."""
        session = project_setup["session"]
        project = project_setup["project"]
        repo = ExecutionEnvironmentConfigRepository(session)

        result = await repo.get_by_project(project.id)

        assert result is None

    @pytest.mark.asyncio
    async def test_get_by_project_found(self, project_setup: Any) -> None:
        """Test getting existing config."""
        session = project_setup["session"]
        project = project_setup["project"]
        repo = ExecutionEnvironmentConfigRepository(session)

        # Create config first
        await repo.create_or_update(project.id)

        result = await repo.get_by_project(project.id)

        assert result is not None
        assert result.project_id == project.id


class TestConfigCreateOrUpdate:
    """Tests for ExecutionEnvironmentConfigRepository.create_or_update."""

    @pytest.mark.asyncio
    async def test_create_new_config(self, project_setup: Any) -> None:
        """Test creating a new config."""
        session = project_setup["session"]
        project = project_setup["project"]
        repo = ExecutionEnvironmentConfigRepository(session)

        config = await repo.create_or_update(project.id)

        assert config is not None
        assert config.id is not None
        assert config.project_id == project.id
        # Check defaults
        assert config.docker_image == "node:20-alpine"
        assert config.vhs_enabled is True
        assert config.playwright_enabled is True
        assert config.codex_enabled is True

    @pytest.mark.asyncio
    async def test_create_with_custom_values(self, project_setup: Any) -> None:
        """Test creating config with custom values."""
        session = project_setup["session"]
        project = project_setup["project"]
        repo = ExecutionEnvironmentConfigRepository(session)

        config = await repo.create_or_update(
            project.id,
            docker_image="python:3.12",
            vhs_enabled=False,
            playwright_headless=False,
            max_concurrent_executions=5,
        )

        assert config.docker_image == "python:3.12"
        assert config.vhs_enabled is False
        assert config.playwright_headless is False
        assert config.max_concurrent_executions == COUNT_FIVE

    @pytest.mark.asyncio
    async def test_update_existing_config(self, project_setup: Any) -> None:
        """Test updating an existing config."""
        session = project_setup["session"]
        project = project_setup["project"]
        repo = ExecutionEnvironmentConfigRepository(session)

        # Create initial config
        config1 = await repo.create_or_update(
            project.id,
            docker_image="node:18",
        )
        original_id = config1.id

        # Update config
        config2 = await repo.create_or_update(
            project.id,
            docker_image="node:20",
            vhs_enabled=False,
        )

        # Should be same record
        assert config2.id == original_id
        assert config2.docker_image == "node:20"
        assert config2.vhs_enabled is False

    @pytest.mark.asyncio
    async def test_update_preserves_unmodified_fields(self, project_setup: Any) -> None:
        """Test that update preserves fields not specified."""
        session = project_setup["session"]
        project = project_setup["project"]
        repo = ExecutionEnvironmentConfigRepository(session)

        # Create with custom values
        await repo.create_or_update(
            project.id,
            docker_image="python:3.12",
            playwright_browser="firefox",
        )

        # Update only one field
        config = await repo.create_or_update(
            project.id,
            docker_image="python:3.11",
        )

        # Original custom value should be preserved
        assert config.docker_image == "python:3.11"
        assert config.playwright_browser == "firefox"

    @pytest.mark.asyncio
    async def test_update_all_settings_categories(self, project_setup: Any) -> None:
        """Test updating settings from all categories."""
        session = project_setup["session"]
        project = project_setup["project"]
        repo = ExecutionEnvironmentConfigRepository(session)

        config = await repo.create_or_update(
            project.id,
            # Docker
            docker_image="custom:latest",
            network_mode="host",
            # VHS
            vhs_theme="GitHub Dark",
            vhs_width=1600,
            vhs_height=900,
            # Playwright
            playwright_browser="webkit",
            playwright_viewport_width=1920,
            playwright_viewport_height=1080,
            # Codex
            codex_sandbox_mode="workspace-read",
            codex_timeout=600,
            # Storage
            artifact_retention_days=60,
            max_artifact_size_mb=200,
            # Execution limits
            max_concurrent_executions=10,
            execution_timeout=1200,
        )

        assert config.docker_image == "custom:latest"
        assert config.network_mode == "host"
        assert config.vhs_theme == "GitHub Dark"
        assert config.vhs_width == 1600
        assert config.playwright_browser == "webkit"
        assert config.codex_sandbox_mode == "workspace-read"
        assert config.artifact_retention_days == 60
        assert config.max_concurrent_executions == COUNT_TEN

    @pytest.mark.asyncio
    async def test_create_with_invalid_kwargs_ignored(self, project_setup: Any) -> None:
        """Test that invalid kwargs are silently ignored during create."""
        session = project_setup["session"]
        project = project_setup["project"]
        repo = ExecutionEnvironmentConfigRepository(session)

        # Pass a mix of valid and invalid kwargs
        config = await repo.create_or_update(
            project.id,
            docker_image="python:3.12",
            nonexistent_field="should_be_ignored",
            another_invalid_attr=12345,
        )

        # Valid field should be set
        assert config.docker_image == "python:3.12"
        # Config should still be created successfully
        assert config.id is not None
        assert config.project_id == project.id
        # Invalid fields should not exist on the object
        assert not hasattr(config, "nonexistent_field") or getattr(config, "nonexistent_field", None) is None

    @pytest.mark.asyncio
    async def test_update_with_invalid_kwargs_ignored(self, project_setup: Any) -> None:
        """Test that invalid kwargs are silently ignored during update."""
        session = project_setup["session"]
        project = project_setup["project"]
        repo = ExecutionEnvironmentConfigRepository(session)

        # First create a config
        config1 = await repo.create_or_update(
            project.id,
            docker_image="node:18",
        )
        original_id = config1.id

        # Update with a mix of valid and invalid kwargs
        config2 = await repo.create_or_update(
            project.id,
            docker_image="node:20",
            invalid_field="should_be_ignored",
            fake_setting=True,
        )

        # Should be same record (update path)
        assert config2.id == original_id
        # Valid field should be updated
        assert config2.docker_image == "node:20"
        # Invalid fields should not cause errors

    @pytest.mark.asyncio
    async def test_create_with_only_invalid_kwargs(self, project_setup: Any) -> None:
        """Test creating config with only invalid kwargs still creates a valid config."""
        session = project_setup["session"]
        project = project_setup["project"]
        repo = ExecutionEnvironmentConfigRepository(session)

        # Pass only invalid kwargs
        config = await repo.create_or_update(
            project.id,
            not_a_real_field="value",
            completely_made_up=42,
        )

        # Config should still be created with defaults
        assert config.id is not None
        assert config.project_id == project.id
        assert config.docker_image == "node:20-alpine"  # Default value

    @pytest.mark.asyncio
    async def test_update_with_only_invalid_kwargs(self, project_setup: Any) -> None:
        """Test updating config with only invalid kwargs doesn't change valid fields."""
        session = project_setup["session"]
        project = project_setup["project"]
        repo = ExecutionEnvironmentConfigRepository(session)

        # Create with custom value
        config1 = await repo.create_or_update(
            project.id,
            docker_image="custom:image",
        )
        original_id = config1.id

        # Update with only invalid kwargs
        config2 = await repo.create_or_update(
            project.id,
            fake_attr="ignored",
        )

        # Should be same record and field should be unchanged
        assert config2.id == original_id
        assert config2.docker_image == "custom:image"
