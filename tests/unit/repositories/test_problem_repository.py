"""Comprehensive unit tests for ProblemRepository to achieve 85%+ coverage.

Tests for:
- create() - problem creation with various options
- get_by_id() - retrieving problem by ID
- get_by_number() - retrieving problem by problem number
- list_all() - listing with filters and pagination
- update() - updating with optimistic locking
- transition_status() - status transitions with validation
- record_rca() - recording root cause analysis
- update_workaround() - updating workaround information
- update_permanent_fix() - updating permanent fix information
- close() - closing problems
- delete() - soft and hard delete
- count_by_status() - counting problems by status
- count_by_priority() - counting problems by priority
- get_activities() - retrieving activity log
"""

from datetime import UTC, datetime
from uuid import uuid4

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from tests.test_constants import COUNT_FIVE, COUNT_FOUR, COUNT_THREE, COUNT_TWO
from tracertm.core.concurrency import ConcurrencyError
from tracertm.repositories.problem_repository import ProblemRepository
from tracertm.repositories.project_repository import ProjectRepository


def unique_project_name() -> str:
    """Generate a unique project name for tests."""
    return f"Test Project {uuid4().hex[:8]}"


# ============================================================================
# CREATE OPERATIONS
# ============================================================================


@pytest.mark.unit
@pytest.mark.asyncio
async def test_create_problem_basic(db_session: AsyncSession) -> None:
    """Test creating problem with basic fields."""
    project_repo = ProjectRepository(db_session)
    project = await project_repo.create(name=unique_project_name())
    await db_session.commit()

    repo = ProblemRepository(db_session)
    problem = await repo.create(
        project_id=project.id,
        title="Test Problem",
    )

    assert problem.id is not None
    assert problem.problem_number is not None
    assert problem.problem_number.startswith("P-")
    assert problem.title == "Test Problem"
    assert problem.status == "open"
    assert problem.version == 1


@pytest.mark.unit
@pytest.mark.asyncio
async def test_create_problem_with_description(db_session: AsyncSession) -> None:
    """Test creating problem with description."""
    project_repo = ProjectRepository(db_session)
    project = await project_repo.create(name=unique_project_name())
    await db_session.commit()

    repo = ProblemRepository(db_session)
    problem = await repo.create(
        project_id=project.id,
        title="Test Problem",
        description="Detailed problem description",
    )

    assert problem.description == "Detailed problem description"


@pytest.mark.unit
@pytest.mark.asyncio
async def test_create_problem_with_classification(db_session: AsyncSession) -> None:
    """Test creating problem with classification fields."""
    project_repo = ProjectRepository(db_session)
    project = await project_repo.create(name=unique_project_name())
    await db_session.commit()

    repo = ProblemRepository(db_session)
    problem = await repo.create(
        project_id=project.id,
        title="Test Problem",
        category="network",
        sub_category="dns",
        tags=["critical", "infrastructure"],
    )

    assert problem.category == "network"
    assert problem.sub_category == "dns"
    assert problem.tags == ["critical", "infrastructure"]


@pytest.mark.unit
@pytest.mark.asyncio
async def test_create_problem_with_impact_assessment(db_session: AsyncSession) -> None:
    """Test creating problem with impact assessment fields."""
    project_repo = ProjectRepository(db_session)
    project = await project_repo.create(name=unique_project_name())
    await db_session.commit()

    repo = ProblemRepository(db_session)
    problem = await repo.create(
        project_id=project.id,
        title="Test Problem",
        impact_level="critical",
        urgency="high",
        priority="critical",
        affected_systems=["api", "database"],
        affected_users_estimated=1000,
        business_impact_description="Significant revenue loss",
    )

    assert problem.impact_level == "critical"
    assert problem.urgency == "high"
    assert problem.priority == "critical"
    assert problem.affected_systems == ["api", "database"]
    assert problem.affected_users_estimated == 1000
    assert problem.business_impact_description == "Significant revenue loss"


@pytest.mark.unit
@pytest.mark.asyncio
async def test_create_problem_with_assignment(db_session: AsyncSession) -> None:
    """Test creating problem with assignment fields."""
    project_repo = ProjectRepository(db_session)
    project = await project_repo.create(name=unique_project_name())
    await db_session.commit()

    repo = ProblemRepository(db_session)
    problem = await repo.create(
        project_id=project.id,
        title="Test Problem",
        assigned_to="john.doe@example.com",
        assigned_team="Platform Team",
        owner="jane.smith@example.com",
    )

    assert problem.assigned_to == "john.doe@example.com"
    assert problem.assigned_team == "Platform Team"
    assert problem.owner == "jane.smith@example.com"


@pytest.mark.unit
@pytest.mark.asyncio
async def test_create_problem_with_target_date(db_session: AsyncSession) -> None:
    """Test creating problem with target resolution date."""
    project_repo = ProjectRepository(db_session)
    project = await project_repo.create(name=unique_project_name())
    await db_session.commit()

    target_date = datetime(2025, 12, 31, tzinfo=UTC)

    repo = ProblemRepository(db_session)
    problem = await repo.create(
        project_id=project.id,
        title="Test Problem",
        target_resolution_date=target_date,
    )

    # Compare without timezone (SQLite may strip tz info)
    assert problem.target_resolution_date is not None
    assert problem.target_resolution_date.year == 2025
    assert problem.target_resolution_date.month == 12
    assert problem.target_resolution_date.day == 31


@pytest.mark.unit
@pytest.mark.asyncio
async def test_create_problem_with_metadata(db_session: AsyncSession) -> None:
    """Test creating problem with custom metadata."""
    project_repo = ProjectRepository(db_session)
    project = await project_repo.create(name=unique_project_name())
    await db_session.commit()

    repo = ProblemRepository(db_session)
    problem = await repo.create(
        project_id=project.id,
        title="Test Problem",
        metadata={"custom_field": "custom_value", "incident_count": 5},
    )

    assert problem.problem_metadata == {"custom_field": "custom_value", "incident_count": 5}


@pytest.mark.unit
@pytest.mark.asyncio
async def test_create_problem_logs_activity(db_session: AsyncSession) -> None:
    """Test that creating a problem logs a creation activity."""
    project_repo = ProjectRepository(db_session)
    project = await project_repo.create(name=unique_project_name())
    await db_session.commit()

    repo = ProblemRepository(db_session)
    problem = await repo.create(
        project_id=project.id,
        title="Test Problem",
        created_by="test_user",
    )

    activities = await repo.get_activities(problem.id)
    assert len(activities) == 1
    assert activities[0].activity_type == "created"
    assert activities[0].performed_by == "test_user"


# ============================================================================
# GET_BY_ID OPERATIONS
# ============================================================================


@pytest.mark.unit
@pytest.mark.asyncio
async def test_get_by_id_found(db_session: AsyncSession) -> None:
    """Test retrieving problem by ID when found."""
    project_repo = ProjectRepository(db_session)
    project = await project_repo.create(name=unique_project_name())
    await db_session.commit()

    repo = ProblemRepository(db_session)
    created = await repo.create(project_id=project.id, title="Test Problem")
    await db_session.commit()

    found = await repo.get_by_id(created.id)
    assert found is not None
    assert found.id == created.id
    assert found.title == "Test Problem"


@pytest.mark.unit
@pytest.mark.asyncio
async def test_get_by_id_not_found(db_session: AsyncSession) -> None:
    """Test retrieving problem by ID when not found."""
    repo = ProblemRepository(db_session)
    found = await repo.get_by_id(str(uuid4()))
    assert found is None


@pytest.mark.unit
@pytest.mark.asyncio
async def test_get_by_id_excludes_deleted(db_session: AsyncSession) -> None:
    """Test that get_by_id excludes soft-deleted problems."""
    project_repo = ProjectRepository(db_session)
    project = await project_repo.create(name=unique_project_name())
    await db_session.commit()

    repo = ProblemRepository(db_session)
    problem = await repo.create(project_id=project.id, title="Test Problem")
    await db_session.commit()

    await repo.delete(problem.id, soft=True)
    await db_session.commit()

    found = await repo.get_by_id(problem.id)
    assert found is None


@pytest.mark.unit
@pytest.mark.asyncio
async def test_get_by_id_scoped_to_project(db_session: AsyncSession) -> None:
    """Test retrieving problem by ID scoped to a specific project."""
    project_repo = ProjectRepository(db_session)
    project1 = await project_repo.create(name=unique_project_name())
    project2 = await project_repo.create(name=unique_project_name())
    await db_session.commit()

    repo = ProblemRepository(db_session)
    problem = await repo.create(project_id=project1.id, title="Test Problem")
    await db_session.commit()

    # Should find with correct project
    found1 = await repo.get_by_id(problem.id, project_id=project1.id)
    assert found1 is not None

    # Should not find with wrong project
    found2 = await repo.get_by_id(problem.id, project_id=project2.id)
    assert found2 is None


# ============================================================================
# GET_BY_NUMBER OPERATIONS
# ============================================================================


@pytest.mark.unit
@pytest.mark.asyncio
async def test_get_by_number_found(db_session: AsyncSession) -> None:
    """Test retrieving problem by problem number when found."""
    project_repo = ProjectRepository(db_session)
    project = await project_repo.create(name=unique_project_name())
    await db_session.commit()

    repo = ProblemRepository(db_session)
    created = await repo.create(project_id=project.id, title="Test Problem")
    await db_session.commit()

    found = await repo.get_by_number(created.problem_number)
    assert found is not None
    assert found.problem_number == created.problem_number


@pytest.mark.unit
@pytest.mark.asyncio
async def test_get_by_number_not_found(db_session: AsyncSession) -> None:
    """Test retrieving problem by number when not found."""
    repo = ProblemRepository(db_session)
    found = await repo.get_by_number("P-NONEXISTENT")
    assert found is None


@pytest.mark.unit
@pytest.mark.asyncio
async def test_get_by_number_scoped_to_project(db_session: AsyncSession) -> None:
    """Test retrieving problem by number scoped to project."""
    project_repo = ProjectRepository(db_session)
    project1 = await project_repo.create(name=unique_project_name())
    project2 = await project_repo.create(name=unique_project_name())
    await db_session.commit()

    repo = ProblemRepository(db_session)
    problem = await repo.create(project_id=project1.id, title="Test Problem")
    await db_session.commit()

    # Should find with correct project
    found1 = await repo.get_by_number(problem.problem_number, project_id=project1.id)
    assert found1 is not None

    # Should not find with wrong project
    found2 = await repo.get_by_number(problem.problem_number, project_id=project2.id)
    assert found2 is None


# ============================================================================
# LIST_ALL OPERATIONS
# ============================================================================


@pytest.mark.unit
@pytest.mark.asyncio
async def test_list_all_basic(db_session: AsyncSession) -> None:
    """Test listing problems for a project."""
    project_repo = ProjectRepository(db_session)
    project = await project_repo.create(name=unique_project_name())
    await db_session.commit()

    repo = ProblemRepository(db_session)
    await repo.create(project_id=project.id, title="Problem 1")
    await repo.create(project_id=project.id, title="Problem 2")
    await repo.create(project_id=project.id, title="Problem 3")
    await db_session.commit()

    problems = await repo.list_all(project_id=project.id)
    assert len(problems) == COUNT_THREE


@pytest.mark.unit
@pytest.mark.asyncio
async def test_list_all_excludes_deleted(db_session: AsyncSession) -> None:
    """Test listing problems excludes deleted by default."""
    project_repo = ProjectRepository(db_session)
    project = await project_repo.create(name=unique_project_name())
    await db_session.commit()

    repo = ProblemRepository(db_session)
    p1 = await repo.create(project_id=project.id, title="Problem 1")
    await repo.create(project_id=project.id, title="Problem 2")
    await db_session.commit()

    await repo.delete(p1.id, soft=True)
    await db_session.commit()

    problems = await repo.list_all(project_id=project.id)
    assert len(problems) == 1


@pytest.mark.unit
@pytest.mark.asyncio
async def test_list_all_include_deleted(db_session: AsyncSession) -> None:
    """Test listing problems can include deleted."""
    project_repo = ProjectRepository(db_session)
    project = await project_repo.create(name=unique_project_name())
    await db_session.commit()

    repo = ProblemRepository(db_session)
    p1 = await repo.create(project_id=project.id, title="Problem 1")
    await repo.create(project_id=project.id, title="Problem 2")
    await db_session.commit()

    await repo.delete(p1.id, soft=True)
    await db_session.commit()

    problems = await repo.list_all(project_id=project.id, include_deleted=True)
    assert len(problems) == COUNT_TWO


@pytest.mark.unit
@pytest.mark.asyncio
async def test_list_all_filter_by_status(db_session: AsyncSession) -> None:
    """Test filtering problems by status."""
    project_repo = ProjectRepository(db_session)
    project = await project_repo.create(name=unique_project_name())
    await db_session.commit()

    repo = ProblemRepository(db_session)
    p1 = await repo.create(project_id=project.id, title="Problem 1")
    await repo.create(project_id=project.id, title="Problem 2")
    await db_session.commit()

    # Transition one to investigation
    await repo.transition_status(p1.id, "in_investigation")
    await db_session.commit()

    open_problems = await repo.list_all(project_id=project.id, status="open")
    assert len(open_problems) == 1

    investigating = await repo.list_all(project_id=project.id, status="in_investigation")
    assert len(investigating) == 1


@pytest.mark.unit
@pytest.mark.asyncio
async def test_list_all_filter_by_priority(db_session: AsyncSession) -> None:
    """Test filtering problems by priority."""
    project_repo = ProjectRepository(db_session)
    project = await project_repo.create(name=unique_project_name())
    await db_session.commit()

    repo = ProblemRepository(db_session)
    await repo.create(project_id=project.id, title="Problem 1", priority="high")
    await repo.create(project_id=project.id, title="Problem 2", priority="low")
    await db_session.commit()

    high_priority = await repo.list_all(project_id=project.id, priority="high")
    assert len(high_priority) == 1
    assert high_priority[0].title == "Problem 1"


@pytest.mark.unit
@pytest.mark.asyncio
async def test_list_all_filter_by_impact_level(db_session: AsyncSession) -> None:
    """Test filtering problems by impact level."""
    project_repo = ProjectRepository(db_session)
    project = await project_repo.create(name=unique_project_name())
    await db_session.commit()

    repo = ProblemRepository(db_session)
    await repo.create(project_id=project.id, title="Problem 1", impact_level="critical")
    await repo.create(project_id=project.id, title="Problem 2", impact_level="low")
    await db_session.commit()

    critical = await repo.list_all(project_id=project.id, impact_level="critical")
    assert len(critical) == 1
    assert critical[0].title == "Problem 1"


@pytest.mark.unit
@pytest.mark.asyncio
async def test_list_all_filter_by_category(db_session: AsyncSession) -> None:
    """Test filtering problems by category."""
    project_repo = ProjectRepository(db_session)
    project = await project_repo.create(name=unique_project_name())
    await db_session.commit()

    repo = ProblemRepository(db_session)
    await repo.create(project_id=project.id, title="Problem 1", category="network")
    await repo.create(project_id=project.id, title="Problem 2", category="database")
    await db_session.commit()

    network = await repo.list_all(project_id=project.id, category="network")
    assert len(network) == 1
    assert network[0].title == "Problem 1"


@pytest.mark.unit
@pytest.mark.asyncio
async def test_list_all_filter_by_assigned_to(db_session: AsyncSession) -> None:
    """Test filtering problems by assigned_to."""
    project_repo = ProjectRepository(db_session)
    project = await project_repo.create(name=unique_project_name())
    await db_session.commit()

    repo = ProblemRepository(db_session)
    await repo.create(project_id=project.id, title="Problem 1", assigned_to="alice")
    await repo.create(project_id=project.id, title="Problem 2", assigned_to="bob")
    await db_session.commit()

    alice_problems = await repo.list_all(project_id=project.id, assigned_to="alice")
    assert len(alice_problems) == 1
    assert alice_problems[0].title == "Problem 1"


@pytest.mark.unit
@pytest.mark.asyncio
async def test_list_all_pagination(db_session: AsyncSession) -> None:
    """Test pagination in list_all."""
    project_repo = ProjectRepository(db_session)
    project = await project_repo.create(name=unique_project_name())
    await db_session.commit()

    repo = ProblemRepository(db_session)
    for i in range(10):
        await repo.create(project_id=project.id, title=f"Problem {i}")
    await db_session.commit()

    page1 = await repo.list_all(project_id=project.id, limit=5, offset=0)
    page2 = await repo.list_all(project_id=project.id, limit=5, offset=5)

    assert len(page1) == COUNT_FIVE
    assert len(page2) == COUNT_FIVE

    # Ensure no overlap
    page1_ids = {p.id for p in page1}
    page2_ids = {p.id for p in page2}
    assert len(page1_ids & page2_ids) == 0


# ============================================================================
# UPDATE OPERATIONS
# ============================================================================


@pytest.mark.unit
@pytest.mark.asyncio
async def test_update_basic_fields(db_session: AsyncSession) -> None:
    """Test updating basic problem fields."""
    project_repo = ProjectRepository(db_session)
    project = await project_repo.create(name=unique_project_name())
    await db_session.commit()

    repo = ProblemRepository(db_session)
    problem = await repo.create(project_id=project.id, title="Original Title")
    await db_session.commit()

    updated = await repo.update(
        problem.id,
        expected_version=1,
        title="Updated Title",
        description="Updated Description",
    )

    assert updated.title == "Updated Title"
    assert updated.description == "Updated Description"
    assert updated.version == COUNT_TWO


@pytest.mark.unit
@pytest.mark.asyncio
async def test_update_optimistic_locking_success(db_session: AsyncSession) -> None:
    """Test that update succeeds with correct version."""
    project_repo = ProjectRepository(db_session)
    project = await project_repo.create(name=unique_project_name())
    await db_session.commit()

    repo = ProblemRepository(db_session)
    problem = await repo.create(project_id=project.id, title="Test")
    await db_session.commit()

    # First update
    updated = await repo.update(problem.id, expected_version=1, title="Updated")
    assert updated.version == COUNT_TWO

    # Second update with correct version
    updated2 = await repo.update(updated.id, expected_version=2, title="Updated Again")
    assert updated2.version == COUNT_THREE


@pytest.mark.unit
@pytest.mark.asyncio
async def test_update_optimistic_locking_failure(db_session: AsyncSession) -> None:
    """Test that update fails with stale version."""
    project_repo = ProjectRepository(db_session)
    project = await project_repo.create(name=unique_project_name())
    await db_session.commit()

    repo = ProblemRepository(db_session)
    problem = await repo.create(project_id=project.id, title="Test")
    await db_session.commit()

    # Update to increment version
    await repo.update(problem.id, expected_version=1, title="First Update")
    await db_session.commit()

    # Try to update with stale version
    with pytest.raises(ConcurrencyError):
        await repo.update(problem.id, expected_version=1, title="Second Update")


@pytest.mark.unit
@pytest.mark.asyncio
async def test_update_not_found(db_session: AsyncSession) -> None:
    """Test updating non-existent problem."""
    repo = ProblemRepository(db_session)

    with pytest.raises(ValueError, match="not found"):
        await repo.update(str(uuid4()), expected_version=1, title="Test")


@pytest.mark.unit
@pytest.mark.asyncio
async def test_update_logs_significant_changes(db_session: AsyncSession) -> None:
    """Test that updating significant fields logs activity."""
    project_repo = ProjectRepository(db_session)
    project = await project_repo.create(name=unique_project_name())
    await db_session.commit()

    repo = ProblemRepository(db_session)
    problem = await repo.create(project_id=project.id, title="Test")
    await db_session.commit()

    # Update status (significant field)
    await repo.update(
        problem.id,
        expected_version=1,
        status="in_investigation",
        performed_by="test_user",
    )
    await db_session.commit()

    activities = await repo.get_activities(problem.id)
    # Should have creation activity + status change activity
    assert len(activities) >= COUNT_TWO
    status_activity = next((a for a in activities if a.activity_type == "status_changed"), None)
    assert status_activity is not None


# ============================================================================
# TRANSITION_STATUS OPERATIONS
# ============================================================================


@pytest.mark.unit
@pytest.mark.asyncio
async def test_transition_status_valid(db_session: AsyncSession) -> None:
    """Test valid status transition."""
    project_repo = ProjectRepository(db_session)
    project = await project_repo.create(name=unique_project_name())
    await db_session.commit()

    repo = ProblemRepository(db_session)
    problem = await repo.create(project_id=project.id, title="Test")
    await db_session.commit()

    # open -> in_investigation is valid
    updated = await repo.transition_status(problem.id, "in_investigation")
    assert updated.status == "in_investigation"


@pytest.mark.unit
@pytest.mark.asyncio
async def test_transition_status_invalid(db_session: AsyncSession) -> None:
    """Test invalid status transition."""
    project_repo = ProjectRepository(db_session)
    project = await project_repo.create(name=unique_project_name())
    await db_session.commit()

    repo = ProblemRepository(db_session)
    problem = await repo.create(project_id=project.id, title="Test")
    await db_session.commit()

    # open -> known_error is not valid (must go through investigation first)
    with pytest.raises(ValueError, match="Invalid status transition"):
        await repo.transition_status(problem.id, "known_error")


@pytest.mark.unit
@pytest.mark.asyncio
async def test_transition_status_not_found(db_session: AsyncSession) -> None:
    """Test transition for non-existent problem."""
    repo = ProblemRepository(db_session)

    with pytest.raises(ValueError, match="not found"):
        await repo.transition_status(str(uuid4()), "in_investigation")


@pytest.mark.unit
@pytest.mark.asyncio
async def test_transition_status_logs_activity(db_session: AsyncSession) -> None:
    """Test that status transition logs activity."""
    project_repo = ProjectRepository(db_session)
    project = await project_repo.create(name=unique_project_name())
    await db_session.commit()

    repo = ProblemRepository(db_session)
    problem = await repo.create(project_id=project.id, title="Test")
    await db_session.commit()

    await repo.transition_status(
        problem.id,
        "in_investigation",
        reason="Starting investigation",
        performed_by="test_user",
    )
    await db_session.commit()

    activities = await repo.get_activities(problem.id)
    transition_activity = next((a for a in activities if a.activity_type == "status_transition"), None)
    assert transition_activity is not None
    assert transition_activity.from_value == "open"
    assert transition_activity.to_value == "in_investigation"


# ============================================================================
# RECORD_RCA OPERATIONS
# ============================================================================


@pytest.mark.unit
@pytest.mark.asyncio
async def test_record_rca_basic(db_session: AsyncSession) -> None:
    """Test recording basic RCA."""
    project_repo = ProjectRepository(db_session)
    project = await project_repo.create(name=unique_project_name())
    await db_session.commit()

    repo = ProblemRepository(db_session)
    problem = await repo.create(project_id=project.id, title="Test")
    await db_session.commit()

    updated = await repo.record_rca(
        problem.id,
        rca_method="five_whys",
        performed_by="analyst",
    )

    assert updated.rca_performed is True
    assert updated.rca_method == "five_whys"
    assert updated.rca_completed_at is not None
    assert updated.rca_completed_by == "analyst"


@pytest.mark.unit
@pytest.mark.asyncio
async def test_record_rca_with_root_cause(db_session: AsyncSession) -> None:
    """Test recording RCA with root cause identified."""
    project_repo = ProjectRepository(db_session)
    project = await project_repo.create(name=unique_project_name())
    await db_session.commit()

    repo = ProblemRepository(db_session)
    problem = await repo.create(project_id=project.id, title="Test")
    await db_session.commit()

    updated = await repo.record_rca(
        problem.id,
        rca_method="fishbone",
        rca_notes="Analysis notes",
        rca_data={"category": "process", "factors": ["training", "documentation"]},
        root_cause_identified=True,
        root_cause_description="Inadequate error handling in payment module",
        root_cause_category="technology",
        root_cause_confidence="high",
    )

    assert updated.root_cause_identified is True
    assert updated.root_cause_description == "Inadequate error handling in payment module"
    assert updated.root_cause_category == "technology"
    assert updated.root_cause_confidence == "high"


@pytest.mark.unit
@pytest.mark.asyncio
async def test_record_rca_not_found(db_session: AsyncSession) -> None:
    """Test RCA for non-existent problem."""
    repo = ProblemRepository(db_session)

    with pytest.raises(ValueError, match="not found"):
        await repo.record_rca(str(uuid4()), rca_method="five_whys")


# ============================================================================
# UPDATE_WORKAROUND OPERATIONS
# ============================================================================


@pytest.mark.unit
@pytest.mark.asyncio
async def test_update_workaround_available(db_session: AsyncSession) -> None:
    """Test updating workaround as available."""
    project_repo = ProjectRepository(db_session)
    project = await project_repo.create(name=unique_project_name())
    await db_session.commit()

    repo = ProblemRepository(db_session)
    problem = await repo.create(project_id=project.id, title="Test")
    await db_session.commit()

    updated = await repo.update_workaround(
        problem.id,
        workaround_available=True,
        workaround_description="Restart the service",
        workaround_effectiveness="partial",
    )

    assert updated.workaround_available is True
    assert updated.workaround_description == "Restart the service"
    assert updated.workaround_effectiveness == "partial"


@pytest.mark.unit
@pytest.mark.asyncio
async def test_update_workaround_not_available(db_session: AsyncSession) -> None:
    """Test updating workaround as not available."""
    project_repo = ProjectRepository(db_session)
    project = await project_repo.create(name=unique_project_name())
    await db_session.commit()

    repo = ProblemRepository(db_session)
    problem = await repo.create(project_id=project.id, title="Test")
    await db_session.commit()

    updated = await repo.update_workaround(problem.id, workaround_available=False)

    assert updated.workaround_available is False


@pytest.mark.unit
@pytest.mark.asyncio
async def test_update_workaround_not_found(db_session: AsyncSession) -> None:
    """Test workaround update for non-existent problem."""
    repo = ProblemRepository(db_session)

    with pytest.raises(ValueError, match="not found"):
        await repo.update_workaround(str(uuid4()), workaround_available=True)


# ============================================================================
# UPDATE_PERMANENT_FIX OPERATIONS
# ============================================================================


@pytest.mark.unit
@pytest.mark.asyncio
async def test_update_permanent_fix_available(db_session: AsyncSession) -> None:
    """Test updating permanent fix as available."""
    project_repo = ProjectRepository(db_session)
    project = await project_repo.create(name=unique_project_name())
    await db_session.commit()

    repo = ProblemRepository(db_session)
    problem = await repo.create(project_id=project.id, title="Test")
    await db_session.commit()

    updated = await repo.update_permanent_fix(
        problem.id,
        permanent_fix_available=True,
        permanent_fix_description="Upgraded dependency to v2.0",
        permanent_fix_change_id="CHG-12345",
    )

    assert updated.permanent_fix_available is True
    assert updated.permanent_fix_description == "Upgraded dependency to v2.0"
    assert updated.permanent_fix_change_id == "CHG-12345"
    assert updated.permanent_fix_implemented_at is not None


@pytest.mark.unit
@pytest.mark.asyncio
async def test_update_permanent_fix_not_found(db_session: AsyncSession) -> None:
    """Test permanent fix update for non-existent problem."""
    repo = ProblemRepository(db_session)

    with pytest.raises(ValueError, match="not found"):
        await repo.update_permanent_fix(str(uuid4()), permanent_fix_available=True)


# ============================================================================
# CLOSE OPERATIONS
# ============================================================================


@pytest.mark.unit
@pytest.mark.asyncio
async def test_close_problem(db_session: AsyncSession) -> None:
    """Test closing a problem."""
    project_repo = ProjectRepository(db_session)
    project = await project_repo.create(name=unique_project_name())
    await db_session.commit()

    repo = ProblemRepository(db_session)
    problem = await repo.create(project_id=project.id, title="Test")
    await db_session.commit()

    closed = await repo.close(
        problem.id,
        resolution_type="permanent_fix",
        closure_notes="Issue resolved with deployment",
        closed_by="admin",
    )

    assert closed.status == "closed"
    assert closed.resolution_type == "permanent_fix"
    assert closed.closure_notes == "Issue resolved with deployment"
    assert closed.closed_by == "admin"
    assert closed.closed_at is not None


@pytest.mark.unit
@pytest.mark.asyncio
async def test_close_problem_not_found(db_session: AsyncSession) -> None:
    """Test closing non-existent problem."""
    repo = ProblemRepository(db_session)

    with pytest.raises(ValueError, match="not found"):
        await repo.close(str(uuid4()), resolution_type="permanent_fix")


# ============================================================================
# DELETE OPERATIONS
# ============================================================================


@pytest.mark.unit
@pytest.mark.asyncio
async def test_delete_soft(db_session: AsyncSession) -> None:
    """Test soft delete of problem."""
    project_repo = ProjectRepository(db_session)
    project = await project_repo.create(name=unique_project_name())
    await db_session.commit()

    repo = ProblemRepository(db_session)
    problem = await repo.create(project_id=project.id, title="Test")
    await db_session.commit()

    result = await repo.delete(problem.id, soft=True)
    assert result is True

    # Should not be found in normal query
    found = await repo.get_by_id(problem.id)
    assert found is None


@pytest.mark.unit
@pytest.mark.asyncio
async def test_delete_hard(db_session: AsyncSession) -> None:
    """Test hard delete of problem."""
    project_repo = ProjectRepository(db_session)
    project = await project_repo.create(name=unique_project_name())
    await db_session.commit()

    repo = ProblemRepository(db_session)
    problem = await repo.create(project_id=project.id, title="Test")
    await db_session.commit()

    result = await repo.delete(problem.id, soft=False)
    assert result is True


@pytest.mark.unit
@pytest.mark.asyncio
async def test_delete_not_found(db_session: AsyncSession) -> None:
    """Test delete of non-existent problem."""
    repo = ProblemRepository(db_session)
    result = await repo.delete(str(uuid4()), soft=True)
    assert result is False


# ============================================================================
# COUNT_BY_STATUS OPERATIONS
# ============================================================================


@pytest.mark.unit
@pytest.mark.asyncio
async def test_count_by_status(db_session: AsyncSession) -> None:
    """Test counting problems by status."""
    project_repo = ProjectRepository(db_session)
    project = await project_repo.create(name=unique_project_name())
    await db_session.commit()

    repo = ProblemRepository(db_session)
    p1 = await repo.create(project_id=project.id, title="Problem 1")
    p2 = await repo.create(project_id=project.id, title="Problem 2")
    await repo.create(project_id=project.id, title="Problem 3")
    await db_session.commit()

    await repo.transition_status(p1.id, "in_investigation")
    await repo.transition_status(p2.id, "in_investigation")
    await db_session.commit()

    counts = await repo.count_by_status(project.id)
    assert counts.get("open") == 1
    assert counts.get("in_investigation") == COUNT_TWO


# ============================================================================
# COUNT_BY_PRIORITY OPERATIONS
# ============================================================================


@pytest.mark.unit
@pytest.mark.asyncio
async def test_count_by_priority(db_session: AsyncSession) -> None:
    """Test counting problems by priority."""
    project_repo = ProjectRepository(db_session)
    project = await project_repo.create(name=unique_project_name())
    await db_session.commit()

    repo = ProblemRepository(db_session)
    await repo.create(project_id=project.id, title="Problem 1", priority="critical")
    await repo.create(project_id=project.id, title="Problem 2", priority="critical")
    await repo.create(project_id=project.id, title="Problem 3", priority="low")
    await db_session.commit()

    counts = await repo.count_by_priority(project.id)
    assert counts.get("critical") == COUNT_TWO
    assert counts.get("low") == 1


# ============================================================================
# GET_ACTIVITIES OPERATIONS
# ============================================================================


@pytest.mark.unit
@pytest.mark.asyncio
async def test_get_activities(db_session: AsyncSession) -> None:
    """Test getting activity log for a problem."""
    project_repo = ProjectRepository(db_session)
    project = await project_repo.create(name=unique_project_name())
    await db_session.commit()

    repo = ProblemRepository(db_session)
    problem = await repo.create(project_id=project.id, title="Test")
    await db_session.commit()

    # Perform several actions to generate activities
    await repo.transition_status(problem.id, "in_investigation")
    await repo.record_rca(problem.id, rca_method="five_whys")
    await repo.update_workaround(problem.id, workaround_available=True, workaround_description="Restart")
    await db_session.commit()

    activities = await repo.get_activities(problem.id)
    assert len(activities) >= COUNT_FOUR  # created + transition + rca + workaround


@pytest.mark.unit
@pytest.mark.asyncio
async def test_get_activities_with_limit(db_session: AsyncSession) -> None:
    """Test getting activities with limit."""
    project_repo = ProjectRepository(db_session)
    project = await project_repo.create(name=unique_project_name())
    await db_session.commit()

    repo = ProblemRepository(db_session)
    problem = await repo.create(project_id=project.id, title="Test")
    await db_session.commit()

    # Generate several activities
    await repo.transition_status(problem.id, "in_investigation")
    await repo.record_rca(problem.id, rca_method="five_whys")
    await db_session.commit()

    activities = await repo.get_activities(problem.id, limit=2)
    assert len(activities) == COUNT_TWO
