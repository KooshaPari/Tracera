"""Comprehensive unit tests for WorkflowRunRepository to achieve 85%+ coverage.

Tests for:
- create_run() - workflow run creation
- list_runs() - listing with filters and pagination
- update_by_external_id() - updating runs by external ID
"""

from datetime import UTC, datetime
from uuid import uuid4

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from tests.test_constants import COUNT_FIVE, COUNT_THREE, COUNT_TWO
from tracertm.repositories.project_repository import ProjectRepository
from tracertm.repositories.workflow_run_repository import WorkflowRunRepository


def unique_project_name() -> str:
    """Generate a unique project name for tests."""
    return f"Test Project {uuid4().hex[:8]}"


# ============================================================================
# CREATE_RUN OPERATIONS
# ============================================================================


@pytest.mark.unit
@pytest.mark.asyncio
async def test_create_run_basic(db_session: AsyncSession) -> None:
    """Test creating workflow run with basic fields."""
    project_repo = ProjectRepository(db_session)
    project = await project_repo.create(name=unique_project_name())
    await db_session.commit()

    repo = WorkflowRunRepository(db_session)
    run = await repo.create_run(
        workflow_name="test_workflow",
        project_id=str(project.id),
    )

    assert run.id is not None
    assert run.workflow_name == "test_workflow"
    assert run.status == "queued"
    assert run.project_id == project.id
    assert run.payload == {}
    assert run.result == {}


@pytest.mark.unit
@pytest.mark.asyncio
async def test_create_run_with_payload(db_session: AsyncSession) -> None:
    """Test creating workflow run with payload."""
    project_repo = ProjectRepository(db_session)
    project = await project_repo.create(name=unique_project_name())
    await db_session.commit()

    repo = WorkflowRunRepository(db_session)
    payload = {"input": "test_data", "config": {"option": True}}
    run = await repo.create_run(
        workflow_name="data_processing",
        project_id=str(project.id),
        payload=payload,
    )

    assert run.payload == payload


@pytest.mark.unit
@pytest.mark.asyncio
async def test_create_run_with_external_id(db_session: AsyncSession) -> None:
    """Test creating workflow run with external run ID."""
    project_repo = ProjectRepository(db_session)
    project = await project_repo.create(name=unique_project_name())
    await db_session.commit()

    repo = WorkflowRunRepository(db_session)
    external_id = f"ext-{uuid4().hex[:8]}"
    run = await repo.create_run(
        workflow_name="external_workflow",
        project_id=str(project.id),
        external_run_id=external_id,
    )

    assert run.external_run_id == external_id


@pytest.mark.unit
@pytest.mark.asyncio
async def test_create_run_with_graph_id(db_session: AsyncSession) -> None:
    """Test creating workflow run with graph ID."""
    from tests.unit.repositories.conftest import create_default_graph_for_project

    project_repo = ProjectRepository(db_session)
    project = await project_repo.create(name=unique_project_name())
    graph = await create_default_graph_for_project(db_session, str(project.id))
    await db_session.commit()

    repo = WorkflowRunRepository(db_session)
    run = await repo.create_run(
        workflow_name="graph_workflow",
        project_id=str(project.id),
        graph_id=str(graph.id),
    )

    assert run.graph_id == graph.id


@pytest.mark.unit
@pytest.mark.asyncio
async def test_create_run_with_user_id(db_session: AsyncSession) -> None:
    """Test creating workflow run with created_by_user_id."""
    project_repo = ProjectRepository(db_session)
    project = await project_repo.create(name=unique_project_name())
    await db_session.commit()

    repo = WorkflowRunRepository(db_session)
    user_id = f"user-{uuid4().hex[:8]}"
    run = await repo.create_run(
        workflow_name="user_workflow",
        project_id=str(project.id),
        created_by_user_id=user_id,
    )

    assert run.created_by_user_id == user_id


@pytest.mark.unit
@pytest.mark.asyncio
async def test_create_run_with_all_fields(db_session: AsyncSession) -> None:
    """Test creating workflow run with all optional fields."""
    from tests.unit.repositories.conftest import create_default_graph_for_project

    project_repo = ProjectRepository(db_session)
    project = await project_repo.create(name=unique_project_name())
    graph = await create_default_graph_for_project(db_session, str(project.id))
    await db_session.commit()

    repo = WorkflowRunRepository(db_session)
    external_id = f"ext-{uuid4().hex[:8]}"
    user_id = f"user-{uuid4().hex[:8]}"
    payload = {"key": "value"}

    run = await repo.create_run(
        workflow_name="complete_workflow",
        project_id=str(project.id),
        graph_id=str(graph.id),
        payload=payload,
        external_run_id=external_id,
        created_by_user_id=user_id,
    )

    assert run.workflow_name == "complete_workflow"
    assert run.project_id == project.id
    assert run.graph_id == graph.id
    assert run.payload == payload
    assert run.external_run_id == external_id
    assert run.created_by_user_id == user_id
    assert run.status == "queued"


@pytest.mark.unit
@pytest.mark.asyncio
async def test_create_run_without_project(db_session: AsyncSession) -> None:
    """Test creating workflow run without project ID."""
    repo = WorkflowRunRepository(db_session)
    run = await repo.create_run(workflow_name="standalone_workflow")

    assert run.id is not None
    assert run.project_id is None


# ============================================================================
# LIST_RUNS OPERATIONS
# ============================================================================


@pytest.mark.unit
@pytest.mark.asyncio
async def test_list_runs_basic(db_session: AsyncSession) -> None:
    """Test listing workflow runs for a project."""
    project_repo = ProjectRepository(db_session)
    project = await project_repo.create(name=unique_project_name())
    await db_session.commit()

    repo = WorkflowRunRepository(db_session)
    await repo.create_run(workflow_name="workflow1", project_id=str(project.id))
    await repo.create_run(workflow_name="workflow2", project_id=str(project.id))
    await repo.create_run(workflow_name="workflow3", project_id=str(project.id))
    await db_session.commit()

    runs = await repo.list_runs(project_id=str(project.id))

    assert len(runs) == COUNT_THREE


@pytest.mark.unit
@pytest.mark.asyncio
async def test_list_runs_filters_by_project(db_session: AsyncSession) -> None:
    """Test listing runs only returns runs for specified project."""
    project_repo = ProjectRepository(db_session)
    project1 = await project_repo.create(name=unique_project_name())
    project2 = await project_repo.create(name=unique_project_name())
    await db_session.commit()

    repo = WorkflowRunRepository(db_session)
    await repo.create_run(workflow_name="workflow1", project_id=str(project1.id))
    await repo.create_run(workflow_name="workflow2", project_id=str(project1.id))
    await repo.create_run(workflow_name="workflow3", project_id=str(project2.id))
    await db_session.commit()

    runs1 = await repo.list_runs(project_id=str(project1.id))
    runs2 = await repo.list_runs(project_id=str(project2.id))

    assert len(runs1) == COUNT_TWO
    assert len(runs2) == 1


@pytest.mark.unit
@pytest.mark.asyncio
async def test_list_runs_filter_by_status(db_session: AsyncSession) -> None:
    """Test listing runs with status filter."""
    project_repo = ProjectRepository(db_session)
    project = await project_repo.create(name=unique_project_name())
    await db_session.commit()

    repo = WorkflowRunRepository(db_session)
    run1 = await repo.create_run(workflow_name="workflow1", project_id=str(project.id))
    await repo.create_run(workflow_name="workflow2", project_id=str(project.id))
    await repo.create_run(workflow_name="workflow3", project_id=str(project.id))
    await db_session.commit()

    # Update some runs to different statuses
    await repo.update_by_external_id(
        external_run_id=run1.external_run_id or run1.id,
        status="completed",
    )
    await db_session.commit()

    # Filter by queued status (default)
    queued_runs = await repo.list_runs(project_id=str(project.id), status="queued")

    # Should return runs that are still queued
    assert all(run.status == "queued" for run in queued_runs)


@pytest.mark.unit
@pytest.mark.asyncio
async def test_list_runs_filter_by_workflow_name(db_session: AsyncSession) -> None:
    """Test listing runs with workflow name filter."""
    project_repo = ProjectRepository(db_session)
    project = await project_repo.create(name=unique_project_name())
    await db_session.commit()

    repo = WorkflowRunRepository(db_session)
    await repo.create_run(workflow_name="data_sync", project_id=str(project.id))
    await repo.create_run(workflow_name="data_sync", project_id=str(project.id))
    await repo.create_run(workflow_name="analysis", project_id=str(project.id))
    await db_session.commit()

    data_sync_runs = await repo.list_runs(project_id=str(project.id), workflow_name="data_sync")
    analysis_runs = await repo.list_runs(project_id=str(project.id), workflow_name="analysis")

    assert len(data_sync_runs) == COUNT_TWO
    assert len(analysis_runs) == 1
    assert all(run.workflow_name == "data_sync" for run in data_sync_runs)
    assert all(run.workflow_name == "analysis" for run in analysis_runs)


@pytest.mark.unit
@pytest.mark.asyncio
async def test_list_runs_pagination_limit(db_session: AsyncSession) -> None:
    """Test listing runs with limit."""
    project_repo = ProjectRepository(db_session)
    project = await project_repo.create(name=unique_project_name())
    await db_session.commit()

    repo = WorkflowRunRepository(db_session)
    for i in range(10):
        await repo.create_run(workflow_name=f"workflow_{i}", project_id=str(project.id))
    await db_session.commit()

    runs = await repo.list_runs(project_id=str(project.id), limit=5)

    assert len(runs) == COUNT_FIVE


@pytest.mark.unit
@pytest.mark.asyncio
async def test_list_runs_pagination_offset(db_session: AsyncSession) -> None:
    """Test listing runs with offset."""
    project_repo = ProjectRepository(db_session)
    project = await project_repo.create(name=unique_project_name())
    await db_session.commit()

    repo = WorkflowRunRepository(db_session)
    for i in range(10):
        await repo.create_run(workflow_name=f"workflow_{i}", project_id=str(project.id))
    await db_session.commit()

    runs = await repo.list_runs(project_id=str(project.id), limit=5, offset=5)

    assert len(runs) == COUNT_FIVE


@pytest.mark.unit
@pytest.mark.asyncio
async def test_list_runs_empty_when_no_runs(db_session: AsyncSession) -> None:
    """Test listing runs returns empty list when no runs exist."""
    project_repo = ProjectRepository(db_session)
    project = await project_repo.create(name=unique_project_name())
    await db_session.commit()

    repo = WorkflowRunRepository(db_session)
    runs = await repo.list_runs(project_id=str(project.id))

    assert runs == []


# ============================================================================
# UPDATE_BY_EXTERNAL_ID OPERATIONS
# ============================================================================


@pytest.mark.unit
@pytest.mark.asyncio
async def test_update_by_external_id_status(db_session: AsyncSession) -> None:
    """Test updating run status by external ID."""
    project_repo = ProjectRepository(db_session)
    project = await project_repo.create(name=unique_project_name())
    await db_session.commit()

    repo = WorkflowRunRepository(db_session)
    external_id = f"ext-{uuid4().hex[:8]}"
    run = await repo.create_run(
        workflow_name="workflow",
        project_id=str(project.id),
        external_run_id=external_id,
    )
    await db_session.commit()

    await repo.update_by_external_id(
        external_run_id=external_id,
        status="running",
    )
    await db_session.commit()

    # Refresh to get updated data
    await db_session.refresh(run)

    assert run.status == "running"


@pytest.mark.unit
@pytest.mark.asyncio
async def test_update_by_external_id_with_result(db_session: AsyncSession) -> None:
    """Test updating run with result by external ID."""
    project_repo = ProjectRepository(db_session)
    project = await project_repo.create(name=unique_project_name())
    await db_session.commit()

    repo = WorkflowRunRepository(db_session)
    external_id = f"ext-{uuid4().hex[:8]}"
    run = await repo.create_run(
        workflow_name="workflow",
        project_id=str(project.id),
        external_run_id=external_id,
    )
    await db_session.commit()

    result = {"output": "success", "count": 42}
    await repo.update_by_external_id(
        external_run_id=external_id,
        status="completed",
        result=result,
    )
    await db_session.commit()

    await db_session.refresh(run)

    assert run.status == "completed"
    assert run.result == result


@pytest.mark.unit
@pytest.mark.asyncio
async def test_update_by_external_id_with_error(db_session: AsyncSession) -> None:
    """Test updating run with error message by external ID."""
    project_repo = ProjectRepository(db_session)
    project = await project_repo.create(name=unique_project_name())
    await db_session.commit()

    repo = WorkflowRunRepository(db_session)
    external_id = f"ext-{uuid4().hex[:8]}"
    run = await repo.create_run(
        workflow_name="workflow",
        project_id=str(project.id),
        external_run_id=external_id,
    )
    await db_session.commit()

    await repo.update_by_external_id(
        external_run_id=external_id,
        status="failed",
        error_message="Connection timeout",
    )
    await db_session.commit()

    await db_session.refresh(run)

    assert run.status == "failed"
    assert run.error_message == "Connection timeout"


@pytest.mark.unit
@pytest.mark.asyncio
async def test_update_by_external_id_with_timestamps(db_session: AsyncSession) -> None:
    """Test updating run with timestamps by external ID."""
    project_repo = ProjectRepository(db_session)
    project = await project_repo.create(name=unique_project_name())
    await db_session.commit()

    repo = WorkflowRunRepository(db_session)
    external_id = f"ext-{uuid4().hex[:8]}"
    run = await repo.create_run(
        workflow_name="workflow",
        project_id=str(project.id),
        external_run_id=external_id,
    )
    await db_session.commit()

    started = datetime.now(UTC)
    completed = datetime.now(UTC)

    await repo.update_by_external_id(
        external_run_id=external_id,
        status="completed",
        started_at=started,
        completed_at=completed,
    )
    await db_session.commit()

    await db_session.refresh(run)

    assert run.started_at is not None
    assert run.completed_at is not None


@pytest.mark.unit
@pytest.mark.asyncio
async def test_update_by_external_id_all_fields(db_session: AsyncSession) -> None:
    """Test updating run with all fields by external ID."""
    project_repo = ProjectRepository(db_session)
    project = await project_repo.create(name=unique_project_name())
    await db_session.commit()

    repo = WorkflowRunRepository(db_session)
    external_id = f"ext-{uuid4().hex[:8]}"
    run = await repo.create_run(
        workflow_name="workflow",
        project_id=str(project.id),
        external_run_id=external_id,
    )
    await db_session.commit()

    started = datetime.now(UTC)
    completed = datetime.now(UTC)
    result = {"success": True}

    await repo.update_by_external_id(
        external_run_id=external_id,
        status="completed",
        result=result,
        error_message=None,
        started_at=started,
        completed_at=completed,
    )
    await db_session.commit()

    await db_session.refresh(run)

    assert run.status == "completed"
    assert run.result == result
    assert run.started_at is not None
    assert run.completed_at is not None
