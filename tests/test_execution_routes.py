from typing import Any

"""Tests for execution API routes."""

from datetime import UTC, datetime
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from tests.test_constants import COUNT_TWO, HTTP_BAD_REQUEST, HTTP_NOT_FOUND
from tracertm.api.routers.execution import (
    add_artifact,
    complete_execution,
    create_execution,
    generate_vhs_tape,
    get_execution,
    get_execution_config,
    list_artifacts,
    list_executions,
    start_execution,
    update_execution_config,
)
from tracertm.schemas.execution import (
    ExecutionArtifactCreate,
    ExecutionComplete,
    ExecutionCreate,
    ExecutionEnvironmentConfigUpdate,
    ExecutionStart,
)


@pytest.fixture
def mock_db() -> None:
    """Create a mock AsyncSession."""
    return MagicMock(spec=AsyncSession)


@pytest.fixture
def mock_claims() -> None:
    """Create mock auth claims."""
    return {"role": "admin", "sub": "user123"}


@pytest.fixture
def mock_execution() -> None:
    """Create a mock Execution model."""
    mock = MagicMock()
    mock.id = "exec123"
    mock.project_id = "proj123"
    mock.execution_type = "playwright"
    mock.trigger_source = "manual"
    mock.status = "pending"
    mock.created_at = datetime.now(UTC)
    mock.updated_at = datetime.now(UTC)
    mock.started_at = None
    mock.completed_at = None
    mock.duration_ms = None
    mock.exit_code = None
    mock.error_message = None
    mock.output_summary = None
    mock.container_id = None
    mock.container_image = None
    return mock


@pytest.fixture
def mock_artifact() -> None:
    """Create a mock ExecutionArtifact model."""
    mock = MagicMock()
    mock.id = "art123"
    mock.execution_id = "exec123"
    mock.artifact_type = "screenshot"
    mock.file_path = "/artifacts/screenshot.png"
    mock.file_size = 102400
    mock.mime_type = "image/png"
    mock.captured_at = datetime.now(UTC)
    mock.created_at = datetime.now(UTC)
    return mock


@pytest.fixture
def mock_config() -> None:
    """Create a mock ExecutionEnvironmentConfig model."""
    mock = MagicMock()
    mock.id = "config123"
    mock.project_id = "proj123"
    mock.docker_image = "node:20-alpine"
    mock.vhs_enabled = True
    mock.playwright_enabled = True
    mock.vhs_theme = "Dracula"
    mock.vhs_font_size = 14
    mock.vhs_width = 1200
    mock.vhs_height = 600
    return mock


# =============================================================================
# Create Execution Tests
# =============================================================================


@pytest.mark.asyncio
async def test_create_execution_success(mock_db: Any, mock_claims: Any, mock_execution: Any) -> None:
    """Test creating an execution successfully."""
    with patch("tracertm.api.routers.execution.ExecutionService") as MockService:
        service = MagicMock()
        MockService.return_value = service

        service.create = AsyncMock(return_value=mock_execution)
        service.list_artifacts = AsyncMock(return_value=[])

        execution_create = ExecutionCreate(
            execution_type="playwright",
            trigger_source="manual",
        )

        result = await create_execution(
            project_id="proj123",
            execution_create=execution_create,
            claims=mock_claims,
            db=mock_db,
        )

        assert result.id == "exec123"
        assert result.project_id == "proj123"
        assert result.execution_type == "playwright"
        assert result.artifact_count == 0
        service.create.assert_called_once()


@pytest.mark.asyncio
async def test_create_execution_with_config(mock_db: Any, mock_claims: Any, mock_execution: Any) -> None:
    """Test creating an execution with custom config."""
    with patch("tracertm.api.routers.execution.ExecutionService") as MockService:
        service = MagicMock()
        MockService.return_value = service

        service.create = AsyncMock(return_value=mock_execution)
        service.list_artifacts = AsyncMock(return_value=[])

        custom_config = {
            "vhs_theme": "Dracula",
            "vhs_width": 1600,
        }

        execution_create = ExecutionCreate(
            execution_type="vhs",
            trigger_source="webhook",
            trigger_ref="pr-42",
            config=custom_config,
        )

        result = await create_execution(
            project_id="proj123",
            execution_create=execution_create,
            claims=mock_claims,
            db=mock_db,
        )

        assert result.id == "exec123"
        service.create.assert_called_once_with(
            project_id="proj123",
            execution_type="vhs",
            trigger_source="webhook",
            test_run_id=None,
            item_id=None,
            trigger_ref="pr-42",
            config=custom_config,
        )


# =============================================================================
# List Executions Tests
# =============================================================================


@pytest.mark.asyncio
async def test_list_executions_success(mock_db: Any, mock_claims: Any, mock_execution: Any) -> None:
    """Test listing executions for a project."""
    with patch("tracertm.api.routers.execution.ExecutionService") as MockService:
        service = MagicMock()
        MockService.return_value = service

        mock_execution2 = MagicMock()
        mock_execution2.id = "exec456"
        mock_execution2.project_id = "proj123"

        service.list_by_project = AsyncMock(return_value=[mock_execution, mock_execution2])
        service.list_artifacts = AsyncMock(return_value=[])

        result = await list_executions(
            project_id="proj123",
            claims=mock_claims,
            db=mock_db,
        )

        assert result.total == COUNT_TWO
        assert len(result.executions) == COUNT_TWO
        assert result.executions[0].id == "exec123"
        assert result.executions[1].id == "exec456"


@pytest.mark.asyncio
async def test_list_executions_with_filters(mock_db: Any, mock_claims: Any, mock_execution: Any) -> None:
    """Test listing executions with status and type filters."""
    with patch("tracertm.api.routers.execution.ExecutionService") as MockService:
        service = MagicMock()
        MockService.return_value = service

        service.list_by_project = AsyncMock(return_value=[mock_execution])
        service.list_artifacts = AsyncMock(return_value=[])

        result = await list_executions(
            project_id="proj123",
            status="running",
            execution_type="playwright",
            claims=mock_claims,
            db=mock_db,
        )

        assert result.total == 1
        service.list_by_project.assert_called_once_with(
            "proj123",
            status="running",
            execution_type="playwright",
            limit=100,
            offset=0,
        )


# =============================================================================
# Get Execution Tests
# =============================================================================


@pytest.mark.asyncio
async def test_get_execution_success(mock_db: Any, mock_claims: Any, mock_execution: Any) -> None:
    """Test getting an execution by ID."""
    with patch("tracertm.api.routers.execution.ExecutionService") as MockService:
        service = MagicMock()
        MockService.return_value = service

        service.get = AsyncMock(return_value=mock_execution)
        service.list_artifacts = AsyncMock(return_value=[])

        result = await get_execution(
            project_id="proj123",
            execution_id="exec123",
            claims=mock_claims,
            db=mock_db,
        )

        assert result.id == "exec123"
        service.get.assert_called_once_with("exec123")


@pytest.mark.asyncio
async def test_get_execution_not_found(mock_db: Any, mock_claims: Any) -> None:
    """Test getting a non-existent execution."""
    with patch("tracertm.api.routers.execution.ExecutionService") as MockService:
        service = MagicMock()
        MockService.return_value = service

        service.get = AsyncMock(return_value=None)

        with pytest.raises(HTTPException) as exc_info:
            await get_execution(
                project_id="proj123",
                execution_id="nonexistent",
                claims=mock_claims,
                db=mock_db,
            )

        exc = exc_info.value
        assert isinstance(exc, HTTPException)
        assert getattr(exc, "status_code", None) == HTTP_NOT_FOUND


@pytest.mark.asyncio
async def test_get_execution_forbidden(mock_db: Any, mock_claims: Any) -> None:
    """Test getting an execution from a different project."""
    mock_execution = MagicMock()
    mock_execution.id = "exec123"
    mock_execution.project_id = "proj999"

    with patch("tracertm.api.routers.execution.ExecutionService") as MockService:
        service = MagicMock()
        MockService.return_value = service

        service.get = AsyncMock(return_value=mock_execution)

        with pytest.raises(HTTPException) as exc_info:
            await get_execution(
                project_id="proj123",
                execution_id="exec123",
                claims=mock_claims,
                db=mock_db,
            )

        exc = exc_info.value
        assert isinstance(exc, HTTPException)
        assert getattr(exc, "status_code", None) == 403


# =============================================================================
# Start Execution Tests
# =============================================================================


@pytest.mark.asyncio
async def test_start_execution_success(mock_db: Any, mock_claims: Any, mock_execution: Any) -> None:
    """Test starting an execution."""
    with patch("tracertm.api.routers.execution.ExecutionService") as MockService:
        service = MagicMock()
        MockService.return_value = service

        service.get = AsyncMock(return_value=mock_execution)
        service.start = AsyncMock(return_value=True)
        service.list_artifacts = AsyncMock(return_value=[])

        mock_execution.status = "running"

        result = await start_execution(
            project_id="proj123",
            execution_id="exec123",
            start_data=ExecutionStart(),
            claims=mock_claims,
            db=mock_db,
        )

        assert result.id == "exec123"
        service.start.assert_called_once_with("exec123")


@pytest.mark.asyncio
async def test_start_execution_wrong_status(mock_db: Any, mock_claims: Any) -> None:
    """Test starting an execution that's not pending."""
    mock_execution = MagicMock()
    mock_execution.id = "exec123"
    mock_execution.project_id = "proj123"
    mock_execution.status = "running"

    with patch("tracertm.api.routers.execution.ExecutionService") as MockService:
        service = MagicMock()
        MockService.return_value = service

        service.get = AsyncMock(return_value=mock_execution)

        with pytest.raises(HTTPException) as exc_info:
            await start_execution(
                project_id="proj123",
                execution_id="exec123",
                start_data=ExecutionStart(),
                claims=mock_claims,
                db=mock_db,
            )

        exc = exc_info.value
        assert isinstance(exc, HTTPException)
        assert getattr(exc, "status_code", None) == 409


# =============================================================================
# Complete Execution Tests
# =============================================================================


@pytest.mark.asyncio
async def test_complete_execution_success(mock_db: Any, mock_claims: Any, mock_execution: Any) -> None:
    """Test completing an execution."""
    with patch("tracertm.api.routers.execution.ExecutionService") as MockService:
        service = MagicMock()
        MockService.return_value = service

        completed_execution = MagicMock()
        completed_execution.id = "exec123"
        completed_execution.project_id = "proj123"
        completed_execution.status = "passed"
        completed_execution.exit_code = 0
        completed_execution.duration_ms = 5000

        service.get = AsyncMock(return_value=mock_execution)
        service.complete = AsyncMock(return_value=completed_execution)
        service.list_artifacts = AsyncMock(return_value=[])

        result = await complete_execution(
            project_id="proj123",
            execution_id="exec123",
            complete_data=ExecutionComplete(status="passed"),
            claims=mock_claims,
            db=mock_db,
        )

        assert result.id == "exec123"
        assert result.status == "passed"
        service.complete.assert_called_once()


# =============================================================================
# Artifacts Tests
# =============================================================================


@pytest.mark.asyncio
async def test_list_artifacts_success(mock_db: Any, mock_claims: Any, mock_execution: Any, mock_artifact: Any) -> None:
    """Test listing artifacts for an execution."""
    with patch("tracertm.api.routers.execution.ExecutionService") as MockService:
        service = MagicMock()
        MockService.return_value = service

        service.get = AsyncMock(return_value=mock_execution)
        service.list_artifacts = AsyncMock(return_value=[mock_artifact])

        result = await list_artifacts(
            project_id="proj123",
            execution_id="exec123",
            claims=mock_claims,
            db=mock_db,
        )

        assert result.total == 1
        assert len(result.artifacts) == 1
        assert result.artifacts[0].id == "art123"


@pytest.mark.asyncio
async def test_add_artifact_success(mock_db: Any, mock_claims: Any, mock_execution: Any, mock_artifact: Any) -> None:
    """Test adding an artifact to an execution."""
    with patch("tracertm.api.routers.execution.ExecutionService") as MockService:
        service = MagicMock()
        MockService.return_value = service

        service.get = AsyncMock(return_value=mock_execution)
        service.store_artifact = AsyncMock(return_value=mock_artifact)

        artifact_create = ExecutionArtifactCreate(
            artifact_type="screenshot",
            file_path="/tmp/screenshot.png",
        )

        result = await add_artifact(
            project_id="proj123",
            execution_id="exec123",
            artifact_create=artifact_create,
            claims=mock_claims,
            db=mock_db,
        )

        assert result.id == "art123"
        assert result.artifact_type == "screenshot"
        service.store_artifact.assert_called_once()


# =============================================================================
# Config Tests
# =============================================================================


@pytest.mark.asyncio
async def test_get_execution_config_success(mock_db: Any, mock_claims: Any, mock_config: Any) -> None:
    """Test getting execution configuration."""
    with patch("tracertm.api.routers.execution.ExecutionService") as MockService:
        service = MagicMock()
        MockService.return_value = service

        service.get_config = AsyncMock(return_value=mock_config)

        result = await get_execution_config(
            project_id="proj123",
            claims=mock_claims,
            db=mock_db,
        )

        assert result.id == "config123"
        assert result.docker_image == "node:20-alpine"


@pytest.mark.asyncio
async def test_update_execution_config_success(mock_db: Any, mock_claims: Any, _mock_config: Any) -> None:
    """Test updating execution configuration."""
    with patch("tracertm.api.routers.execution.ExecutionService") as MockService:
        service = MagicMock()
        MockService.return_value = service

        updated_config = MagicMock()
        updated_config.id = "config123"
        updated_config.docker_image = "node:22-alpine"
        updated_config.vhs_theme = "Nord"

        service.upsert_config = AsyncMock(return_value=updated_config)

        config_update = ExecutionEnvironmentConfigUpdate(
            docker_image="node:22-alpine",
            vhs_theme="Nord",
        )

        result = await update_execution_config(
            project_id="proj123",
            config_update=config_update,
            claims=mock_claims,
            db=mock_db,
        )

        assert result.id == "config123"
        assert result.docker_image == "node:22-alpine"
        service.upsert_config.assert_called_once()


# =============================================================================
# VHS Tape Generation Tests
# =============================================================================


@pytest.mark.asyncio
async def test_generate_vhs_tape_success(
    mock_db: Any, mock_claims: Any, mock_execution: Any, mock_artifact: Any, mock_config: Any
) -> None:
    """Test generating a VHS tape."""
    with patch("tracertm.api.routers.execution.ExecutionService") as MockService:
        with patch("tracertm.api.routers.execution.VHSService"):
            service = MagicMock()
            MockService.return_value = service

            service.get = AsyncMock(return_value=mock_execution)
            service.list_artifacts = AsyncMock(return_value=[mock_artifact])
            service.get_config = AsyncMock(return_value=mock_config)

            result = await generate_vhs_tape(
                project_id="proj123",
                execution_id="exec123",
                claims=mock_claims,
                db=mock_db,
            )

            assert result["status"] == "accepted"
            assert result["execution_id"] == "exec123"


@pytest.mark.asyncio
async def test_generate_vhs_tape_no_artifacts(mock_db: Any, mock_claims: Any, mock_execution: Any) -> None:
    """Test generating a VHS tape with no artifacts."""
    with patch("tracertm.api.routers.execution.ExecutionService") as MockService:
        service = MagicMock()
        MockService.return_value = service

        service.get = AsyncMock(return_value=mock_execution)
        service.list_artifacts = AsyncMock(return_value=[])

        with pytest.raises(HTTPException) as exc_info:
            await generate_vhs_tape(
                project_id="proj123",
                execution_id="exec123",
                claims=mock_claims,
                db=mock_db,
            )

        exc = exc_info.value
        assert isinstance(exc, HTTPException)
        assert getattr(exc, "status_code", None) == HTTP_BAD_REQUEST
