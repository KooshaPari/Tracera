from typing import Any

"""Integration tests for Problem and Process repositories."""

from uuid import uuid4

import pytest

from tests.test_constants import COUNT_TWO
from tracertm.models.project import Project
from tracertm.repositories.problem_repository import ProblemRepository
from tracertm.repositories.process_repository import ProcessRepository


@pytest.mark.asyncio
@pytest.mark.integration
async def test_problem_repository_crud(async_db_session: Any) -> None:
    """Test ProblemRepository CRUD operations."""
    # Create a project first
    project = Project(
        id=str(uuid4()),
        name="Test Project",
        description="Test project for problem repository",
    )
    async_db_session.add(project)
    await async_db_session.flush()

    repo = ProblemRepository(async_db_session)

    # Create a problem
    problem = await repo.create(
        project_id=str(project.id),
        title="Repository Test Problem",
        description="Testing the repository layer",
        impact_level="high",
        urgency="high",
        priority="critical",
        category="Software Bug",
    )

    assert problem.id is not None
    assert problem.problem_number is not None
    assert problem.title == "Repository Test Problem"
    assert problem.priority == "critical"

    # Get by ID
    fetched = await repo.get_by_id(problem.id)
    assert fetched is not None
    assert fetched.title == "Repository Test Problem"

    # Update
    updated = await repo.update(problem.id, problem.version, status="in_investigation")
    assert updated is not None
    assert updated.status == "in_investigation"

    # List all for project
    problems = await repo.list_all(project_id=str(project.id))
    assert len(problems) == 1
    assert problems[0].id == problem.id

    # List with filters
    problems = await repo.list_all(project_id=str(project.id), status="in_investigation")
    assert len(problems) == 1

    problems = await repo.list_all(project_id=str(project.id), status="closed")
    assert len(problems) == 0


@pytest.mark.asyncio
@pytest.mark.integration
async def test_problem_repository_stats(async_db_session: Any) -> None:
    """Test ProblemRepository stats aggregation."""
    project = Project(
        id=str(uuid4()),
        name="Test Project",
        description="Test project for problem stats",
    )
    async_db_session.add(project)
    await async_db_session.flush()

    repo = ProblemRepository(async_db_session)

    # Create multiple problems with different statuses
    await repo.create(
        project_id=str(project.id),
        title="Open Problem 1",
        impact_level="critical",
        urgency="high",
        priority="critical",
    )
    await repo.create(
        project_id=str(project.id),
        title="Open Problem 2",
        impact_level="high",
        urgency="medium",
        priority="high",
    )

    # Create closed problem
    closed_problem = await repo.create(
        project_id=str(project.id),
        title="Closed Problem",
        impact_level="low",
        urgency="low",
        priority="low",
    )
    await repo.update(closed_problem.id, closed_problem.version, status="closed")

    # Get stats
    status_counts = await repo.count_by_status(str(project.id))
    priority_counts = await repo.count_by_priority(str(project.id))

    assert status_counts["open"] == COUNT_TWO
    assert status_counts["closed"] == 1
    assert priority_counts["critical"] == 1
    assert priority_counts["high"] == 1
    assert priority_counts["low"] == 1


@pytest.mark.asyncio
@pytest.mark.integration
async def test_process_repository_crud(async_db_session: Any) -> None:
    """Test ProcessRepository CRUD operations."""
    project = Project(
        id=str(uuid4()),
        name="Test Project",
        description="Test project for process repository",
    )
    async_db_session.add(project)
    await async_db_session.flush()

    repo = ProcessRepository(async_db_session)

    # Create a process
    process = await repo.create(
        project_id=str(project.id),
        name="Repository Test Process",
        description="Testing the process repository layer",
        category="operational",
        stages=[
            {"id": "1", "name": "Initiate", "order": 1, "required": True},
            {"id": "2", "name": "Review", "order": 2, "required": True},
        ],
        swimlanes=[
            {"id": "1", "name": "Requester", "role": "user"},
        ],
    )

    assert process.id is not None
    assert process.process_number is not None
    assert process.name == "Repository Test Process"
    assert process.status == "draft"  # Default status
    assert len(process.stages or []) == COUNT_TWO
    assert len(process.swimlanes or []) == 1

    # Get by ID
    fetched = await repo.get_by_id(process.id)
    assert fetched is not None
    assert fetched.name == "Repository Test Process"

    # Update
    updated = await repo.update(process.id, process.version, status="active")
    assert updated is not None
    assert updated.status == "active"

    # List all for project
    processes = await repo.list_all(project_id=str(project.id))
    assert len(processes) == 1
    assert processes[0].id == process.id

    # List with filters
    processes = await repo.list_all(project_id=str(project.id), status="active")
    assert len(processes) == 1

    processes = await repo.list_all(project_id=str(project.id), status="archived")
    assert len(processes) == 0


@pytest.mark.asyncio
@pytest.mark.integration
async def test_process_repository_stats(async_db_session: Any) -> None:
    """Test ProcessRepository stats aggregation."""
    project = Project(
        id=str(uuid4()),
        name="Test Project",
        description="Test project for process stats",
    )
    async_db_session.add(project)
    await async_db_session.flush()

    repo = ProcessRepository(async_db_session)

    # Create multiple processes
    p1 = await repo.create(
        project_id=str(project.id),
        name="Active Process 1",
        category="operational",
    )
    await repo.update(p1.id, p1.version, status="active")

    p2 = await repo.create(
        project_id=str(project.id),
        name="Active Process 2",
        category="support",
    )
    await repo.update(p2.id, p2.version, status="active")

    await repo.create(
        project_id=str(project.id),
        name="Draft Process",
        category="operational",
    )

    # Get stats
    status_counts = await repo.count_by_status(str(project.id))
    category_counts = await repo.count_by_category(str(project.id))

    assert status_counts["active"] == COUNT_TWO
    assert status_counts["draft"] == 1
    assert category_counts["operational"] == COUNT_TWO
    assert category_counts["support"] == 1
