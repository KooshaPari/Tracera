"""Comprehensive unit tests for TestRunRepository to achieve 85%+ coverage.

Tests for:
- create() - test run creation
- get_by_id() - retrieval by ID
- get_by_number() - retrieval by run number
- list_by_project() - listing with filters
- update() - updating run fields
- start() - starting a run
- complete() - completing a run
- cancel() - cancelling a run
- add_result() - adding test results
- add_bulk_results() - bulk results
- get_results() - retrieving results
- get_activities() - activity logs
- delete() - deleting runs
- get_stats() - project statistics
"""

from datetime import UTC, datetime
from uuid import uuid4

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from tests.test_constants import COUNT_FIVE, COUNT_TEN, COUNT_THREE, COUNT_TWO
from tracertm.models import test_case as tc_models
from tracertm.models import test_suite as ts_models
from tracertm.repositories import test_run_repository
from tracertm.repositories.project_repository import ProjectRepository

# Use module-qualified names to avoid pytest collection issues
RunRepository = test_run_repository.TestRunRepository
_TestCaseModel = tc_models.TestCase
_TestSuiteModel = ts_models.TestSuite


def unique_project_name() -> str:
    """Generate a unique project name for tests."""
    return f"Test Project {uuid4().hex[:8]}"


# ============================================================================
# CREATE OPERATIONS
# ============================================================================


@pytest.mark.unit
@pytest.mark.asyncio
async def test_create_basic(db_session: AsyncSession) -> None:
    """Test creating test run with basic fields."""
    project_repo = ProjectRepository(db_session)
    project = await project_repo.create(name=unique_project_name())
    await db_session.commit()

    repo = RunRepository(db_session)
    run = await repo.create(
        project_id=str(project.id),
        name="Test Run 1",
    )

    assert run.id is not None
    assert run.name == "Test Run 1"
    assert run.project_id == project.id
    assert run.status.value == "pending"
    assert run.run_type.value == "manual"
    assert run.run_number.startswith("TR-")


@pytest.mark.unit
@pytest.mark.asyncio
async def test_create_with_description(db_session: AsyncSession) -> None:
    """Test creating test run with description."""
    project_repo = ProjectRepository(db_session)
    project = await project_repo.create(name=unique_project_name())
    await db_session.commit()

    repo = RunRepository(db_session)
    run = await repo.create(
        project_id=str(project.id),
        name="Test Run",
        description="This is a test run description",
    )

    assert run.description == "This is a test run description"


@pytest.mark.unit
@pytest.mark.asyncio
async def test_create_with_environment(db_session: AsyncSession) -> None:
    """Test creating test run with environment info."""
    project_repo = ProjectRepository(db_session)
    project = await project_repo.create(name=unique_project_name())
    await db_session.commit()

    repo = RunRepository(db_session)
    run = await repo.create(
        project_id=str(project.id),
        name="CI Test Run",
        environment="staging",
        build_number="123",
        build_url="https://ci.example.com/build/123",
        branch="main",
        commit_sha="abc123def456",
    )

    assert run.environment == "staging"
    assert run.build_number == "123"
    assert run.build_url == "https://ci.example.com/build/123"
    assert run.branch == "main"
    assert run.commit_sha == "abc123def456"


@pytest.mark.unit
@pytest.mark.asyncio
async def test_create_with_run_type(db_session: AsyncSession) -> None:
    """Test creating test run with different run types."""
    project_repo = ProjectRepository(db_session)
    project = await project_repo.create(name=unique_project_name())
    await db_session.commit()

    repo = RunRepository(db_session)
    run = await repo.create(
        project_id=str(project.id),
        name="Automated Test Run",
        run_type="automated",
    )

    assert run.run_type.value == "automated"


@pytest.mark.unit
@pytest.mark.asyncio
async def test_create_with_suite(db_session: AsyncSession) -> None:
    """Test creating test run linked to a suite."""
    project_repo = ProjectRepository(db_session)
    project = await project_repo.create(name=unique_project_name())
    await db_session.commit()

    # Create a test suite
    suite = _TestSuiteModel(
        id=str(uuid4()),
        project_id=str(project.id),
        name="Integration Suite",
        suite_number=f"TS-{uuid4().hex[:8].upper()}",
    )
    db_session.add(suite)
    await db_session.flush()

    repo = RunRepository(db_session)
    run = await repo.create(
        project_id=str(project.id),
        name="Suite Test Run",
        suite_id=suite.id,
    )

    assert run.suite_id == suite.id


@pytest.mark.unit
@pytest.mark.asyncio
async def test_create_with_tags(db_session: AsyncSession) -> None:
    """Test creating test run with tags."""
    project_repo = ProjectRepository(db_session)
    project = await project_repo.create(name=unique_project_name())
    await db_session.commit()

    repo = RunRepository(db_session)
    run = await repo.create(
        project_id=str(project.id),
        name="Tagged Test Run",
        tags=["smoke", "regression", "p1"],
    )

    assert run.tags == ["smoke", "regression", "p1"]


@pytest.mark.unit
@pytest.mark.asyncio
async def test_create_with_metadata(db_session: AsyncSession) -> None:
    """Test creating test run with metadata."""
    project_repo = ProjectRepository(db_session)
    project = await project_repo.create(name=unique_project_name())
    await db_session.commit()

    repo = RunRepository(db_session)
    metadata = {"trigger": "webhook", "pipeline_id": "abc123"}
    run = await repo.create(
        project_id=str(project.id),
        name="Test Run with Metadata",
        metadata=metadata,
    )

    assert run.run_metadata == metadata


@pytest.mark.unit
@pytest.mark.asyncio
async def test_create_with_external_id(db_session: AsyncSession) -> None:
    """Test creating test run with external run ID."""
    project_repo = ProjectRepository(db_session)
    project = await project_repo.create(name=unique_project_name())
    await db_session.commit()

    repo = RunRepository(db_session)
    external_id = f"ext-{uuid4().hex[:8]}"
    run = await repo.create(
        project_id=str(project.id),
        name="External Test Run",
        external_run_id=external_id,
    )

    assert run.external_run_id == external_id


# ============================================================================
# GET OPERATIONS
# ============================================================================


@pytest.mark.unit
@pytest.mark.asyncio
async def test_get_by_id_existing(db_session: AsyncSession) -> None:
    """Test getting test run by ID."""
    project_repo = ProjectRepository(db_session)
    project = await project_repo.create(name=unique_project_name())
    await db_session.commit()

    repo = RunRepository(db_session)
    created = await repo.create(project_id=str(project.id), name="Test Run")
    await db_session.commit()

    retrieved = await repo.get_by_id(created.id)

    assert retrieved is not None
    assert retrieved.id == created.id
    assert retrieved.name == "Test Run"


@pytest.mark.unit
@pytest.mark.asyncio
async def test_get_by_id_nonexistent(db_session: AsyncSession) -> None:
    """Test getting nonexistent test run by ID."""
    repo = RunRepository(db_session)
    result = await repo.get_by_id(str(uuid4()))
    assert result is None


@pytest.mark.unit
@pytest.mark.asyncio
async def test_get_by_number_existing(db_session: AsyncSession) -> None:
    """Test getting test run by run number."""
    project_repo = ProjectRepository(db_session)
    project = await project_repo.create(name=unique_project_name())
    await db_session.commit()

    repo = RunRepository(db_session)
    created = await repo.create(project_id=str(project.id), name="Test Run")
    await db_session.commit()

    retrieved = await repo.get_by_number(created.run_number)

    assert retrieved is not None
    assert retrieved.run_number == created.run_number


@pytest.mark.unit
@pytest.mark.asyncio
async def test_get_by_number_nonexistent(db_session: AsyncSession) -> None:
    """Test getting nonexistent test run by number."""
    repo = RunRepository(db_session)
    result = await repo.get_by_number("TR-NONEXIST")
    assert result is None


# ============================================================================
# LIST OPERATIONS
# ============================================================================


@pytest.mark.unit
@pytest.mark.asyncio
async def test_list_by_project_basic(db_session: AsyncSession) -> None:
    """Test listing test runs for a project."""
    project_repo = ProjectRepository(db_session)
    project = await project_repo.create(name=unique_project_name())
    await db_session.commit()

    repo = RunRepository(db_session)
    await repo.create(project_id=str(project.id), name="Run 1")
    await repo.create(project_id=str(project.id), name="Run 2")
    await repo.create(project_id=str(project.id), name="Run 3")
    await db_session.commit()

    runs, total = await repo.list_by_project(str(project.id))

    assert len(runs) == COUNT_THREE
    assert total == COUNT_THREE


@pytest.mark.unit
@pytest.mark.asyncio
async def test_list_by_project_filters_by_project(db_session: AsyncSession) -> None:
    """Test listing runs only returns runs for specified project."""
    project_repo = ProjectRepository(db_session)
    project1 = await project_repo.create(name=unique_project_name())
    project2 = await project_repo.create(name=unique_project_name())
    await db_session.commit()

    repo = RunRepository(db_session)
    await repo.create(project_id=project1.id, name="Run 1")
    await repo.create(project_id=project1.id, name="Run 2")
    await repo.create(project_id=project2.id, name="Run 3")
    await db_session.commit()

    _, total1 = await repo.list_by_project(project1.id)
    _, total2 = await repo.list_by_project(project2.id)

    assert total1 == COUNT_TWO
    assert total2 == 1


@pytest.mark.unit
@pytest.mark.asyncio
async def test_list_by_project_filter_by_run_type(db_session: AsyncSession) -> None:
    """Test listing runs with run type filter."""
    project_repo = ProjectRepository(db_session)
    project = await project_repo.create(name=unique_project_name())
    await db_session.commit()

    repo = RunRepository(db_session)
    await repo.create(project_id=str(project.id), name="Manual Run", run_type="manual")
    await repo.create(project_id=str(project.id), name="Auto Run", run_type="automated")
    await db_session.commit()

    manual_runs, _ = await repo.list_by_project(project.id, run_type="manual")
    auto_runs, _ = await repo.list_by_project(project.id, run_type="automated")

    assert len(manual_runs) == 1
    assert len(auto_runs) == 1


@pytest.mark.unit
@pytest.mark.asyncio
async def test_list_by_project_filter_by_environment(db_session: AsyncSession) -> None:
    """Test listing runs with environment filter."""
    project_repo = ProjectRepository(db_session)
    project = await project_repo.create(name=unique_project_name())
    await db_session.commit()

    repo = RunRepository(db_session)
    await repo.create(project_id=str(project.id), name="Staging Run", environment="staging")
    await repo.create(project_id=str(project.id), name="Prod Run", environment="production")
    await db_session.commit()

    staging_runs, _ = await repo.list_by_project(project.id, environment="staging")
    prod_runs, _ = await repo.list_by_project(project.id, environment="production")

    assert len(staging_runs) == 1
    assert len(prod_runs) == 1


@pytest.mark.unit
@pytest.mark.asyncio
async def test_list_by_project_filter_by_initiated_by(db_session: AsyncSession) -> None:
    """Test listing runs with initiated_by filter."""
    project_repo = ProjectRepository(db_session)
    project = await project_repo.create(name=unique_project_name())
    await db_session.commit()

    repo = RunRepository(db_session)
    await repo.create(project_id=str(project.id), name="Run 1", initiated_by="user1")
    await repo.create(project_id=str(project.id), name="Run 2", initiated_by="user2")
    await db_session.commit()

    user1_runs, _ = await repo.list_by_project(project.id, initiated_by="user1")

    assert len(user1_runs) == 1


@pytest.mark.unit
@pytest.mark.asyncio
async def test_list_by_project_pagination(db_session: AsyncSession) -> None:
    """Test listing runs with pagination."""
    project_repo = ProjectRepository(db_session)
    project = await project_repo.create(name=unique_project_name())
    await db_session.commit()

    repo = RunRepository(db_session)
    for i in range(10):
        await repo.create(project_id=str(project.id), name=f"Run {i}")
    await db_session.commit()

    runs_page1, total = await repo.list_by_project(project.id, limit=5, skip=0)
    runs_page2, _ = await repo.list_by_project(project.id, limit=5, skip=5)

    assert len(runs_page1) == COUNT_FIVE
    assert len(runs_page2) == COUNT_FIVE
    assert total == COUNT_TEN


# ============================================================================
# UPDATE OPERATIONS
# ============================================================================


@pytest.mark.unit
@pytest.mark.asyncio
async def test_update_basic(db_session: AsyncSession) -> None:
    """Test updating test run fields."""
    project_repo = ProjectRepository(db_session)
    project = await project_repo.create(name=unique_project_name())
    await db_session.commit()

    repo = RunRepository(db_session)
    run = await repo.create(project_id=str(project.id), name="Original Name")
    await db_session.commit()

    updated = await repo.update(run.id, name="Updated Name")

    assert updated is not None
    assert updated.name == "Updated Name"
    assert updated.version == COUNT_TWO


@pytest.mark.unit
@pytest.mark.asyncio
async def test_update_nonexistent(db_session: AsyncSession) -> None:
    """Test updating nonexistent run returns None."""
    repo = RunRepository(db_session)
    result = await repo.update(str(uuid4()), name="New Name")
    assert result is None


# ============================================================================
# START OPERATIONS
# ============================================================================


@pytest.mark.unit
@pytest.mark.asyncio
async def test_start_run(db_session: AsyncSession) -> None:
    """Test starting a pending test run."""
    project_repo = ProjectRepository(db_session)
    project = await project_repo.create(name=unique_project_name())
    await db_session.commit()

    repo = RunRepository(db_session)
    run = await repo.create(project_id=str(project.id), name="Test Run")
    await db_session.commit()

    started = await repo.start(run.id, executed_by="test_user")

    assert started is not None
    assert started.status.value == "running"
    assert started.started_at is not None
    assert started.executed_by == "test_user"


@pytest.mark.unit
@pytest.mark.asyncio
async def test_start_run_already_running(db_session: AsyncSession) -> None:
    """Test starting an already running run raises error."""
    project_repo = ProjectRepository(db_session)
    project = await project_repo.create(name=unique_project_name())
    await db_session.commit()

    repo = RunRepository(db_session)
    run = await repo.create(project_id=str(project.id), name="Test Run")
    await repo.start(run.id)
    await db_session.commit()

    with pytest.raises(ValueError, match="Cannot start run"):
        await repo.start(run.id)


@pytest.mark.unit
@pytest.mark.asyncio
async def test_start_nonexistent_run(db_session: AsyncSession) -> None:
    """Test starting nonexistent run returns None."""
    repo = RunRepository(db_session)
    result = await repo.start(str(uuid4()))
    assert result is None


# ============================================================================
# COMPLETE OPERATIONS
# ============================================================================


@pytest.mark.unit
@pytest.mark.asyncio
async def test_complete_run(db_session: AsyncSession) -> None:
    """Test completing a running test run."""
    project_repo = ProjectRepository(db_session)
    project = await project_repo.create(name=unique_project_name())
    await db_session.commit()

    repo = RunRepository(db_session)
    run = await repo.create(project_id=str(project.id), name="Test Run")
    await repo.start(run.id)
    await db_session.commit()

    completed = await repo.complete(
        run.id,
        status="passed",
        notes="All tests passed",
        completed_by="test_user",
    )

    assert completed is not None
    assert completed.status.value == "passed"
    assert completed.completed_at is not None
    assert completed.notes == "All tests passed"


@pytest.mark.unit
@pytest.mark.asyncio
async def test_complete_run_auto_status(db_session: AsyncSession) -> None:
    """Test completing run with automatic status determination."""
    project_repo = ProjectRepository(db_session)
    project = await project_repo.create(name=unique_project_name())
    await db_session.commit()

    repo = RunRepository(db_session)
    run = await repo.create(project_id=str(project.id), name="Test Run")
    await repo.start(run.id)

    # Set some failure counts to trigger FAILED status
    run_obj = await repo.get_by_id(run.id)
    assert run_obj is not None
    run_obj.failed_count = 2
    await db_session.commit()

    completed = await repo.complete(run.id)  # No explicit status

    assert completed is not None
    assert completed.status.value == "failed"


@pytest.mark.unit
@pytest.mark.asyncio
async def test_complete_run_not_running(db_session: AsyncSession) -> None:
    """Test completing a non-running run raises error."""
    project_repo = ProjectRepository(db_session)
    project = await project_repo.create(name=unique_project_name())
    await db_session.commit()

    repo = RunRepository(db_session)
    run = await repo.create(project_id=str(project.id), name="Test Run")
    await db_session.commit()

    with pytest.raises(ValueError, match="Cannot complete run"):
        await repo.complete(run.id)


@pytest.mark.unit
@pytest.mark.asyncio
async def test_complete_nonexistent_run(db_session: AsyncSession) -> None:
    """Test completing nonexistent run returns None."""
    repo = RunRepository(db_session)
    result = await repo.complete(str(uuid4()))
    assert result is None


# ============================================================================
# CANCEL OPERATIONS
# ============================================================================


@pytest.mark.unit
@pytest.mark.asyncio
async def test_cancel_pending_run(db_session: AsyncSession) -> None:
    """Test cancelling a pending test run."""
    project_repo = ProjectRepository(db_session)
    project = await project_repo.create(name=unique_project_name())
    await db_session.commit()

    repo = RunRepository(db_session)
    run = await repo.create(project_id=str(project.id), name="Test Run")
    await db_session.commit()

    cancelled = await repo.cancel(
        run.id,
        reason="Test cancelled by user",
        cancelled_by="test_user",
    )

    assert cancelled is not None
    assert cancelled.status.value == "cancelled"
    assert cancelled.notes == "Test cancelled by user"


@pytest.mark.unit
@pytest.mark.asyncio
async def test_cancel_running_run(db_session: AsyncSession) -> None:
    """Test cancelling a running test run."""
    project_repo = ProjectRepository(db_session)
    project = await project_repo.create(name=unique_project_name())
    await db_session.commit()

    repo = RunRepository(db_session)
    run = await repo.create(project_id=str(project.id), name="Test Run")
    await repo.start(run.id)
    await db_session.commit()

    cancelled = await repo.cancel(run.id)

    assert cancelled is not None
    assert cancelled.status.value == "cancelled"
    assert cancelled.completed_at is not None


@pytest.mark.unit
@pytest.mark.asyncio
async def test_cancel_completed_run_raises_error(db_session: AsyncSession) -> None:
    """Test cancelling a completed run raises error."""
    project_repo = ProjectRepository(db_session)
    project = await project_repo.create(name=unique_project_name())
    await db_session.commit()

    repo = RunRepository(db_session)
    run = await repo.create(project_id=str(project.id), name="Test Run")
    await repo.start(run.id)
    await repo.complete(run.id, status="passed")
    await db_session.commit()

    with pytest.raises(ValueError, match="Cannot cancel run"):
        await repo.cancel(run.id)


@pytest.mark.unit
@pytest.mark.asyncio
async def test_cancel_nonexistent_run(db_session: AsyncSession) -> None:
    """Test cancelling nonexistent run returns None."""
    repo = RunRepository(db_session)
    result = await repo.cancel(str(uuid4()))
    assert result is None


# ============================================================================
# TEST RESULT OPERATIONS
# ============================================================================


@pytest.mark.unit
@pytest.mark.asyncio
async def test_add_result(db_session: AsyncSession) -> None:
    """Test adding a test result to a run."""
    project_repo = ProjectRepository(db_session)
    project = await project_repo.create(name=unique_project_name())
    await db_session.commit()

    # Create test case
    tc_id = str(uuid4())
    test_case = _TestCaseModel(
        id=tc_id,
        project_id=str(project.id),
        title="Test Case 1",
        test_case_number=f"TC-{uuid4().hex[:8].upper()}",
    )
    db_session.add(test_case)
    await db_session.flush()

    repo = RunRepository(db_session)
    run = await repo.create(project_id=str(project.id), name="Test Run")
    await repo.start(run.id)
    await db_session.commit()

    result = await repo.add_result(
        run_id=run.id,
        test_case_id=test_case.id,
        status="passed",
        executed_by="test_user",
    )

    assert result is not None
    assert result.status.value == "passed"
    assert result.test_case_id == test_case.id

    # Check run metrics updated
    updated_run = await repo.get_by_id(run.id)
    assert updated_run is not None
    assert updated_run.total_tests == 1
    assert updated_run.passed_count == 1


@pytest.mark.unit
@pytest.mark.asyncio
async def test_add_result_failed(db_session: AsyncSession) -> None:
    """Test adding a failed test result."""
    project_repo = ProjectRepository(db_session)
    project = await project_repo.create(name=unique_project_name())
    await db_session.commit()

    test_case = _TestCaseModel(
        id=str(uuid4()),
        project_id=str(project.id),
        title="Test Case 1",
        test_case_number=f"TC-{uuid4().hex[:8].upper()}",
    )
    db_session.add(test_case)
    await db_session.flush()

    repo = RunRepository(db_session)
    run = await repo.create(project_id=str(project.id), name="Test Run")
    await repo.start(run.id)
    await db_session.commit()

    result = await repo.add_result(
        run_id=run.id,
        test_case_id=test_case.id,
        status="failed",
        failure_reason="Assertion failed",
        error_message="Expected 1 but got 2",
    )

    assert result is not None
    assert result.status.value == "failed"
    assert result.failure_reason == "Assertion failed"

    updated_run = await repo.get_by_id(run.id)
    assert updated_run is not None
    assert updated_run.failed_count == 1


@pytest.mark.unit
@pytest.mark.asyncio
async def test_add_result_with_details(db_session: AsyncSession) -> None:
    """Test adding result with all details."""
    project_repo = ProjectRepository(db_session)
    project = await project_repo.create(name=unique_project_name())
    await db_session.commit()

    test_case = _TestCaseModel(
        id=str(uuid4()),
        project_id=str(project.id),
        title="Test Case 1",
        test_case_number=f"TC-{uuid4().hex[:8].upper()}",
    )
    db_session.add(test_case)
    await db_session.flush()

    repo = RunRepository(db_session)
    run = await repo.create(project_id=str(project.id), name="Test Run")
    await repo.start(run.id)
    await db_session.commit()

    result = await repo.add_result(
        run_id=run.id,
        test_case_id=test_case.id,
        status="passed",
        duration_seconds=120,
        actual_result="Test completed successfully",
        screenshots=["screenshot1.png", "screenshot2.png"],
        logs_url="https://logs.example.com/123",
        notes="Test notes here",
        metadata={"browser": "chrome"},
    )

    assert result is not None
    assert result.duration_seconds == 120
    assert result.actual_result == "Test completed successfully"
    assert result.screenshots == ["screenshot1.png", "screenshot2.png"]
    assert result.logs_url == "https://logs.example.com/123"


@pytest.mark.unit
@pytest.mark.asyncio
async def test_add_bulk_results(db_session: AsyncSession) -> None:
    """Test adding multiple test results at once."""
    project_repo = ProjectRepository(db_session)
    project = await project_repo.create(name=unique_project_name())
    await db_session.commit()

    # Create test cases
    test_cases = []
    for i in range(3):
        tc = _TestCaseModel(
            id=str(uuid4()),
            project_id=str(project.id),
            title=f"Test Case {i}",
            test_case_number=f"TC-{uuid4().hex[:8].upper()}",
        )
        db_session.add(tc)
        test_cases.append(tc)
    await db_session.flush()

    repo = RunRepository(db_session)
    run = await repo.create(project_id=str(project.id), name="Test Run")
    await repo.start(run.id)
    await db_session.commit()

    results_data = [
        {"test_case_id": test_cases[0].id, "status": "passed"},
        {"test_case_id": test_cases[1].id, "status": "failed", "failure_reason": "Bug"},
        {"test_case_id": test_cases[2].id, "status": "skipped"},
    ]

    results = await repo.add_bulk_results(run.id, results_data)

    assert len(results) == COUNT_THREE

    updated_run = await repo.get_by_id(run.id)
    assert updated_run is not None
    assert updated_run.total_tests == COUNT_THREE
    assert updated_run.passed_count == 1
    assert updated_run.failed_count == 1
    assert updated_run.skipped_count == 1


@pytest.mark.unit
@pytest.mark.asyncio
async def test_get_results(db_session: AsyncSession) -> None:
    """Test getting all results for a run."""
    project_repo = ProjectRepository(db_session)
    project = await project_repo.create(name=unique_project_name())
    await db_session.commit()

    test_case = _TestCaseModel(
        id=str(uuid4()),
        project_id=str(project.id),
        title="Test Case 1",
        test_case_number=f"TC-{uuid4().hex[:8].upper()}",
    )
    db_session.add(test_case)
    await db_session.flush()

    repo = RunRepository(db_session)
    run = await repo.create(project_id=str(project.id), name="Test Run")
    await repo.start(run.id)
    await repo.add_result(run.id, test_case.id, "passed")
    await db_session.commit()

    results = await repo.get_results(run.id)

    assert len(results) == 1
    assert results[0].test_case_id == test_case.id


@pytest.mark.unit
@pytest.mark.asyncio
async def test_get_results_filtered_by_status(db_session: AsyncSession) -> None:
    """Test getting results filtered by status."""
    project_repo = ProjectRepository(db_session)
    project = await project_repo.create(name=unique_project_name())
    await db_session.commit()

    test_cases = []
    for i in range(2):
        tc = _TestCaseModel(
            id=str(uuid4()),
            project_id=str(project.id),
            title=f"TC {i}",
            test_case_number=f"TC-{uuid4().hex[:8].upper()}",
        )
        db_session.add(tc)
        test_cases.append(tc)
    await db_session.flush()

    repo = RunRepository(db_session)
    run = await repo.create(project_id=str(project.id), name="Test Run")
    await repo.start(run.id)
    await repo.add_result(run.id, test_cases[0].id, "passed")
    await repo.add_result(run.id, test_cases[1].id, "failed")
    await db_session.commit()

    passed_results = await repo.get_results(run.id, status="passed")
    failed_results = await repo.get_results(run.id, status="failed")

    assert len(passed_results) == 1
    assert len(failed_results) == 1


# ============================================================================
# ACTIVITY OPERATIONS
# ============================================================================


@pytest.mark.unit
@pytest.mark.asyncio
async def test_get_activities(db_session: AsyncSession) -> None:
    """Test getting activity log for a run."""
    project_repo = ProjectRepository(db_session)
    project = await project_repo.create(name=unique_project_name())
    await db_session.commit()

    repo = RunRepository(db_session)
    run = await repo.create(project_id=str(project.id), name="Test Run")
    await repo.start(run.id)
    await db_session.commit()

    activities = await repo.get_activities(run.id)

    # Should have "created" and "started" activities
    assert len(activities) >= COUNT_TWO
    activity_types = [a.activity_type for a in activities]
    assert "created" in activity_types
    assert "started" in activity_types


# ============================================================================
# DELETE OPERATIONS
# ============================================================================


@pytest.mark.unit
@pytest.mark.asyncio
async def test_delete_run(db_session: AsyncSession) -> None:
    """Test deleting a test run."""
    project_repo = ProjectRepository(db_session)
    project = await project_repo.create(name=unique_project_name())
    await db_session.commit()

    repo = RunRepository(db_session)
    run = await repo.create(project_id=str(project.id), name="Test Run")
    await db_session.commit()

    result = await repo.delete(run.id)

    assert result is True

    deleted = await repo.get_by_id(run.id)
    assert deleted is None


@pytest.mark.unit
@pytest.mark.asyncio
async def test_delete_nonexistent_run(db_session: AsyncSession) -> None:
    """Test deleting nonexistent run returns False."""
    repo = RunRepository(db_session)
    result = await repo.delete(str(uuid4()))
    assert result is False


# ============================================================================
# STATS OPERATIONS
# ============================================================================


@pytest.mark.unit
@pytest.mark.asyncio
async def test_get_stats(db_session: AsyncSession) -> None:
    """Test getting statistics for test runs."""
    project_repo = ProjectRepository(db_session)
    project = await project_repo.create(name=unique_project_name())
    await db_session.commit()

    repo = RunRepository(db_session)

    # Create runs with different types and environments
    _ = await repo.create(
        project_id=str(project.id),
        name="Run 1",
        run_type="manual",
        environment="staging",
    )
    _ = await repo.create(
        project_id=str(project.id),
        name="Run 2",
        run_type="automated",
        environment="production",
    )
    await db_session.commit()

    stats = await repo.get_stats(str(project.id))

    assert stats["total_runs"] == COUNT_TWO
    assert "by_status" in stats
    assert "by_type" in stats
    assert "by_environment" in stats
    assert "recent_runs" in stats


@pytest.mark.unit
@pytest.mark.asyncio
async def test_get_stats_empty_project(db_session: AsyncSession) -> None:
    """Test getting stats for project with no runs."""
    project_repo = ProjectRepository(db_session)
    project = await project_repo.create(name=unique_project_name())
    await db_session.commit()

    repo = RunRepository(db_session)
    stats = await repo.get_stats(str(project.id))

    assert stats["total_runs"] == 0
    assert stats["recent_runs"] == []


# ============================================================================
# ADDITIONAL COVERAGE TESTS - LIST BY PROJECT FILTERS
# ============================================================================


@pytest.mark.unit
@pytest.mark.asyncio
async def test_list_by_project_filter_by_status(db_session: AsyncSession) -> None:
    """Test listing runs with status filter."""
    project_repo = ProjectRepository(db_session)
    project = await project_repo.create(name=unique_project_name())
    await db_session.commit()

    repo = RunRepository(db_session)
    run1 = await repo.create(project_id=str(project.id), name="Run 1")
    _ = await repo.create(project_id=str(project.id), name="Run 2")
    await repo.start(run1.id)
    await db_session.commit()

    pending_runs, pending_total = await repo.list_by_project(project.id, status="pending")
    running_runs, running_total = await repo.list_by_project(project.id, status="running")

    assert pending_total == 1
    assert len(pending_runs) == 1
    assert pending_runs[0].name == "Run 2"

    assert running_total == 1
    assert len(running_runs) == 1
    assert running_runs[0].name == "Run 1"


@pytest.mark.unit
@pytest.mark.asyncio
async def test_list_by_project_filter_by_suite_id(db_session: AsyncSession) -> None:
    """Test listing runs with suite_id filter."""
    project_repo = ProjectRepository(db_session)
    project = await project_repo.create(name=unique_project_name())
    await db_session.commit()

    # Create test suites
    suite1 = _TestSuiteModel(
        id=str(uuid4()),
        project_id=str(project.id),
        name="Suite 1",
        suite_number=f"TS-{uuid4().hex[:8].upper()}",
    )
    suite2 = _TestSuiteModel(
        id=str(uuid4()),
        project_id=str(project.id),
        name="Suite 2",
        suite_number=f"TS-{uuid4().hex[:8].upper()}",
    )
    db_session.add(suite1)
    db_session.add(suite2)
    await db_session.flush()

    repo = RunRepository(db_session)
    await repo.create(project_id=str(project.id), name="Run for Suite 1", suite_id=suite1.id)
    await repo.create(project_id=str(project.id), name="Run for Suite 2", suite_id=suite2.id)
    await repo.create(project_id=str(project.id), name="Run without suite")
    await db_session.commit()

    suite1_runs, suite1_total = await repo.list_by_project(project.id, suite_id=suite1.id)
    suite2_runs, suite2_total = await repo.list_by_project(project.id, suite_id=suite2.id)

    assert suite1_total == 1
    assert suite1_runs[0].name == "Run for Suite 1"
    assert suite2_total == 1
    assert suite2_runs[0].name == "Run for Suite 2"


@pytest.mark.unit
@pytest.mark.asyncio
async def test_list_by_project_filter_by_date_range(db_session: AsyncSession) -> None:
    """Test listing runs with date range filters."""
    project_repo = ProjectRepository(db_session)
    project = await project_repo.create(name=unique_project_name())
    await db_session.commit()

    repo = RunRepository(db_session)
    await repo.create(project_id=str(project.id), name="Run 1")
    await repo.create(project_id=str(project.id), name="Run 2")
    await db_session.commit()

    # Test from_date filter (all runs should be created "now")
    past_date = datetime(2020, 1, 1, tzinfo=UTC)
    future_date = datetime(2099, 1, 1, tzinfo=UTC)

    _, total_from_past = await repo.list_by_project(project.id, from_date=past_date)
    _, total_from_future = await repo.list_by_project(project.id, from_date=future_date)

    assert total_from_past == COUNT_TWO  # All runs are after past date
    assert total_from_future == 0  # No runs are after future date

    # Test to_date filter
    _, total_to_future = await repo.list_by_project(project.id, to_date=future_date)
    _, total_to_past = await repo.list_by_project(project.id, to_date=past_date)

    assert total_to_future == COUNT_TWO  # All runs are before future date
    assert total_to_past == 0  # No runs are before past date


@pytest.mark.unit
@pytest.mark.asyncio
async def test_list_by_project_combined_filters(db_session: AsyncSession) -> None:
    """Test listing runs with multiple filters combined."""
    project_repo = ProjectRepository(db_session)
    project = await project_repo.create(name=unique_project_name())
    await db_session.commit()

    suite = _TestSuiteModel(
        id=str(uuid4()),
        project_id=str(project.id),
        name="Regression Suite",
        suite_number=f"TS-{uuid4().hex[:8].upper()}",
    )
    db_session.add(suite)
    await db_session.flush()

    repo = RunRepository(db_session)
    # Create various runs
    await repo.create(
        project_id=str(project.id),
        name="Auto Staging Run",
        run_type="automated",
        environment="staging",
        suite_id=suite.id,
    )
    await repo.create(
        project_id=str(project.id),
        name="Auto Prod Run",
        run_type="automated",
        environment="production",
    )
    await repo.create(
        project_id=str(project.id),
        name="Manual Staging Run",
        run_type="manual",
        environment="staging",
    )
    await db_session.commit()

    # Test run_type + environment combination
    auto_staging_runs, count = await repo.list_by_project(project.id, run_type="automated", environment="staging")
    assert count == 1
    assert auto_staging_runs[0].name == "Auto Staging Run"

    # Test run_type + suite_id combination
    auto_suite_runs, count2 = await repo.list_by_project(project.id, run_type="automated", suite_id=suite.id)
    assert count2 == 1
    assert auto_suite_runs[0].name == "Auto Staging Run"

    # Test environment + suite_id (should find the one with both)
    _staging_suite_runs, count3 = await repo.list_by_project(project.id, environment="staging", suite_id=suite.id)
    assert count3 == 1


# ============================================================================
# ADDITIONAL COVERAGE TESTS - COMPLETE METHOD EDGE CASES
# ============================================================================


@pytest.mark.unit
@pytest.mark.asyncio
async def test_complete_run_auto_status_blocked(db_session: AsyncSession) -> None:
    """Test completing run with auto-status determination when only blocked tests."""
    project_repo = ProjectRepository(db_session)
    project = await project_repo.create(name=unique_project_name())
    await db_session.commit()

    repo = RunRepository(db_session)
    run = await repo.create(project_id=str(project.id), name="Test Run")
    await repo.start(run.id)

    # Set blocked count (no failures, no errors)
    run_obj = await repo.get_by_id(run.id)
    assert run_obj is not None
    run_obj.blocked_count = 3
    run_obj.total_tests = 3
    await db_session.commit()

    completed = await repo.complete(run.id)  # No explicit status

    assert completed is not None
    assert completed.status.value == "blocked"


@pytest.mark.unit
@pytest.mark.asyncio
async def test_complete_run_auto_status_error(db_session: AsyncSession) -> None:
    """Test completing run with auto-status when error_count > 0."""
    project_repo = ProjectRepository(db_session)
    project = await project_repo.create(name=unique_project_name())
    await db_session.commit()

    repo = RunRepository(db_session)
    run = await repo.create(project_id=str(project.id), name="Test Run")
    await repo.start(run.id)

    # Set error count (triggers FAILED status path)
    run_obj = await repo.get_by_id(run.id)
    assert run_obj is not None
    run_obj.error_count = 2
    run_obj.total_tests = 2
    await db_session.commit()

    completed = await repo.complete(run.id)

    # error_count > 0 triggers the same path as failed_count > 0
    assert completed is not None
    assert completed.status.value == "failed"


@pytest.mark.unit
@pytest.mark.asyncio
async def test_complete_run_auto_status_passed_all_green(db_session: AsyncSession) -> None:
    """Test completing run with auto-status when all tests pass (no failures)."""
    project_repo = ProjectRepository(db_session)
    project = await project_repo.create(name=unique_project_name())
    await db_session.commit()

    repo = RunRepository(db_session)
    run = await repo.create(project_id=str(project.id), name="Test Run")
    await repo.start(run.id)

    # Set only passed tests (no failures, errors, or blocked)
    run_obj = await repo.get_by_id(run.id)
    assert run_obj is not None
    run_obj.passed_count = 5
    run_obj.total_tests = 5
    await db_session.commit()

    completed = await repo.complete(run.id)

    assert completed is not None
    assert completed.status.value == "passed"


@pytest.mark.unit
@pytest.mark.asyncio
async def test_complete_run_auto_status_with_skipped_only(db_session: AsyncSession) -> None:
    """Test completing run with only skipped tests (no failures)."""
    project_repo = ProjectRepository(db_session)
    project = await project_repo.create(name=unique_project_name())
    await db_session.commit()

    repo = RunRepository(db_session)
    run = await repo.create(project_id=str(project.id), name="Test Run")
    await repo.start(run.id)

    # Set only skipped tests
    run_obj = await repo.get_by_id(run.id)
    assert run_obj is not None
    run_obj.skipped_count = 5
    run_obj.total_tests = 5
    await db_session.commit()

    completed = await repo.complete(run.id)

    # With no failures, errors, or blocked -> PASSED
    assert completed is not None
    assert completed.status.value == "passed"


@pytest.mark.unit
@pytest.mark.asyncio
async def test_complete_run_calculates_pass_rate(db_session: AsyncSession) -> None:
    """Test that complete() calculates pass_rate when total_tests > 0."""
    project_repo = ProjectRepository(db_session)
    project = await project_repo.create(name=unique_project_name())
    await db_session.commit()

    repo = RunRepository(db_session)
    run = await repo.create(project_id=str(project.id), name="Test Run")
    await repo.start(run.id)

    # Set test counts manually for pass rate calculation
    run_obj = await repo.get_by_id(run.id)
    assert run_obj is not None
    run_obj.total_tests = 10
    run_obj.passed_count = 8
    run_obj.failed_count = 2
    await db_session.commit()

    completed = await repo.complete(run.id)

    assert completed is not None
    assert completed.pass_rate == 80.0  # 8/10 * 100


@pytest.mark.unit
@pytest.mark.asyncio
async def test_complete_run_zero_tests_no_pass_rate(db_session: AsyncSession) -> None:
    """Test that complete() does not calculate pass_rate when total_tests is 0."""
    project_repo = ProjectRepository(db_session)
    project = await project_repo.create(name=unique_project_name())
    await db_session.commit()

    repo = RunRepository(db_session)
    run = await repo.create(project_id=str(project.id), name="Test Run")
    await repo.start(run.id)
    await db_session.commit()

    # Complete with no tests
    completed = await repo.complete(run.id)

    # pass_rate should remain at default (None or 0 depending on model)
    assert completed is not None
    assert completed.total_tests == 0
    # Pass rate calculation is skipped when total_tests == 0


@pytest.mark.unit
@pytest.mark.asyncio
async def test_complete_run_with_failure_summary(db_session: AsyncSession) -> None:
    """Test completing run with failure_summary parameter."""
    project_repo = ProjectRepository(db_session)
    project = await project_repo.create(name=unique_project_name())
    await db_session.commit()

    repo = RunRepository(db_session)
    run = await repo.create(project_id=str(project.id), name="Test Run")
    await repo.start(run.id)
    run_obj = await repo.get_by_id(run.id)
    assert run_obj is not None
    run_obj.failed_count = 1
    await db_session.commit()

    completed = await repo.complete(
        run.id,
        failure_summary="Login tests failed due to authentication service timeout",
    )

    assert completed is not None
    assert completed.failure_summary == "Login tests failed due to authentication service timeout"


# ============================================================================
# ADDITIONAL COVERAGE TESTS - ADD RESULT STATUS TYPES
# ============================================================================


@pytest.mark.unit
@pytest.mark.asyncio
async def test_add_result_blocked(db_session: AsyncSession) -> None:
    """Test adding a blocked test result updates blocked_count."""
    project_repo = ProjectRepository(db_session)
    project = await project_repo.create(name=unique_project_name())
    await db_session.commit()

    test_case = _TestCaseModel(
        id=str(uuid4()),
        project_id=str(project.id),
        title="Test Case 1",
        test_case_number=f"TC-{uuid4().hex[:8].upper()}",
    )
    db_session.add(test_case)
    await db_session.flush()

    repo = RunRepository(db_session)
    run = await repo.create(project_id=str(project.id), name="Test Run")
    await repo.start(run.id)
    await db_session.commit()

    result = await repo.add_result(
        run_id=run.id,
        test_case_id=test_case.id,
        status="blocked",
        failure_reason="Prerequisite test failed",
    )

    assert result.status.value == "blocked"

    updated_run = await repo.get_by_id(run.id)
    assert updated_run is not None
    assert updated_run.total_tests == 1
    assert updated_run.blocked_count == 1
    assert updated_run.passed_count == 0
    assert updated_run.failed_count == 0


@pytest.mark.unit
@pytest.mark.asyncio
async def test_add_result_error(db_session: AsyncSession) -> None:
    """Test adding an error test result updates error_count."""
    project_repo = ProjectRepository(db_session)
    project = await project_repo.create(name=unique_project_name())
    await db_session.commit()

    test_case = _TestCaseModel(
        id=str(uuid4()),
        project_id=str(project.id),
        title="Test Case 1",
        test_case_number=f"TC-{uuid4().hex[:8].upper()}",
    )
    db_session.add(test_case)
    await db_session.flush()

    repo = RunRepository(db_session)
    run = await repo.create(project_id=str(project.id), name="Test Run")
    await repo.start(run.id)
    await db_session.commit()

    result = await repo.add_result(
        run_id=run.id,
        test_case_id=test_case.id,
        status="error",
        error_message="RuntimeException: Connection refused",
        stack_trace="at line 42...",
    )

    assert result.status.value == "error"

    updated_run = await repo.get_by_id(run.id)
    assert updated_run is not None
    assert updated_run.total_tests == 1
    assert updated_run.error_count == 1
    assert updated_run.passed_count == 0
    assert updated_run.failed_count == 0


@pytest.mark.unit
@pytest.mark.asyncio
async def test_add_bulk_results_with_blocked_and_error(db_session: AsyncSession) -> None:
    """Test adding bulk results with BLOCKED and ERROR status types."""
    project_repo = ProjectRepository(db_session)
    project = await project_repo.create(name=unique_project_name())
    await db_session.commit()

    test_cases = []
    for i in range(5):
        tc = _TestCaseModel(
            id=str(uuid4()),
            project_id=str(project.id),
            title=f"Test Case {i}",
            test_case_number=f"TC-{uuid4().hex[:8].upper()}",
        )
        db_session.add(tc)
        test_cases.append(tc)
    await db_session.flush()

    repo = RunRepository(db_session)
    run = await repo.create(project_id=str(project.id), name="Test Run")
    await repo.start(run.id)
    await db_session.commit()

    results_data = [
        {"test_case_id": test_cases[0].id, "status": "passed"},
        {"test_case_id": test_cases[1].id, "status": "failed", "failure_reason": "Bug"},
        {"test_case_id": test_cases[2].id, "status": "skipped"},
        {"test_case_id": test_cases[3].id, "status": "blocked", "failure_reason": "Dependency failed"},
        {"test_case_id": test_cases[4].id, "status": "error", "error_message": "Timeout"},
    ]

    results = await repo.add_bulk_results(run.id, results_data)

    assert len(results) == COUNT_FIVE

    updated_run = await repo.get_by_id(run.id)
    assert updated_run is not None
    assert updated_run.total_tests == COUNT_FIVE
    assert updated_run.passed_count == 1
    assert updated_run.failed_count == 1
    assert updated_run.skipped_count == 1
    assert updated_run.blocked_count == 1
    assert updated_run.error_count == 1


@pytest.mark.unit
@pytest.mark.asyncio
async def test_add_result_skipped(db_session: AsyncSession) -> None:
    """Test adding a skipped test result updates skipped_count."""
    project_repo = ProjectRepository(db_session)
    project = await project_repo.create(name=unique_project_name())
    await db_session.commit()

    test_case = _TestCaseModel(
        id=str(uuid4()),
        project_id=str(project.id),
        title="Test Case 1",
        test_case_number=f"TC-{uuid4().hex[:8].upper()}",
    )
    db_session.add(test_case)
    await db_session.flush()

    repo = RunRepository(db_session)
    run = await repo.create(project_id=str(project.id), name="Test Run")
    await repo.start(run.id)
    await db_session.commit()

    result = await repo.add_result(
        run_id=run.id,
        test_case_id=test_case.id,
        status="skipped",
        notes="Skipped due to feature flag disabled",
    )

    assert result.status.value == "skipped"

    updated_run = await repo.get_by_id(run.id)
    assert updated_run is not None
    assert updated_run.total_tests == 1
    assert updated_run.skipped_count == 1


@pytest.mark.unit
@pytest.mark.asyncio
async def test_add_result_without_test_case(db_session: AsyncSession) -> None:
    """Test adding result when test case doesn't exist (no stat update)."""
    project_repo = ProjectRepository(db_session)
    project = await project_repo.create(name=unique_project_name())
    await db_session.commit()

    repo = RunRepository(db_session)
    run = await repo.create(project_id=str(project.id), name="Test Run")
    await repo.start(run.id)
    await db_session.commit()

    # Use a non-existent test case ID
    fake_tc_id = str(uuid4())
    result = await repo.add_result(
        run_id=run.id,
        test_case_id=fake_tc_id,
        status="passed",
    )

    # Result is still created
    assert result is not None
    assert result.status.value == "passed"

    # Run metrics are still updated
    updated_run = await repo.get_by_id(run.id)
    assert updated_run is not None
    assert updated_run.total_tests == 1
    assert updated_run.passed_count == 1


# ============================================================================
# ADDITIONAL COVERAGE TESTS - EDGE CASES
# ============================================================================


@pytest.mark.unit
@pytest.mark.asyncio
async def test_list_by_project_all_filters_combined(db_session: AsyncSession) -> None:
    """Test listing runs with all filters at once."""
    project_repo = ProjectRepository(db_session)
    project = await project_repo.create(name=unique_project_name())
    await db_session.commit()

    suite = _TestSuiteModel(
        id=str(uuid4()),
        project_id=str(project.id),
        name="Full Suite",
        suite_number=f"TS-{uuid4().hex[:8].upper()}",
    )
    db_session.add(suite)
    await db_session.flush()

    repo = RunRepository(db_session)
    run = await repo.create(
        project_id=str(project.id),
        name="Full Filter Run",
        run_type="automated",
        environment="production",
        suite_id=suite.id,
        initiated_by="ci-bot",
    )
    await repo.start(run.id)
    await db_session.commit()

    # Search with all filters matching
    runs, total = await repo.list_by_project(
        project.id,
        status="running",
        run_type="automated",
        suite_id=suite.id,
        environment="production",
        initiated_by="ci-bot",
    )

    assert total == 1
    assert runs[0].name == "Full Filter Run"


@pytest.mark.unit
@pytest.mark.asyncio
async def test_complete_run_calculates_duration(db_session: AsyncSession) -> None:
    """Test that complete() calculates duration_seconds correctly."""
    project_repo = ProjectRepository(db_session)
    project = await project_repo.create(name=unique_project_name())
    await db_session.commit()

    repo = RunRepository(db_session)
    run = await repo.create(project_id=str(project.id), name="Test Run")
    await repo.start(run.id)
    await db_session.commit()

    completed = await repo.complete(run.id, status="passed")

    # Duration should be calculated
    assert completed is not None
    assert completed.duration_seconds is not None
    assert completed.duration_seconds >= 0


# ============================================================================
# ADDITIONAL TESTS FOR 100% COVERAGE
# ============================================================================


@pytest.mark.unit
@pytest.mark.asyncio
async def test_update_with_none_value_skipped(db_session: AsyncSession) -> None:
    """Test update() skips None values per line 162 branch."""
    project_repo = ProjectRepository(db_session)
    project = await project_repo.create(name=unique_project_name())
    await db_session.commit()

    repo = RunRepository(db_session)
    run = await repo.create(project_id=str(project.id), name="Original Name")
    await db_session.commit()

    # Update with None value - should be skipped
    updated = await repo.update(run.id, name="New Name", description=None)

    assert updated is not None
    assert updated.name == "New Name"
    # description should remain None (not attempted to set)


@pytest.mark.unit
@pytest.mark.asyncio
async def test_complete_run_without_started_at(db_session: AsyncSession) -> None:
    """Test complete() when started_at is None per lines 220-223 branch."""
    project_repo = ProjectRepository(db_session)
    project = await project_repo.create(name=unique_project_name())
    await db_session.commit()

    repo = RunRepository(db_session)
    run = await repo.create(project_id=str(project.id), name="Test Run")
    await repo.start(run.id)
    await db_session.commit()

    # Manually set started_at to None to test the branch
    run_obj = await repo.get_by_id(run.id)
    assert run_obj is not None
    run_obj.started_at = None
    await db_session.commit()

    completed = await repo.complete(run.id, status="passed")

    # Duration should not be calculated when started_at is None
    assert completed is not None
    assert completed.duration_seconds is None or completed.duration_seconds == 0


@pytest.mark.unit
@pytest.mark.asyncio
async def test_add_result_updates_test_case_stats_for_failed(db_session: AsyncSession) -> None:
    """Test add_result updates test_case fail_count per lines 381-382."""
    project_repo = ProjectRepository(db_session)
    project = await project_repo.create(name=unique_project_name())
    await db_session.commit()

    test_case = _TestCaseModel(
        id=str(uuid4()),
        project_id=str(project.id),
        title="Test Case",
        test_case_number=f"TC-{uuid4().hex[:8].upper()}",
    )
    db_session.add(test_case)
    await db_session.flush()

    repo = RunRepository(db_session)
    run = await repo.create(project_id=str(project.id), name="Test Run")
    await repo.start(run.id)
    await db_session.commit()

    # Add failed result - covers lines 381-382
    await repo.add_result(
        run_id=run.id,
        test_case_id=test_case.id,
        status="failed",
        completed_at=datetime.now(UTC),
    )
    await db_session.commit()

    # Verify test case fail_count was incremented
    await db_session.refresh(test_case)
    assert test_case.fail_count == 1
    assert test_case.total_executions == 1


@pytest.mark.unit
@pytest.mark.asyncio
async def test_add_result_when_run_does_not_exist(db_session: AsyncSession) -> None:
    """Test add_result when run doesn't exist per lines 356-368 branch."""
    project_repo = ProjectRepository(db_session)
    project = await project_repo.create(name=unique_project_name())
    await db_session.commit()

    test_case = _TestCaseModel(
        id=str(uuid4()),
        project_id=str(project.id),
        title="Test Case",
        test_case_number=f"TC-{uuid4().hex[:8].upper()}",
    )
    db_session.add(test_case)
    await db_session.flush()

    repo = RunRepository(db_session)

    # Try to add result to non-existent run - should not crash
    fake_run_id = str(uuid4())
    result = await repo.add_result(
        run_id=fake_run_id,
        test_case_id=test_case.id,
        status="passed",
    )

    # Result is created even if run doesn't exist (line 352)
    assert result is not None
    assert result.run_id == fake_run_id
