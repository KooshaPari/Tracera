"""
Comprehensive unit tests for TestRunRepository to achieve 85%+ coverage.

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

from datetime import datetime, timezone
from uuid import uuid4

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from tracertm.repositories.project_repository import ProjectRepository
from tracertm.repositories import test_run_repository
from tracertm.models import test_case as tc_models
from tracertm.models import test_suite as ts_models

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
async def test_create_basic(db_session: AsyncSession):
    """Test creating test run with basic fields."""
    project_repo = ProjectRepository(db_session)
    project = await project_repo.create(name=unique_project_name())
    await db_session.commit()

    repo = RunRepository(db_session)
    run = await repo.create(
        project_id=project.id,
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
async def test_create_with_description(db_session: AsyncSession):
    """Test creating test run with description."""
    project_repo = ProjectRepository(db_session)
    project = await project_repo.create(name=unique_project_name())
    await db_session.commit()

    repo = RunRepository(db_session)
    run = await repo.create(
        project_id=project.id,
        name="Test Run",
        description="This is a test run description",
    )

    assert run.description == "This is a test run description"


@pytest.mark.unit
@pytest.mark.asyncio
async def test_create_with_environment(db_session: AsyncSession):
    """Test creating test run with environment info."""
    project_repo = ProjectRepository(db_session)
    project = await project_repo.create(name=unique_project_name())
    await db_session.commit()

    repo = RunRepository(db_session)
    run = await repo.create(
        project_id=project.id,
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
async def test_create_with_run_type(db_session: AsyncSession):
    """Test creating test run with different run types."""
    project_repo = ProjectRepository(db_session)
    project = await project_repo.create(name=unique_project_name())
    await db_session.commit()

    repo = RunRepository(db_session)
    run = await repo.create(
        project_id=project.id,
        name="Automated Test Run",
        run_type="automated",
    )

    assert run.run_type.value == "automated"


@pytest.mark.unit
@pytest.mark.asyncio
async def test_create_with_suite(db_session: AsyncSession):
    """Test creating test run linked to a suite."""
    project_repo = ProjectRepository(db_session)
    project = await project_repo.create(name=unique_project_name())
    await db_session.commit()

    # Create a test suite
    suite = _TestSuiteModel(
        id=str(uuid4()),
        project_id=project.id,
        name="Integration Suite",
        suite_number=f"TS-{uuid4().hex[:8].upper()}",
    )
    db_session.add(suite)
    await db_session.flush()

    repo = RunRepository(db_session)
    run = await repo.create(
        project_id=project.id,
        name="Suite Test Run",
        suite_id=suite.id,
    )

    assert run.suite_id == suite.id


@pytest.mark.unit
@pytest.mark.asyncio
async def test_create_with_tags(db_session: AsyncSession):
    """Test creating test run with tags."""
    project_repo = ProjectRepository(db_session)
    project = await project_repo.create(name=unique_project_name())
    await db_session.commit()

    repo = RunRepository(db_session)
    run = await repo.create(
        project_id=project.id,
        name="Tagged Test Run",
        tags=["smoke", "regression", "p1"],
    )

    assert run.tags == ["smoke", "regression", "p1"]


@pytest.mark.unit
@pytest.mark.asyncio
async def test_create_with_metadata(db_session: AsyncSession):
    """Test creating test run with metadata."""
    project_repo = ProjectRepository(db_session)
    project = await project_repo.create(name=unique_project_name())
    await db_session.commit()

    repo = RunRepository(db_session)
    metadata = {"trigger": "webhook", "pipeline_id": "abc123"}
    run = await repo.create(
        project_id=project.id,
        name="Test Run with Metadata",
        metadata=metadata,
    )

    assert run.run_metadata == metadata


@pytest.mark.unit
@pytest.mark.asyncio
async def test_create_with_external_id(db_session: AsyncSession):
    """Test creating test run with external run ID."""
    project_repo = ProjectRepository(db_session)
    project = await project_repo.create(name=unique_project_name())
    await db_session.commit()

    repo = RunRepository(db_session)
    external_id = f"ext-{uuid4().hex[:8]}"
    run = await repo.create(
        project_id=project.id,
        name="External Test Run",
        external_run_id=external_id,
    )

    assert run.external_run_id == external_id


# ============================================================================
# GET OPERATIONS
# ============================================================================


@pytest.mark.unit
@pytest.mark.asyncio
async def test_get_by_id_existing(db_session: AsyncSession):
    """Test getting test run by ID."""
    project_repo = ProjectRepository(db_session)
    project = await project_repo.create(name=unique_project_name())
    await db_session.commit()

    repo = RunRepository(db_session)
    created = await repo.create(project_id=project.id, name="Test Run")
    await db_session.commit()

    retrieved = await repo.get_by_id(created.id)

    assert retrieved is not None
    assert retrieved.id == created.id
    assert retrieved.name == "Test Run"


@pytest.mark.unit
@pytest.mark.asyncio
async def test_get_by_id_nonexistent(db_session: AsyncSession):
    """Test getting nonexistent test run by ID."""
    repo = RunRepository(db_session)
    result = await repo.get_by_id(str(uuid4()))
    assert result is None


@pytest.mark.unit
@pytest.mark.asyncio
async def test_get_by_number_existing(db_session: AsyncSession):
    """Test getting test run by run number."""
    project_repo = ProjectRepository(db_session)
    project = await project_repo.create(name=unique_project_name())
    await db_session.commit()

    repo = RunRepository(db_session)
    created = await repo.create(project_id=project.id, name="Test Run")
    await db_session.commit()

    retrieved = await repo.get_by_number(created.run_number)

    assert retrieved is not None
    assert retrieved.run_number == created.run_number


@pytest.mark.unit
@pytest.mark.asyncio
async def test_get_by_number_nonexistent(db_session: AsyncSession):
    """Test getting nonexistent test run by number."""
    repo = RunRepository(db_session)
    result = await repo.get_by_number("TR-NONEXIST")
    assert result is None


# ============================================================================
# LIST OPERATIONS
# ============================================================================


@pytest.mark.unit
@pytest.mark.asyncio
async def test_list_by_project_basic(db_session: AsyncSession):
    """Test listing test runs for a project."""
    project_repo = ProjectRepository(db_session)
    project = await project_repo.create(name=unique_project_name())
    await db_session.commit()

    repo = RunRepository(db_session)
    await repo.create(project_id=project.id, name="Run 1")
    await repo.create(project_id=project.id, name="Run 2")
    await repo.create(project_id=project.id, name="Run 3")
    await db_session.commit()

    runs, total = await repo.list_by_project(project.id)

    assert len(runs) == 3
    assert total == 3


@pytest.mark.unit
@pytest.mark.asyncio
async def test_list_by_project_filters_by_project(db_session: AsyncSession):
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

    runs1, total1 = await repo.list_by_project(project1.id)
    runs2, total2 = await repo.list_by_project(project2.id)

    assert total1 == 2
    assert total2 == 1


@pytest.mark.unit
@pytest.mark.asyncio
async def test_list_by_project_filter_by_run_type(db_session: AsyncSession):
    """Test listing runs with run type filter."""
    project_repo = ProjectRepository(db_session)
    project = await project_repo.create(name=unique_project_name())
    await db_session.commit()

    repo = RunRepository(db_session)
    await repo.create(project_id=project.id, name="Manual Run", run_type="manual")
    await repo.create(project_id=project.id, name="Auto Run", run_type="automated")
    await db_session.commit()

    manual_runs, _ = await repo.list_by_project(project.id, run_type="manual")
    auto_runs, _ = await repo.list_by_project(project.id, run_type="automated")

    assert len(manual_runs) == 1
    assert len(auto_runs) == 1


@pytest.mark.unit
@pytest.mark.asyncio
async def test_list_by_project_filter_by_environment(db_session: AsyncSession):
    """Test listing runs with environment filter."""
    project_repo = ProjectRepository(db_session)
    project = await project_repo.create(name=unique_project_name())
    await db_session.commit()

    repo = RunRepository(db_session)
    await repo.create(project_id=project.id, name="Staging Run", environment="staging")
    await repo.create(project_id=project.id, name="Prod Run", environment="production")
    await db_session.commit()

    staging_runs, _ = await repo.list_by_project(project.id, environment="staging")
    prod_runs, _ = await repo.list_by_project(project.id, environment="production")

    assert len(staging_runs) == 1
    assert len(prod_runs) == 1


@pytest.mark.unit
@pytest.mark.asyncio
async def test_list_by_project_filter_by_initiated_by(db_session: AsyncSession):
    """Test listing runs with initiated_by filter."""
    project_repo = ProjectRepository(db_session)
    project = await project_repo.create(name=unique_project_name())
    await db_session.commit()

    repo = RunRepository(db_session)
    await repo.create(project_id=project.id, name="Run 1", initiated_by="user1")
    await repo.create(project_id=project.id, name="Run 2", initiated_by="user2")
    await db_session.commit()

    user1_runs, _ = await repo.list_by_project(project.id, initiated_by="user1")

    assert len(user1_runs) == 1


@pytest.mark.unit
@pytest.mark.asyncio
async def test_list_by_project_pagination(db_session: AsyncSession):
    """Test listing runs with pagination."""
    project_repo = ProjectRepository(db_session)
    project = await project_repo.create(name=unique_project_name())
    await db_session.commit()

    repo = RunRepository(db_session)
    for i in range(10):
        await repo.create(project_id=project.id, name=f"Run {i}")
    await db_session.commit()

    runs_page1, total = await repo.list_by_project(project.id, limit=5, skip=0)
    runs_page2, _ = await repo.list_by_project(project.id, limit=5, skip=5)

    assert len(runs_page1) == 5
    assert len(runs_page2) == 5
    assert total == 10


# ============================================================================
# UPDATE OPERATIONS
# ============================================================================


@pytest.mark.unit
@pytest.mark.asyncio
async def test_update_basic(db_session: AsyncSession):
    """Test updating test run fields."""
    project_repo = ProjectRepository(db_session)
    project = await project_repo.create(name=unique_project_name())
    await db_session.commit()

    repo = RunRepository(db_session)
    run = await repo.create(project_id=project.id, name="Original Name")
    await db_session.commit()

    updated = await repo.update(run.id, name="Updated Name")

    assert updated is not None
    assert updated.name == "Updated Name"
    assert updated.version == 2


@pytest.mark.unit
@pytest.mark.asyncio
async def test_update_nonexistent(db_session: AsyncSession):
    """Test updating nonexistent run returns None."""
    repo = RunRepository(db_session)
    result = await repo.update(str(uuid4()), name="New Name")
    assert result is None


# ============================================================================
# START OPERATIONS
# ============================================================================


@pytest.mark.unit
@pytest.mark.asyncio
async def test_start_run(db_session: AsyncSession):
    """Test starting a pending test run."""
    project_repo = ProjectRepository(db_session)
    project = await project_repo.create(name=unique_project_name())
    await db_session.commit()

    repo = RunRepository(db_session)
    run = await repo.create(project_id=project.id, name="Test Run")
    await db_session.commit()

    started = await repo.start(run.id, executed_by="test_user")

    assert started is not None
    assert started.status.value == "running"
    assert started.started_at is not None
    assert started.executed_by == "test_user"


@pytest.mark.unit
@pytest.mark.asyncio
async def test_start_run_already_running(db_session: AsyncSession):
    """Test starting an already running run raises error."""
    project_repo = ProjectRepository(db_session)
    project = await project_repo.create(name=unique_project_name())
    await db_session.commit()

    repo = RunRepository(db_session)
    run = await repo.create(project_id=project.id, name="Test Run")
    await repo.start(run.id)
    await db_session.commit()

    with pytest.raises(ValueError, match="Cannot start run"):
        await repo.start(run.id)


@pytest.mark.unit
@pytest.mark.asyncio
async def test_start_nonexistent_run(db_session: AsyncSession):
    """Test starting nonexistent run returns None."""
    repo = RunRepository(db_session)
    result = await repo.start(str(uuid4()))
    assert result is None


# ============================================================================
# COMPLETE OPERATIONS
# ============================================================================


@pytest.mark.unit
@pytest.mark.asyncio
async def test_complete_run(db_session: AsyncSession):
    """Test completing a running test run."""
    project_repo = ProjectRepository(db_session)
    project = await project_repo.create(name=unique_project_name())
    await db_session.commit()

    repo = RunRepository(db_session)
    run = await repo.create(project_id=project.id, name="Test Run")
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
async def test_complete_run_auto_status(db_session: AsyncSession):
    """Test completing run with automatic status determination."""
    project_repo = ProjectRepository(db_session)
    project = await project_repo.create(name=unique_project_name())
    await db_session.commit()

    repo = RunRepository(db_session)
    run = await repo.create(project_id=project.id, name="Test Run")
    await repo.start(run.id)

    # Set some failure counts to trigger FAILED status
    run_obj = await repo.get_by_id(run.id)
    run_obj.failed_count = 2
    await db_session.commit()

    completed = await repo.complete(run.id)  # No explicit status

    assert completed.status.value == "failed"


@pytest.mark.unit
@pytest.mark.asyncio
async def test_complete_run_not_running(db_session: AsyncSession):
    """Test completing a non-running run raises error."""
    project_repo = ProjectRepository(db_session)
    project = await project_repo.create(name=unique_project_name())
    await db_session.commit()

    repo = RunRepository(db_session)
    run = await repo.create(project_id=project.id, name="Test Run")
    await db_session.commit()

    with pytest.raises(ValueError, match="Cannot complete run"):
        await repo.complete(run.id)


@pytest.mark.unit
@pytest.mark.asyncio
async def test_complete_nonexistent_run(db_session: AsyncSession):
    """Test completing nonexistent run returns None."""
    repo = RunRepository(db_session)
    result = await repo.complete(str(uuid4()))
    assert result is None


# ============================================================================
# CANCEL OPERATIONS
# ============================================================================


@pytest.mark.unit
@pytest.mark.asyncio
async def test_cancel_pending_run(db_session: AsyncSession):
    """Test cancelling a pending test run."""
    project_repo = ProjectRepository(db_session)
    project = await project_repo.create(name=unique_project_name())
    await db_session.commit()

    repo = RunRepository(db_session)
    run = await repo.create(project_id=project.id, name="Test Run")
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
async def test_cancel_running_run(db_session: AsyncSession):
    """Test cancelling a running test run."""
    project_repo = ProjectRepository(db_session)
    project = await project_repo.create(name=unique_project_name())
    await db_session.commit()

    repo = RunRepository(db_session)
    run = await repo.create(project_id=project.id, name="Test Run")
    await repo.start(run.id)
    await db_session.commit()

    cancelled = await repo.cancel(run.id)

    assert cancelled.status.value == "cancelled"
    assert cancelled.completed_at is not None


@pytest.mark.unit
@pytest.mark.asyncio
async def test_cancel_completed_run_raises_error(db_session: AsyncSession):
    """Test cancelling a completed run raises error."""
    project_repo = ProjectRepository(db_session)
    project = await project_repo.create(name=unique_project_name())
    await db_session.commit()

    repo = RunRepository(db_session)
    run = await repo.create(project_id=project.id, name="Test Run")
    await repo.start(run.id)
    await repo.complete(run.id, status="passed")
    await db_session.commit()

    with pytest.raises(ValueError, match="Cannot cancel run"):
        await repo.cancel(run.id)


@pytest.mark.unit
@pytest.mark.asyncio
async def test_cancel_nonexistent_run(db_session: AsyncSession):
    """Test cancelling nonexistent run returns None."""
    repo = RunRepository(db_session)
    result = await repo.cancel(str(uuid4()))
    assert result is None


# ============================================================================
# TEST RESULT OPERATIONS
# ============================================================================


@pytest.mark.unit
@pytest.mark.asyncio
async def test_add_result(db_session: AsyncSession):
    """Test adding a test result to a run."""
    project_repo = ProjectRepository(db_session)
    project = await project_repo.create(name=unique_project_name())
    await db_session.commit()

    # Create test case
    tc_id = str(uuid4())
    test_case = _TestCaseModel(
        id=tc_id,
        project_id=project.id,
        title="Test Case 1",
        test_case_number=f"TC-{uuid4().hex[:8].upper()}",
    )
    db_session.add(test_case)
    await db_session.flush()

    repo = RunRepository(db_session)
    run = await repo.create(project_id=project.id, name="Test Run")
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
    assert updated_run.total_tests == 1
    assert updated_run.passed_count == 1


@pytest.mark.unit
@pytest.mark.asyncio
async def test_add_result_failed(db_session: AsyncSession):
    """Test adding a failed test result."""
    project_repo = ProjectRepository(db_session)
    project = await project_repo.create(name=unique_project_name())
    await db_session.commit()

    test_case = _TestCaseModel(
        id=str(uuid4()),
        project_id=project.id,
        title="Test Case 1",
        test_case_number=f"TC-{uuid4().hex[:8].upper()}",
    )
    db_session.add(test_case)
    await db_session.flush()

    repo = RunRepository(db_session)
    run = await repo.create(project_id=project.id, name="Test Run")
    await repo.start(run.id)
    await db_session.commit()

    result = await repo.add_result(
        run_id=run.id,
        test_case_id=test_case.id,
        status="failed",
        failure_reason="Assertion failed",
        error_message="Expected 1 but got 2",
    )

    assert result.status.value == "failed"
    assert result.failure_reason == "Assertion failed"

    updated_run = await repo.get_by_id(run.id)
    assert updated_run.failed_count == 1


@pytest.mark.unit
@pytest.mark.asyncio
async def test_add_result_with_details(db_session: AsyncSession):
    """Test adding result with all details."""
    project_repo = ProjectRepository(db_session)
    project = await project_repo.create(name=unique_project_name())
    await db_session.commit()

    test_case = _TestCaseModel(
        id=str(uuid4()),
        project_id=project.id,
        title="Test Case 1",
        test_case_number=f"TC-{uuid4().hex[:8].upper()}",
    )
    db_session.add(test_case)
    await db_session.flush()

    repo = RunRepository(db_session)
    run = await repo.create(project_id=project.id, name="Test Run")
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

    assert result.duration_seconds == 120
    assert result.actual_result == "Test completed successfully"
    assert result.screenshots == ["screenshot1.png", "screenshot2.png"]
    assert result.logs_url == "https://logs.example.com/123"


@pytest.mark.unit
@pytest.mark.asyncio
async def test_add_bulk_results(db_session: AsyncSession):
    """Test adding multiple test results at once."""
    project_repo = ProjectRepository(db_session)
    project = await project_repo.create(name=unique_project_name())
    await db_session.commit()

    # Create test cases
    test_cases = []
    for i in range(3):
        tc = _TestCaseModel(
            id=str(uuid4()),
            project_id=project.id,
            title=f"Test Case {i}",
            test_case_number=f"TC-{uuid4().hex[:8].upper()}",
        )
        db_session.add(tc)
        test_cases.append(tc)
    await db_session.flush()

    repo = RunRepository(db_session)
    run = await repo.create(project_id=project.id, name="Test Run")
    await repo.start(run.id)
    await db_session.commit()

    results_data = [
        {"test_case_id": test_cases[0].id, "status": "passed"},
        {"test_case_id": test_cases[1].id, "status": "failed", "failure_reason": "Bug"},
        {"test_case_id": test_cases[2].id, "status": "skipped"},
    ]

    results = await repo.add_bulk_results(run.id, results_data)

    assert len(results) == 3

    updated_run = await repo.get_by_id(run.id)
    assert updated_run.total_tests == 3
    assert updated_run.passed_count == 1
    assert updated_run.failed_count == 1
    assert updated_run.skipped_count == 1


@pytest.mark.unit
@pytest.mark.asyncio
async def test_get_results(db_session: AsyncSession):
    """Test getting all results for a run."""
    project_repo = ProjectRepository(db_session)
    project = await project_repo.create(name=unique_project_name())
    await db_session.commit()

    test_case = _TestCaseModel(
        id=str(uuid4()),
        project_id=project.id,
        title="Test Case 1",
        test_case_number=f"TC-{uuid4().hex[:8].upper()}",
    )
    db_session.add(test_case)
    await db_session.flush()

    repo = RunRepository(db_session)
    run = await repo.create(project_id=project.id, name="Test Run")
    await repo.start(run.id)
    await repo.add_result(run.id, test_case.id, "passed")
    await db_session.commit()

    results = await repo.get_results(run.id)

    assert len(results) == 1
    assert results[0].test_case_id == test_case.id


@pytest.mark.unit
@pytest.mark.asyncio
async def test_get_results_filtered_by_status(db_session: AsyncSession):
    """Test getting results filtered by status."""
    project_repo = ProjectRepository(db_session)
    project = await project_repo.create(name=unique_project_name())
    await db_session.commit()

    test_cases = []
    for i in range(2):
        tc = _TestCaseModel(
            id=str(uuid4()),
            project_id=project.id,
            title=f"TC {i}",
            test_case_number=f"TC-{uuid4().hex[:8].upper()}",
        )
        db_session.add(tc)
        test_cases.append(tc)
    await db_session.flush()

    repo = RunRepository(db_session)
    run = await repo.create(project_id=project.id, name="Test Run")
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
async def test_get_activities(db_session: AsyncSession):
    """Test getting activity log for a run."""
    project_repo = ProjectRepository(db_session)
    project = await project_repo.create(name=unique_project_name())
    await db_session.commit()

    repo = RunRepository(db_session)
    run = await repo.create(project_id=project.id, name="Test Run")
    await repo.start(run.id)
    await db_session.commit()

    activities = await repo.get_activities(run.id)

    # Should have "created" and "started" activities
    assert len(activities) >= 2
    activity_types = [a.activity_type for a in activities]
    assert "created" in activity_types
    assert "started" in activity_types


# ============================================================================
# DELETE OPERATIONS
# ============================================================================


@pytest.mark.unit
@pytest.mark.asyncio
async def test_delete_run(db_session: AsyncSession):
    """Test deleting a test run."""
    project_repo = ProjectRepository(db_session)
    project = await project_repo.create(name=unique_project_name())
    await db_session.commit()

    repo = RunRepository(db_session)
    run = await repo.create(project_id=project.id, name="Test Run")
    await db_session.commit()

    result = await repo.delete(run.id)

    assert result is True

    deleted = await repo.get_by_id(run.id)
    assert deleted is None


@pytest.mark.unit
@pytest.mark.asyncio
async def test_delete_nonexistent_run(db_session: AsyncSession):
    """Test deleting nonexistent run returns False."""
    repo = RunRepository(db_session)
    result = await repo.delete(str(uuid4()))
    assert result is False


# ============================================================================
# STATS OPERATIONS
# ============================================================================


@pytest.mark.unit
@pytest.mark.asyncio
async def test_get_stats(db_session: AsyncSession):
    """Test getting statistics for test runs."""
    project_repo = ProjectRepository(db_session)
    project = await project_repo.create(name=unique_project_name())
    await db_session.commit()

    repo = RunRepository(db_session)

    # Create runs with different types and environments
    run1 = await repo.create(
        project_id=project.id,
        name="Run 1",
        run_type="manual",
        environment="staging",
    )
    run2 = await repo.create(
        project_id=project.id,
        name="Run 2",
        run_type="automated",
        environment="production",
    )
    await db_session.commit()

    stats = await repo.get_stats(project.id)

    assert stats["total_runs"] == 2
    assert "by_status" in stats
    assert "by_type" in stats
    assert "by_environment" in stats
    assert "recent_runs" in stats


@pytest.mark.unit
@pytest.mark.asyncio
async def test_get_stats_empty_project(db_session: AsyncSession):
    """Test getting stats for project with no runs."""
    project_repo = ProjectRepository(db_session)
    project = await project_repo.create(name=unique_project_name())
    await db_session.commit()

    repo = RunRepository(db_session)
    stats = await repo.get_stats(project.id)

    assert stats["total_runs"] == 0
    assert stats["recent_runs"] == []
