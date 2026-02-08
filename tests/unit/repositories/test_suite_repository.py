"""Comprehensive unit tests for TestSuiteRepository to achieve 85%+ coverage.

Tests for:
- create() - test suite creation
- get_by_id() - retrieving suite by ID
- get_by_number() - retrieving suite by suite number
- list_by_project() - listing with filters and pagination
- update() - updating suite fields
- transition_status() - status transitions with validation
- add_test_case() - adding test cases to suite
- remove_test_case() - removing test cases from suite
- get_test_cases() - getting test cases for suite
- reorder_test_cases() - reordering test cases
- get_activities() - retrieving activity log
- delete() - deleting suites
- get_stats() - project statistics
"""

from uuid import uuid4

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from tests.test_constants import COUNT_FIVE, COUNT_TEN, COUNT_THREE, COUNT_TWO
from tracertm.models import test_case as tc_models

# Use module-qualified import to avoid pytest collection issue
from tracertm.repositories import test_suite_repository as ts_repo
from tracertm.repositories.project_repository import ProjectRepository

SuiteRepository = ts_repo.TestSuiteRepository
_TestCaseModel = tc_models.TestCase


def unique_project_name() -> str:
    """Generate a unique project name for tests."""
    return f"Test Project {uuid4().hex[:8]}"


# ============================================================================
# CREATE OPERATIONS
# ============================================================================


@pytest.mark.unit
@pytest.mark.asyncio
async def test_create_suite_basic(db_session: AsyncSession) -> None:
    """Test creating suite with basic fields."""
    project_repo = ProjectRepository(db_session)
    project = await project_repo.create(name=unique_project_name())
    await db_session.commit()

    repo = SuiteRepository(db_session)
    suite = await repo.create(
        project_id=str(project.id),
        name="Test Suite",
    )

    assert suite.id is not None
    assert suite.suite_number is not None
    assert suite.suite_number.startswith("TS-")
    assert suite.name == "Test Suite"
    assert suite.status.value == "draft"


@pytest.mark.unit
@pytest.mark.asyncio
async def test_create_suite_with_description(db_session: AsyncSession) -> None:
    """Test creating suite with description and objective."""
    project_repo = ProjectRepository(db_session)
    project = await project_repo.create(name=unique_project_name())
    await db_session.commit()

    repo = SuiteRepository(db_session)
    suite = await repo.create(
        project_id=str(project.id),
        name="Test Suite",
        description="Suite description",
        objective="Suite objective",
    )

    assert suite.description == "Suite description"
    assert suite.objective == "Suite objective"


@pytest.mark.unit
@pytest.mark.asyncio
async def test_create_suite_with_hierarchy(db_session: AsyncSession) -> None:
    """Test creating suite with parent."""
    project_repo = ProjectRepository(db_session)
    project = await project_repo.create(name=unique_project_name())
    await db_session.commit()

    repo = SuiteRepository(db_session)
    parent = await repo.create(project_id=str(project.id), name="Parent Suite")
    await db_session.commit()

    child = await repo.create(
        project_id=str(project.id),
        name="Child Suite",
        parent_id=parent.id,
        order_index=1,
    )

    assert child.parent_id == parent.id
    assert child.order_index == 1


@pytest.mark.unit
@pytest.mark.asyncio
async def test_create_suite_with_classification(db_session: AsyncSession) -> None:
    """Test creating suite with category and tags."""
    project_repo = ProjectRepository(db_session)
    project = await project_repo.create(name=unique_project_name())
    await db_session.commit()

    repo = SuiteRepository(db_session)
    suite = await repo.create(
        project_id=str(project.id),
        name="Test Suite",
        category="integration",
        tags=["smoke", "critical"],
    )

    assert suite.category == "integration"
    assert suite.tags == ["smoke", "critical"]


@pytest.mark.unit
@pytest.mark.asyncio
async def test_create_suite_with_execution_settings(db_session: AsyncSession) -> None:
    """Test creating suite with execution settings."""
    project_repo = ProjectRepository(db_session)
    project = await project_repo.create(name=unique_project_name())
    await db_session.commit()

    repo = SuiteRepository(db_session)
    suite = await repo.create(
        project_id=str(project.id),
        name="Test Suite",
        is_parallel_execution=True,
        estimated_duration_minutes=60,
    )

    assert suite.is_parallel_execution is True
    assert suite.estimated_duration_minutes == 60


@pytest.mark.unit
@pytest.mark.asyncio
async def test_create_suite_with_environment(db_session: AsyncSession) -> None:
    """Test creating suite with environment settings."""
    project_repo = ProjectRepository(db_session)
    project = await project_repo.create(name=unique_project_name())
    await db_session.commit()

    repo = SuiteRepository(db_session)
    suite = await repo.create(
        project_id=str(project.id),
        name="Test Suite",
        required_environment="staging",
        environment_variables={"API_URL": "https://staging.api.com"},
        setup_instructions="Run setup.sh",
        teardown_instructions="Run cleanup.sh",
    )

    assert suite.required_environment == "staging"
    assert suite.environment_variables == {"API_URL": "https://staging.api.com"}
    assert suite.setup_instructions == "Run setup.sh"
    assert suite.teardown_instructions == "Run cleanup.sh"


@pytest.mark.unit
@pytest.mark.asyncio
async def test_create_suite_with_ownership(db_session: AsyncSession) -> None:
    """Test creating suite with ownership fields."""
    project_repo = ProjectRepository(db_session)
    project = await project_repo.create(name=unique_project_name())
    await db_session.commit()

    repo = SuiteRepository(db_session)
    suite = await repo.create(
        project_id=str(project.id),
        name="Test Suite",
        owner="alice@example.com",
        responsible_team="QA Team",
    )

    assert suite.owner == "alice@example.com"
    assert suite.responsible_team == "QA Team"


@pytest.mark.unit
@pytest.mark.asyncio
async def test_create_suite_with_metadata(db_session: AsyncSession) -> None:
    """Test creating suite with custom metadata."""
    project_repo = ProjectRepository(db_session)
    project = await project_repo.create(name=unique_project_name())
    await db_session.commit()

    repo = SuiteRepository(db_session)
    suite = await repo.create(
        project_id=str(project.id),
        name="Test Suite",
        metadata={"custom_field": "custom_value"},
    )

    assert suite.suite_metadata == {"custom_field": "custom_value"}


@pytest.mark.unit
@pytest.mark.asyncio
async def test_create_suite_logs_activity(db_session: AsyncSession) -> None:
    """Test that creating a suite logs a creation activity."""
    project_repo = ProjectRepository(db_session)
    project = await project_repo.create(name=unique_project_name())
    await db_session.commit()

    repo = SuiteRepository(db_session)
    suite = await repo.create(
        project_id=str(project.id),
        name="Test Suite",
        created_by="test_user",
    )
    await db_session.commit()

    activities = await repo.get_activities(suite.id)
    assert len(activities) == 1
    assert activities[0].activity_type == "created"
    assert activities[0].performed_by == "test_user"


# ============================================================================
# GET_BY_ID OPERATIONS
# ============================================================================


@pytest.mark.unit
@pytest.mark.asyncio
async def test_get_by_id_found(db_session: AsyncSession) -> None:
    """Test retrieving suite by ID when found."""
    project_repo = ProjectRepository(db_session)
    project = await project_repo.create(name=unique_project_name())
    await db_session.commit()

    repo = SuiteRepository(db_session)
    created = await repo.create(project_id=str(project.id), name="Test Suite")
    await db_session.commit()

    found = await repo.get_by_id(created.id)
    assert found is not None
    assert found.id == created.id
    assert found.name == "Test Suite"


@pytest.mark.unit
@pytest.mark.asyncio
async def test_get_by_id_not_found(db_session: AsyncSession) -> None:
    """Test retrieving suite by ID when not found."""
    repo = SuiteRepository(db_session)
    found = await repo.get_by_id(str(uuid4()))
    assert found is None


# ============================================================================
# GET_BY_NUMBER OPERATIONS
# ============================================================================


@pytest.mark.unit
@pytest.mark.asyncio
async def test_get_by_number_found(db_session: AsyncSession) -> None:
    """Test retrieving suite by suite number when found."""
    project_repo = ProjectRepository(db_session)
    project = await project_repo.create(name=unique_project_name())
    await db_session.commit()

    repo = SuiteRepository(db_session)
    created = await repo.create(project_id=str(project.id), name="Test Suite")
    await db_session.commit()

    found = await repo.get_by_number(created.suite_number)
    assert found is not None
    assert found.suite_number == created.suite_number


@pytest.mark.unit
@pytest.mark.asyncio
async def test_get_by_number_not_found(db_session: AsyncSession) -> None:
    """Test retrieving suite by number when not found."""
    repo = SuiteRepository(db_session)
    found = await repo.get_by_number("TS-NONEXISTENT")
    assert found is None


# ============================================================================
# LIST_BY_PROJECT OPERATIONS
# ============================================================================


@pytest.mark.unit
@pytest.mark.asyncio
async def test_list_by_project_basic(db_session: AsyncSession) -> None:
    """Test listing suites for a project."""
    project_repo = ProjectRepository(db_session)
    project = await project_repo.create(name=unique_project_name())
    await db_session.commit()

    repo = SuiteRepository(db_session)
    await repo.create(project_id=str(project.id), name="Suite 1")
    await repo.create(project_id=str(project.id), name="Suite 2")
    await repo.create(project_id=str(project.id), name="Suite 3")
    await db_session.commit()

    suites, total = await repo.list_by_project(project_id=str(project.id))
    assert len(suites) == COUNT_THREE
    assert total == COUNT_THREE


@pytest.mark.unit
@pytest.mark.asyncio
async def test_list_by_project_filter_by_status(db_session: AsyncSession) -> None:
    """Test filtering suites by status."""
    project_repo = ProjectRepository(db_session)
    project = await project_repo.create(name=unique_project_name())
    await db_session.commit()

    repo = SuiteRepository(db_session)
    s1 = await repo.create(project_id=str(project.id), name="Suite 1")
    await repo.create(project_id=str(project.id), name="Suite 2")
    await db_session.commit()

    # Activate one suite
    await repo.transition_status(s1.id, "active")
    await db_session.commit()

    draft_suites, total = await repo.list_by_project(project_id=str(project.id), status="draft")
    assert len(draft_suites) == 1

    active_suites, _total = await repo.list_by_project(project_id=str(project.id), status="active")
    assert len(active_suites) == 1


@pytest.mark.unit
@pytest.mark.asyncio
async def test_list_by_project_filter_by_category(db_session: AsyncSession) -> None:
    """Test filtering suites by category."""
    project_repo = ProjectRepository(db_session)
    project = await project_repo.create(name=unique_project_name())
    await db_session.commit()

    repo = SuiteRepository(db_session)
    await repo.create(project_id=str(project.id), name="Suite 1", category="unit")
    await repo.create(project_id=str(project.id), name="Suite 2", category="integration")
    await db_session.commit()

    unit_suites, _ = await repo.list_by_project(project_id=str(project.id), category="unit")
    assert len(unit_suites) == 1
    assert unit_suites[0].name == "Suite 1"


@pytest.mark.unit
@pytest.mark.asyncio
async def test_list_by_project_filter_by_parent_id(db_session: AsyncSession) -> None:
    """Test filtering suites by parent ID."""
    project_repo = ProjectRepository(db_session)
    project = await project_repo.create(name=unique_project_name())
    await db_session.commit()

    repo = SuiteRepository(db_session)
    parent = await repo.create(project_id=str(project.id), name="Parent Suite")
    await db_session.commit()

    await repo.create(project_id=str(project.id), name="Child 1", parent_id=parent.id)
    await repo.create(project_id=str(project.id), name="Child 2", parent_id=parent.id)
    await repo.create(project_id=str(project.id), name="Root Suite")
    await db_session.commit()

    # Get children
    children, _ = await repo.list_by_project(project_id=str(project.id), parent_id=parent.id)
    assert len(children) == COUNT_TWO

    # Get root suites (no parent)
    roots, _ = await repo.list_by_project(project_id=str(project.id), parent_id="")
    assert len(roots) == COUNT_TWO  # Parent and Root Suite


@pytest.mark.unit
@pytest.mark.asyncio
async def test_list_by_project_filter_by_owner(db_session: AsyncSession) -> None:
    """Test filtering suites by owner."""
    project_repo = ProjectRepository(db_session)
    project = await project_repo.create(name=unique_project_name())
    await db_session.commit()

    repo = SuiteRepository(db_session)
    await repo.create(project_id=str(project.id), name="Suite 1", owner="alice")
    await repo.create(project_id=str(project.id), name="Suite 2", owner="bob")
    await db_session.commit()

    alice_suites, _ = await repo.list_by_project(project_id=str(project.id), owner="alice")
    assert len(alice_suites) == 1
    assert alice_suites[0].name == "Suite 1"


@pytest.mark.unit
@pytest.mark.asyncio
async def test_list_by_project_search(db_session: AsyncSession) -> None:
    """Test searching suites by name."""
    project_repo = ProjectRepository(db_session)
    project = await project_repo.create(name=unique_project_name())
    await db_session.commit()

    repo = SuiteRepository(db_session)
    await repo.create(project_id=str(project.id), name="Authentication Tests")
    await repo.create(project_id=str(project.id), name="Authorization Tests")
    await repo.create(project_id=str(project.id), name="Payment Tests")
    await db_session.commit()

    auth_suites, _ = await repo.list_by_project(project_id=str(project.id), search="Auth")
    assert len(auth_suites) == COUNT_TWO


@pytest.mark.unit
@pytest.mark.asyncio
async def test_list_by_project_pagination(db_session: AsyncSession) -> None:
    """Test pagination in list_by_project."""
    project_repo = ProjectRepository(db_session)
    project = await project_repo.create(name=unique_project_name())
    await db_session.commit()

    repo = SuiteRepository(db_session)
    for i in range(10):
        await repo.create(project_id=str(project.id), name=f"Suite {i}")
    await db_session.commit()

    page1, total = await repo.list_by_project(project_id=str(project.id), skip=0, limit=5)
    page2, _ = await repo.list_by_project(project_id=str(project.id), skip=5, limit=5)

    assert len(page1) == COUNT_FIVE
    assert len(page2) == COUNT_FIVE
    assert total == COUNT_TEN


# ============================================================================
# UPDATE OPERATIONS
# ============================================================================


@pytest.mark.unit
@pytest.mark.asyncio
async def test_update_basic_fields(db_session: AsyncSession) -> None:
    """Test updating basic suite fields."""
    project_repo = ProjectRepository(db_session)
    project = await project_repo.create(name=unique_project_name())
    await db_session.commit()

    repo = SuiteRepository(db_session)
    suite = await repo.create(project_id=str(project.id), name="Original Name")
    await db_session.commit()

    updated = await repo.update(
        suite.id,
        name="Updated Name",
        description="Updated Description",
    )

    assert updated is not None
    assert updated.name == "Updated Name"
    assert updated.description == "Updated Description"
    assert updated.version == COUNT_TWO


@pytest.mark.unit
@pytest.mark.asyncio
async def test_update_not_found(db_session: AsyncSession) -> None:
    """Test updating non-existent suite."""
    repo = SuiteRepository(db_session)
    result = await repo.update(str(uuid4()), name="Test")
    assert result is None


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

    repo = SuiteRepository(db_session)
    suite = await repo.create(project_id=str(project.id), name="Test Suite")
    await db_session.commit()

    # draft -> active is valid
    updated = await repo.transition_status(suite.id, "active")
    assert updated is not None
    assert updated.status.value == "active"


@pytest.mark.unit
@pytest.mark.asyncio
async def test_transition_status_invalid(db_session: AsyncSession) -> None:
    """Test invalid status transition."""
    project_repo = ProjectRepository(db_session)
    project = await project_repo.create(name=unique_project_name())
    await db_session.commit()

    repo = SuiteRepository(db_session)
    suite = await repo.create(project_id=str(project.id), name="Test Suite")
    await db_session.commit()

    # draft -> deprecated is not valid
    with pytest.raises(ValueError, match="Invalid transition"):
        await repo.transition_status(suite.id, "deprecated")


@pytest.mark.unit
@pytest.mark.asyncio
async def test_transition_status_not_found(db_session: AsyncSession) -> None:
    """Test transition for non-existent suite."""
    repo = SuiteRepository(db_session)
    result = await repo.transition_status(str(uuid4()), "active")
    assert result is None


@pytest.mark.unit
@pytest.mark.asyncio
async def test_transition_status_logs_activity(db_session: AsyncSession) -> None:
    """Test that status transition logs activity."""
    project_repo = ProjectRepository(db_session)
    project = await project_repo.create(name=unique_project_name())
    await db_session.commit()

    repo = SuiteRepository(db_session)
    suite = await repo.create(project_id=str(project.id), name="Test Suite")
    await db_session.commit()

    await repo.transition_status(
        suite.id,
        "active",
        reason="Ready for execution",
        performed_by="admin",
    )
    await db_session.commit()

    activities = await repo.get_activities(suite.id)
    status_activity = next((a for a in activities if a.activity_type == "status_changed"), None)
    assert status_activity is not None
    assert status_activity.from_value == "draft"
    assert status_activity.to_value == "active"


# ============================================================================
# TEST CASE ASSOCIATION OPERATIONS
# ============================================================================


@pytest.mark.unit
@pytest.mark.asyncio
async def test_add_test_case(db_session: AsyncSession) -> None:
    """Test adding a test case to a suite."""
    project_repo = ProjectRepository(db_session)
    project = await project_repo.create(name=unique_project_name())
    await db_session.commit()

    # Create test case
    test_case = _TestCaseModel(
        id=str(uuid4()),
        project_id=str(project.id),
        title="Test Case 1",
        test_case_number=f"TC-{uuid4().hex[:8].upper()}",
    )
    db_session.add(test_case)
    await db_session.commit()

    repo = SuiteRepository(db_session)
    suite = await repo.create(project_id=str(project.id), name="Test Suite")
    await db_session.commit()

    assoc = await repo.add_test_case(
        suite.id,
        test_case.id,
        order_index=0,
        is_mandatory=True,
        added_by="tester",
    )

    assert assoc is not None
    assert assoc.suite_id == suite.id
    assert assoc.test_case_id == test_case.id
    assert assoc.order_index == 0
    assert assoc.is_mandatory is True


@pytest.mark.unit
@pytest.mark.asyncio
async def test_add_test_case_updates_metrics(db_session: AsyncSession) -> None:
    """Test that adding test case updates suite metrics."""
    project_repo = ProjectRepository(db_session)
    project = await project_repo.create(name=unique_project_name())
    await db_session.commit()

    # Create test case
    test_case = _TestCaseModel(
        id=str(uuid4()),
        project_id=str(project.id),
        title="Test Case 1",
        test_case_number=f"TC-{uuid4().hex[:8].upper()}",
    )
    db_session.add(test_case)
    await db_session.commit()

    repo = SuiteRepository(db_session)
    suite = await repo.create(project_id=str(project.id), name="Test Suite")
    await db_session.commit()

    await repo.add_test_case(suite.id, test_case.id)
    await db_session.commit()

    updated_suite = await repo.get_by_id(suite.id)
    assert updated_suite is not None
    assert updated_suite.total_test_cases == 1


@pytest.mark.unit
@pytest.mark.asyncio
async def test_remove_test_case(db_session: AsyncSession) -> None:
    """Test removing a test case from a suite."""
    project_repo = ProjectRepository(db_session)
    project = await project_repo.create(name=unique_project_name())
    await db_session.commit()

    # Create test case
    test_case = _TestCaseModel(
        id=str(uuid4()),
        project_id=str(project.id),
        title="Test Case 1",
        test_case_number=f"TC-{uuid4().hex[:8].upper()}",
    )
    db_session.add(test_case)
    await db_session.commit()

    repo = SuiteRepository(db_session)
    suite = await repo.create(project_id=str(project.id), name="Test Suite")
    await db_session.commit()

    await repo.add_test_case(suite.id, test_case.id)
    await db_session.commit()

    result = await repo.remove_test_case(suite.id, test_case.id, removed_by="tester")
    assert result is True

    # Verify it's removed
    test_cases = await repo.get_test_cases(suite.id)
    assert len(test_cases) == 0


@pytest.mark.unit
@pytest.mark.asyncio
async def test_remove_test_case_not_found(db_session: AsyncSession) -> None:
    """Test removing non-existent test case."""
    project_repo = ProjectRepository(db_session)
    project = await project_repo.create(name=unique_project_name())
    await db_session.commit()

    repo = SuiteRepository(db_session)
    suite = await repo.create(project_id=str(project.id), name="Test Suite")
    await db_session.commit()

    result = await repo.remove_test_case(suite.id, str(uuid4()))
    assert result is False


@pytest.mark.unit
@pytest.mark.asyncio
async def test_get_test_cases(db_session: AsyncSession) -> None:
    """Test getting test cases for a suite."""
    project_repo = ProjectRepository(db_session)
    project = await project_repo.create(name=unique_project_name())
    await db_session.commit()

    # Create test cases
    tc1 = _TestCaseModel(
        id=str(uuid4()),
        project_id=str(project.id),
        title="Test Case 1",
        test_case_number=f"TC-{uuid4().hex[:8].upper()}",
    )
    tc2 = _TestCaseModel(
        id=str(uuid4()),
        project_id=str(project.id),
        title="Test Case 2",
        test_case_number=f"TC-{uuid4().hex[:8].upper()}",
    )
    db_session.add_all([tc1, tc2])
    await db_session.commit()

    repo = SuiteRepository(db_session)
    suite = await repo.create(project_id=str(project.id), name="Test Suite")
    await db_session.commit()

    await repo.add_test_case(suite.id, tc1.id, order_index=0)
    await repo.add_test_case(suite.id, tc2.id, order_index=1)
    await db_session.commit()

    test_cases = await repo.get_test_cases(suite.id)
    assert len(test_cases) == COUNT_TWO
    assert test_cases[0].order_index == 0
    assert test_cases[1].order_index == 1


@pytest.mark.unit
@pytest.mark.asyncio
async def test_reorder_test_cases(db_session: AsyncSession) -> None:
    """Test reordering test cases in a suite."""
    project_repo = ProjectRepository(db_session)
    project = await project_repo.create(name=unique_project_name())
    await db_session.commit()

    # Create test cases
    tc1 = _TestCaseModel(
        id=str(uuid4()),
        project_id=str(project.id),
        title="Test Case 1",
        test_case_number=f"TC-{uuid4().hex[:8].upper()}",
    )
    tc2 = _TestCaseModel(
        id=str(uuid4()),
        project_id=str(project.id),
        title="Test Case 2",
        test_case_number=f"TC-{uuid4().hex[:8].upper()}",
    )
    db_session.add_all([tc1, tc2])
    await db_session.commit()

    repo = SuiteRepository(db_session)
    suite = await repo.create(project_id=str(project.id), name="Test Suite")
    await db_session.commit()

    await repo.add_test_case(suite.id, tc1.id, order_index=0)
    await repo.add_test_case(suite.id, tc2.id, order_index=1)
    await db_session.commit()

    # Reverse the order
    result = await repo.reorder_test_cases(suite.id, [tc2.id, tc1.id])
    assert result is True

    test_cases = await repo.get_test_cases(suite.id)
    tc1_assoc = next((tc for tc in test_cases if tc.test_case_id == tc1.id), None)
    tc2_assoc = next((tc for tc in test_cases if tc.test_case_id == tc2.id), None)
    assert tc1_assoc is not None
    assert tc2_assoc is not None
    assert tc1_assoc.order_index == 1
    assert tc2_assoc.order_index == 0


# ============================================================================
# DELETE OPERATIONS
# ============================================================================


@pytest.mark.unit
@pytest.mark.asyncio
async def test_delete_suite(db_session: AsyncSession) -> None:
    """Test deleting a test suite."""
    project_repo = ProjectRepository(db_session)
    project = await project_repo.create(name=unique_project_name())
    await db_session.commit()

    repo = SuiteRepository(db_session)
    suite = await repo.create(project_id=str(project.id), name="Test Suite")
    await db_session.commit()

    result = await repo.delete(suite.id)
    assert result is True

    found = await repo.get_by_id(suite.id)
    assert found is None


@pytest.mark.unit
@pytest.mark.asyncio
async def test_delete_suite_not_found(db_session: AsyncSession) -> None:
    """Test deleting non-existent suite."""
    repo = SuiteRepository(db_session)
    result = await repo.delete(str(uuid4()))
    assert result is False


# ============================================================================
# GET_ACTIVITIES OPERATIONS
# ============================================================================


@pytest.mark.unit
@pytest.mark.asyncio
async def test_get_activities(db_session: AsyncSession) -> None:
    """Test getting activity log for a suite."""
    project_repo = ProjectRepository(db_session)
    project = await project_repo.create(name=unique_project_name())
    await db_session.commit()

    repo = SuiteRepository(db_session)
    suite = await repo.create(project_id=str(project.id), name="Test Suite")
    await db_session.commit()

    await repo.transition_status(suite.id, "active")
    await db_session.commit()

    activities = await repo.get_activities(suite.id)
    assert len(activities) >= COUNT_TWO  # created + status_changed


# ============================================================================
# GET_STATS OPERATIONS
# ============================================================================


@pytest.mark.unit
@pytest.mark.asyncio
async def test_get_stats(db_session: AsyncSession) -> None:
    """Test getting project statistics."""
    project_repo = ProjectRepository(db_session)
    project = await project_repo.create(name=unique_project_name())
    await db_session.commit()

    repo = SuiteRepository(db_session)
    s1 = await repo.create(project_id=str(project.id), name="Suite 1", category="unit")
    await repo.create(project_id=str(project.id), name="Suite 2", category="unit")
    await repo.create(project_id=str(project.id), name="Suite 3", category="integration")
    await db_session.commit()

    # Activate one suite
    await repo.transition_status(s1.id, "active")
    await db_session.commit()

    stats = await repo.get_stats(str(project.id))
    assert stats["total"] == COUNT_THREE
    assert stats["by_status"]["draft"] == COUNT_TWO
    assert stats["by_status"]["active"] == 1
    assert stats["by_category"]["unit"] == COUNT_TWO
    assert stats["by_category"]["integration"] == 1


@pytest.mark.unit
@pytest.mark.asyncio
async def test_get_stats_empty_project(db_session: AsyncSession) -> None:
    """Test getting stats for project with no suites."""
    project_repo = ProjectRepository(db_session)
    project = await project_repo.create(name=unique_project_name())
    await db_session.commit()

    repo = SuiteRepository(db_session)
    stats = await repo.get_stats(str(project.id))
    assert stats["total"] == 0
    assert stats["total_test_cases"] == 0
