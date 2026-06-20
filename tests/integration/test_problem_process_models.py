from typing import Any

"""Integration tests for Problem and Process models."""

from datetime import UTC, datetime
from uuid import uuid4

import pytest

from tests.test_constants import COUNT_TWO
from tracertm.models.problem import Problem, ProblemActivity
from tracertm.models.process import Process, ProcessExecution
from tracertm.models.project import Project


@pytest.mark.asyncio
@pytest.mark.integration
async def test_problem_model_crud(async_db_session: Any) -> None:
    """Test Problem model CRUD operations."""
    # Create a project first
    project = Project(
        id=str(uuid4()),
        name="Test Project",
        description="Test project for problem model",
    )
    async_db_session.add(project)
    await async_db_session.flush()

    # Create a problem
    problem = Problem(
        id=str(uuid4()),
        project_id=project.id,
        problem_number="PRB-001",
        title="Test Problem",
        description="Test problem description",
        status="open",
        impact_level="medium",
        urgency="medium",
        priority="medium",
    )
    async_db_session.add(problem)
    await async_db_session.flush()

    # Verify the problem was created
    assert problem.id is not None
    assert problem.problem_number == "PRB-001"
    assert problem.status == "open"
    assert problem.impact_level == "medium"

    # Update the problem
    problem.status = "in_investigation"
    await async_db_session.flush()
    assert problem.status == "in_investigation"

    # Create problem activity
    activity = ProblemActivity(
        id=str(uuid4()),
        problem_id=problem.id,
        activity_type="status_change",
        description="Changed status to in_investigation",
        performed_by="test_user",
    )
    async_db_session.add(activity)
    await async_db_session.flush()

    assert activity.id is not None
    assert activity.activity_type == "status_change"


@pytest.mark.asyncio
@pytest.mark.integration
async def test_process_model_crud(async_db_session: Any) -> None:
    """Test Process model CRUD operations."""
    # Create a project first
    project = Project(
        id=str(uuid4()),
        name="Test Project",
        description="Test project for process model",
    )
    async_db_session.add(project)
    await async_db_session.flush()

    # Create a process
    process = Process(
        id=str(uuid4()),
        project_id=project.id,
        process_number="PRC-001",
        name="Test Process",
        description="Test process description",
        status="draft",
        category="operational",
        version_number=1,
        is_active_version=True,
        stages=[
            {"id": "1", "name": "Stage 1", "order": 1, "required": True},
            {"id": "2", "name": "Stage 2", "order": 2, "required": False},
        ],
        swimlanes=[
            {"id": "1", "name": "Developer", "role": "dev"},
        ],
    )
    async_db_session.add(process)
    await async_db_session.flush()

    # Verify the process was created
    assert process.id is not None
    assert process.process_number == "PRC-001"
    assert process.status == "draft"
    assert process.version_number == 1
    stages = process.stages or []
    swimlanes = process.swimlanes or []
    assert len(stages) == COUNT_TWO
    assert len(swimlanes) == 1

    # Update the process
    process.status = "active"
    await async_db_session.flush()
    assert process.status == "active"

    # Create process execution
    execution = ProcessExecution(
        id=str(uuid4()),
        process_id=process.id,
        execution_number="EXEC-001",
        status="in_progress",
        started_at=datetime.now(UTC),
        initiated_by="test_user",
    )
    async_db_session.add(execution)
    await async_db_session.flush()

    assert execution.id is not None
    assert execution.status == "in_progress"


@pytest.mark.asyncio
@pytest.mark.integration
async def test_problem_status_transitions(async_db_session: Any) -> None:
    """Test Problem status transitions follow ITIL flow."""
    project = Project(id=str(uuid4()), name="Test Project")
    async_db_session.add(project)
    await async_db_session.flush()

    problem = Problem(
        id=str(uuid4()),
        project_id=project.id,
        problem_number="PRB-002",
        title="Status Test Problem",
        status="open",
        impact_level="high",
        urgency="high",
        priority="high",
    )
    async_db_session.add(problem)
    await async_db_session.flush()

    # Test valid ITIL status transitions
    valid_statuses = ["open", "in_investigation", "pending_workaround", "known_error", "awaiting_fix", "closed"]

    for status in valid_statuses:
        problem.status = status
        await async_db_session.flush()
        assert problem.status == status


@pytest.mark.asyncio
@pytest.mark.integration
async def test_process_versioning(async_db_session: Any) -> None:
    """Test Process versioning functionality."""
    project = Project(id=str(uuid4()), name="Test Project")
    async_db_session.add(project)
    await async_db_session.flush()

    # Create version 1
    process_v1 = Process(
        id=str(uuid4()),
        project_id=project.id,
        process_number="PRC-002",
        name="Versioned Process",
        status="active",
        version_number=1,
        is_active_version=True,
    )
    async_db_session.add(process_v1)
    await async_db_session.flush()

    # Create version 2 (new active version)
    process_v2 = Process(
        id=str(uuid4()),
        project_id=project.id,
        process_number="PRC-002-v2",
        parent_version_id=process_v1.id,
        name="Versioned Process",
        status="active",
        version_number=2,
        is_active_version=True,
    )
    async_db_session.add(process_v2)

    # Deactivate v1
    process_v1.is_active_version = False
    await async_db_session.flush()

    assert process_v1.is_active_version is False
    assert process_v2.is_active_version is True
    assert process_v2.parent_version_id == process_v1.id
