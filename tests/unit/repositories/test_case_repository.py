"""Comprehensive unit tests for TestCaseRepository to achieve 85%+ coverage.

Tests for:
- create() - test case creation
- get_by_id() - retrieval by ID
- get_by_number() - retrieval by number
- list_all() - listing with filters
- count() - counting test cases
- update() - updating with optimistic locking
- transition_status() - status transitions
- submit_for_review() - review submission
- approve() - approval workflow
- deprecate() - deprecation workflow
- record_execution() - execution recording
- delete() - soft/hard delete
- count_by_status() - status counts
- count_by_type() - type counts
- count_by_priority() - priority counts
- count_by_automation_status() - automation counts
- get_execution_summary() - execution stats
- get_activities() - activity logs
"""

from uuid import uuid4

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from tests.test_constants import COUNT_FIVE, COUNT_THREE, COUNT_TWO
from tracertm.core.concurrency import ConcurrencyError
from tracertm.repositories import test_case_repository as tc_repo
from tracertm.repositories.project_repository import ProjectRepository

# Use module-qualified names to avoid pytest collection issues
CaseRepository = tc_repo.TestCaseRepository


def unique_project_name() -> str:
    """Generate a unique project name for tests."""
    return f"Test Project {uuid4().hex[:8]}"


# ============================================================================
# CREATE OPERATIONS
# ============================================================================


@pytest.mark.unit
@pytest.mark.asyncio
async def test_create_basic(db_session: AsyncSession) -> None:
    """Test creating test case with basic fields."""
    project_repo = ProjectRepository(db_session)
    project = await project_repo.create(name=unique_project_name())
    await db_session.commit()

    repo = CaseRepository(db_session)
    tc = await repo.create(
        project_id=project.id,
        title="Login Test Case",
    )

    assert tc.id is not None
    assert tc.title == "Login Test Case"
    assert tc.project_id == project.id
    assert tc.status == "draft"
    assert tc.test_type == "functional"
    assert tc.priority == "medium"
    assert tc.test_case_number.startswith("TC-")
    assert tc.version == 1


@pytest.mark.unit
@pytest.mark.asyncio
async def test_create_with_details(db_session: AsyncSession) -> None:
    """Test creating test case with full details."""
    project_repo = ProjectRepository(db_session)
    project = await project_repo.create(name=unique_project_name())
    await db_session.commit()

    repo = CaseRepository(db_session)
    test_steps = [
        {"step": 1, "action": "Open login page", "expected": "Page loads"},
        {"step": 2, "action": "Enter credentials", "expected": "Fields accept input"},
    ]

    tc = await repo.create(
        project_id=project.id,
        title="Complete Login Test",
        description="Tests the complete login flow",
        objective="Verify user can log in successfully",
        test_type="e2e",
        priority="high",
        category="authentication",
        tags=["login", "auth", "critical"],
        preconditions="User must have valid credentials",
        test_steps=test_steps,
        expected_result="User is logged in and redirected to dashboard",
        postconditions="User session is active",
        test_data={"username": "testuser", "password": "****"},
        estimated_duration_minutes=15,
        assigned_to="qa_engineer",
        created_by="test_author",
    )

    assert tc.description == "Tests the complete login flow"
    assert tc.objective == "Verify user can log in successfully"
    assert tc.test_type == "e2e"
    assert tc.priority == "high"
    assert tc.category == "authentication"
    assert tc.tags == ["login", "auth", "critical"]
    assert tc.test_steps == test_steps
    assert tc.assigned_to == "qa_engineer"


@pytest.mark.unit
@pytest.mark.asyncio
async def test_create_with_automation(db_session: AsyncSession) -> None:
    """Test creating test case with automation details."""
    project_repo = ProjectRepository(db_session)
    project = await project_repo.create(name=unique_project_name())
    await db_session.commit()

    repo = CaseRepository(db_session)
    tc = await repo.create(
        project_id=project.id,
        title="Automated API Test",
        automation_status="automated",
        automation_script_path="/tests/api/test_login.py",
        automation_framework="pytest",
        automation_notes="Runs in CI/CD pipeline",
    )

    assert tc.automation_status == "automated"
    assert tc.automation_script_path == "/tests/api/test_login.py"
    assert tc.automation_framework == "pytest"


# ============================================================================
# GET OPERATIONS
# ============================================================================


@pytest.mark.unit
@pytest.mark.asyncio
async def test_get_by_id_existing(db_session: AsyncSession) -> None:
    """Test getting test case by ID."""
    project_repo = ProjectRepository(db_session)
    project = await project_repo.create(name=unique_project_name())
    await db_session.commit()

    repo = CaseRepository(db_session)
    created = await repo.create(project_id=project.id, title="Test Case")
    await db_session.commit()

    retrieved = await repo.get_by_id(created.id)

    assert retrieved is not None
    assert retrieved.id == created.id


@pytest.mark.unit
@pytest.mark.asyncio
async def test_get_by_id_with_project_scope(db_session: AsyncSession) -> None:
    """Test getting test case by ID with project scope."""
    project_repo = ProjectRepository(db_session)
    project1 = await project_repo.create(name=unique_project_name())
    project2 = await project_repo.create(name=unique_project_name())
    await db_session.commit()

    repo = CaseRepository(db_session)
    tc = await repo.create(project_id=project1.id, title="Test Case")
    await db_session.commit()

    # Should find when project matches
    found = await repo.get_by_id(tc.id, project_id=project1.id)
    assert found is not None

    # Should not find when project doesn't match
    not_found = await repo.get_by_id(tc.id, project_id=project2.id)
    assert not_found is None


@pytest.mark.unit
@pytest.mark.asyncio
async def test_get_by_id_nonexistent(db_session: AsyncSession) -> None:
    """Test getting nonexistent test case by ID."""
    repo = CaseRepository(db_session)
    result = await repo.get_by_id(str(uuid4()))
    assert result is None


@pytest.mark.unit
@pytest.mark.asyncio
async def test_get_by_number_existing(db_session: AsyncSession) -> None:
    """Test getting test case by number."""
    project_repo = ProjectRepository(db_session)
    project = await project_repo.create(name=unique_project_name())
    await db_session.commit()

    repo = CaseRepository(db_session)
    created = await repo.create(project_id=project.id, title="Test Case")
    await db_session.commit()

    retrieved = await repo.get_by_number(created.test_case_number)

    assert retrieved is not None
    assert retrieved.test_case_number == created.test_case_number


@pytest.mark.unit
@pytest.mark.asyncio
async def test_get_by_number_nonexistent(db_session: AsyncSession) -> None:
    """Test getting nonexistent test case by number."""
    repo = CaseRepository(db_session)
    result = await repo.get_by_number("TC-NONEXISTENT")
    assert result is None


# ============================================================================
# LIST OPERATIONS
# ============================================================================


@pytest.mark.unit
@pytest.mark.asyncio
async def test_list_all_basic(db_session: AsyncSession) -> None:
    """Test listing all test cases for a project."""
    project_repo = ProjectRepository(db_session)
    project = await project_repo.create(name=unique_project_name())
    await db_session.commit()

    repo = CaseRepository(db_session)
    await repo.create(project_id=project.id, title="TC 1")
    await repo.create(project_id=project.id, title="TC 2")
    await repo.create(project_id=project.id, title="TC 3")
    await db_session.commit()

    cases = await repo.list_all(project_id=project.id)

    assert len(cases) == COUNT_THREE


@pytest.mark.unit
@pytest.mark.asyncio
async def test_list_all_filter_by_status(db_session: AsyncSession) -> None:
    """Test listing test cases filtered by status."""
    project_repo = ProjectRepository(db_session)
    project = await project_repo.create(name=unique_project_name())
    await db_session.commit()

    repo = CaseRepository(db_session)
    tc1 = await repo.create(project_id=project.id, title="TC 1")
    await repo.create(project_id=project.id, title="TC 2")
    await db_session.commit()

    # Transition one to review
    await repo.submit_for_review(tc1.id)
    await db_session.commit()

    draft_cases = await repo.list_all(project_id=project.id, status="draft")
    review_cases = await repo.list_all(project_id=project.id, status="review")

    assert len(draft_cases) == 1
    assert len(review_cases) == 1


@pytest.mark.unit
@pytest.mark.asyncio
async def test_list_all_filter_by_type(db_session: AsyncSession) -> None:
    """Test listing test cases filtered by type."""
    project_repo = ProjectRepository(db_session)
    project = await project_repo.create(name=unique_project_name())
    await db_session.commit()

    repo = CaseRepository(db_session)
    await repo.create(project_id=project.id, title="TC 1", test_type="functional")
    await repo.create(project_id=project.id, title="TC 2", test_type="e2e")
    await db_session.commit()

    functional_cases = await repo.list_all(project_id=project.id, test_type="functional")
    e2e_cases = await repo.list_all(project_id=project.id, test_type="e2e")

    assert len(functional_cases) == 1
    assert len(e2e_cases) == 1


@pytest.mark.unit
@pytest.mark.asyncio
async def test_list_all_filter_by_priority(db_session: AsyncSession) -> None:
    """Test listing test cases filtered by priority."""
    project_repo = ProjectRepository(db_session)
    project = await project_repo.create(name=unique_project_name())
    await db_session.commit()

    repo = CaseRepository(db_session)
    await repo.create(project_id=project.id, title="TC 1", priority="high")
    await repo.create(project_id=project.id, title="TC 2", priority="low")
    await db_session.commit()

    high_cases = await repo.list_all(project_id=project.id, priority="high")

    assert len(high_cases) == 1


@pytest.mark.unit
@pytest.mark.asyncio
async def test_list_all_filter_by_automation_status(db_session: AsyncSession) -> None:
    """Test listing test cases filtered by automation status."""
    project_repo = ProjectRepository(db_session)
    project = await project_repo.create(name=unique_project_name())
    await db_session.commit()

    repo = CaseRepository(db_session)
    await repo.create(project_id=project.id, title="TC 1", automation_status="automated")
    await repo.create(project_id=project.id, title="TC 2", automation_status="not_automated")
    await db_session.commit()

    automated_cases = await repo.list_all(project_id=project.id, automation_status="automated")

    assert len(automated_cases) == 1


@pytest.mark.unit
@pytest.mark.asyncio
async def test_list_all_filter_by_category(db_session: AsyncSession) -> None:
    """Test listing test cases filtered by category."""
    project_repo = ProjectRepository(db_session)
    project = await project_repo.create(name=unique_project_name())
    await db_session.commit()

    repo = CaseRepository(db_session)
    await repo.create(project_id=project.id, title="TC 1", category="auth")
    await repo.create(project_id=project.id, title="TC 2", category="billing")
    await db_session.commit()

    auth_cases = await repo.list_all(project_id=project.id, category="auth")

    assert len(auth_cases) == 1


@pytest.mark.unit
@pytest.mark.asyncio
async def test_list_all_filter_by_assigned_to(db_session: AsyncSession) -> None:
    """Test listing test cases filtered by assignee."""
    project_repo = ProjectRepository(db_session)
    project = await project_repo.create(name=unique_project_name())
    await db_session.commit()

    repo = CaseRepository(db_session)
    await repo.create(project_id=project.id, title="TC 1", assigned_to="user1")
    await repo.create(project_id=project.id, title="TC 2", assigned_to="user2")
    await db_session.commit()

    user1_cases = await repo.list_all(project_id=project.id, assigned_to="user1")

    assert len(user1_cases) == 1


@pytest.mark.unit
@pytest.mark.asyncio
async def test_list_all_search(db_session: AsyncSession) -> None:
    """Test listing test cases with search."""
    project_repo = ProjectRepository(db_session)
    project = await project_repo.create(name=unique_project_name())
    await db_session.commit()

    repo = CaseRepository(db_session)
    await repo.create(project_id=project.id, title="Login Test")
    await repo.create(project_id=project.id, title="Logout Test")
    await repo.create(project_id=project.id, title="Registration Test")
    await db_session.commit()

    login_cases = await repo.list_all(project_id=project.id, search="Login")

    assert len(login_cases) == 1


@pytest.mark.unit
@pytest.mark.asyncio
async def test_list_all_pagination(db_session: AsyncSession) -> None:
    """Test listing test cases with pagination."""
    project_repo = ProjectRepository(db_session)
    project = await project_repo.create(name=unique_project_name())
    await db_session.commit()

    repo = CaseRepository(db_session)
    for i in range(10):
        await repo.create(project_id=project.id, title=f"TC {i}")
    await db_session.commit()

    page1 = await repo.list_all(project_id=project.id, limit=5, offset=0)
    page2 = await repo.list_all(project_id=project.id, limit=5, offset=5)

    assert len(page1) == COUNT_FIVE
    assert len(page2) == COUNT_FIVE


# ============================================================================
# COUNT OPERATIONS
# ============================================================================


@pytest.mark.unit
@pytest.mark.asyncio
async def test_count_basic(db_session: AsyncSession) -> None:
    """Test counting test cases."""
    project_repo = ProjectRepository(db_session)
    project = await project_repo.create(name=unique_project_name())
    await db_session.commit()

    repo = CaseRepository(db_session)
    await repo.create(project_id=project.id, title="TC 1")
    await repo.create(project_id=project.id, title="TC 2")
    await db_session.commit()

    count = await repo.count(project_id=project.id)

    assert count == COUNT_TWO


@pytest.mark.unit
@pytest.mark.asyncio
async def test_count_with_filters(db_session: AsyncSession) -> None:
    """Test counting test cases with filters."""
    project_repo = ProjectRepository(db_session)
    project = await project_repo.create(name=unique_project_name())
    await db_session.commit()

    repo = CaseRepository(db_session)
    await repo.create(project_id=project.id, title="TC 1", test_type="functional")
    await repo.create(project_id=project.id, title="TC 2", test_type="e2e")
    await db_session.commit()

    functional_count = await repo.count(project_id=project.id, test_type="functional")

    assert functional_count == 1


# ============================================================================
# UPDATE OPERATIONS
# ============================================================================


@pytest.mark.unit
@pytest.mark.asyncio
async def test_update_basic(db_session: AsyncSession) -> None:
    """Test updating test case with optimistic locking."""
    project_repo = ProjectRepository(db_session)
    project = await project_repo.create(name=unique_project_name())
    await db_session.commit()

    repo = CaseRepository(db_session)
    tc = await repo.create(project_id=project.id, title="Original Title")
    await db_session.commit()

    updated = await repo.update(
        tc.id,
        expected_version=1,
        title="Updated Title",
        description="New description",
    )

    assert updated.title == "Updated Title"
    assert updated.description == "New description"
    assert updated.version == COUNT_TWO


@pytest.mark.unit
@pytest.mark.asyncio
async def test_update_version_mismatch(db_session: AsyncSession) -> None:
    """Test updating test case with wrong version raises error."""
    project_repo = ProjectRepository(db_session)
    project = await project_repo.create(name=unique_project_name())
    await db_session.commit()

    repo = CaseRepository(db_session)
    tc = await repo.create(project_id=project.id, title="Test Case")
    await db_session.commit()

    with pytest.raises(ConcurrencyError):
        await repo.update(tc.id, expected_version=99, title="New Title")


@pytest.mark.unit
@pytest.mark.asyncio
async def test_update_nonexistent(db_session: AsyncSession) -> None:
    """Test updating nonexistent test case raises error."""
    repo = CaseRepository(db_session)

    with pytest.raises(ValueError, match="not found"):
        await repo.update(str(uuid4()), expected_version=1, title="New Title")


# ============================================================================
# STATUS TRANSITION OPERATIONS
# ============================================================================


@pytest.mark.unit
@pytest.mark.asyncio
async def test_transition_status_draft_to_review(db_session: AsyncSession) -> None:
    """Test transitioning from draft to review."""
    project_repo = ProjectRepository(db_session)
    project = await project_repo.create(name=unique_project_name())
    await db_session.commit()

    repo = CaseRepository(db_session)
    tc = await repo.create(project_id=project.id, title="Test Case")
    await db_session.commit()

    updated = await repo.transition_status(tc.id, "review")

    assert updated.status == "review"


@pytest.mark.unit
@pytest.mark.asyncio
async def test_transition_status_review_to_approved(db_session: AsyncSession) -> None:
    """Test transitioning from review to approved."""
    project_repo = ProjectRepository(db_session)
    project = await project_repo.create(name=unique_project_name())
    await db_session.commit()

    repo = CaseRepository(db_session)
    tc = await repo.create(project_id=project.id, title="Test Case")
    await repo.transition_status(tc.id, "review")
    await db_session.commit()

    updated = await repo.transition_status(tc.id, "approved")

    assert updated.status == "approved"
    assert updated.approved_at is not None


@pytest.mark.unit
@pytest.mark.asyncio
async def test_transition_status_invalid(db_session: AsyncSession) -> None:
    """Test invalid status transition raises error."""
    project_repo = ProjectRepository(db_session)
    project = await project_repo.create(name=unique_project_name())
    await db_session.commit()

    repo = CaseRepository(db_session)
    tc = await repo.create(project_id=project.id, title="Test Case")
    await db_session.commit()

    # Can't go directly from draft to approved
    with pytest.raises(ValueError, match="Invalid status transition"):
        await repo.transition_status(tc.id, "approved")


@pytest.mark.unit
@pytest.mark.asyncio
async def test_transition_status_nonexistent(db_session: AsyncSession) -> None:
    """Test transitioning nonexistent test case raises error."""
    repo = CaseRepository(db_session)

    with pytest.raises(ValueError, match="not found"):
        await repo.transition_status(str(uuid4()), "review")


# ============================================================================
# WORKFLOW OPERATIONS
# ============================================================================


@pytest.mark.unit
@pytest.mark.asyncio
async def test_submit_for_review(db_session: AsyncSession) -> None:
    """Test submitting test case for review."""
    project_repo = ProjectRepository(db_session)
    project = await project_repo.create(name=unique_project_name())
    await db_session.commit()

    repo = CaseRepository(db_session)
    tc = await repo.create(project_id=project.id, title="Test Case")
    await db_session.commit()

    updated = await repo.submit_for_review(tc.id, reviewer="reviewer_user")

    assert updated.status == "review"
    assert updated.reviewed_by == "reviewer_user"


@pytest.mark.unit
@pytest.mark.asyncio
async def test_approve(db_session: AsyncSession) -> None:
    """Test approving test case."""
    project_repo = ProjectRepository(db_session)
    project = await project_repo.create(name=unique_project_name())
    await db_session.commit()

    repo = CaseRepository(db_session)
    tc = await repo.create(project_id=project.id, title="Test Case")
    await repo.submit_for_review(tc.id)
    await db_session.commit()

    updated = await repo.approve(tc.id, reviewer_notes="LGTM", performed_by="approver")

    assert updated.status == "approved"
    assert updated.reviewed_by == "approver"
    assert updated.reviewed_at is not None


@pytest.mark.unit
@pytest.mark.asyncio
async def test_deprecate(db_session: AsyncSession) -> None:
    """Test deprecating test case."""
    project_repo = ProjectRepository(db_session)
    project = await project_repo.create(name=unique_project_name())
    await db_session.commit()

    repo = CaseRepository(db_session)
    tc = await repo.create(project_id=project.id, title="Old Test Case")
    await db_session.commit()

    updated = await repo.deprecate(tc.id, reason="Replaced by new test")

    assert updated.status == "deprecated"
    assert updated.deprecation_reason == "Replaced by new test"


@pytest.mark.unit
@pytest.mark.asyncio
async def test_deprecate_with_replacement(db_session: AsyncSession) -> None:
    """Test deprecating test case with replacement."""
    project_repo = ProjectRepository(db_session)
    project = await project_repo.create(name=unique_project_name())
    await db_session.commit()

    repo = CaseRepository(db_session)
    old_tc = await repo.create(project_id=project.id, title="Old Test")
    new_tc = await repo.create(project_id=project.id, title="New Test")
    await db_session.commit()

    updated = await repo.deprecate(
        old_tc.id,
        reason="Replaced",
        replacement_test_case_id=new_tc.id,
    )

    assert updated.test_case_metadata["replacement_test_case_id"] == new_tc.id


# ============================================================================
# EXECUTION OPERATIONS
# ============================================================================


@pytest.mark.unit
@pytest.mark.asyncio
async def test_record_execution_passed(db_session: AsyncSession) -> None:
    """Test recording passed execution."""
    project_repo = ProjectRepository(db_session)
    project = await project_repo.create(name=unique_project_name())
    await db_session.commit()

    repo = CaseRepository(db_session)
    tc = await repo.create(project_id=project.id, title="Test Case")
    await db_session.commit()

    updated = await repo.record_execution(tc.id, result="passed")

    assert updated.total_executions == 1
    assert updated.pass_count == 1
    assert updated.last_execution_result == "passed"
    assert updated.last_executed_at is not None


@pytest.mark.unit
@pytest.mark.asyncio
async def test_record_execution_failed(db_session: AsyncSession) -> None:
    """Test recording failed execution."""
    project_repo = ProjectRepository(db_session)
    project = await project_repo.create(name=unique_project_name())
    await db_session.commit()

    repo = CaseRepository(db_session)
    tc = await repo.create(project_id=project.id, title="Test Case")
    await db_session.commit()

    updated = await repo.record_execution(tc.id, result="failed")

    assert updated.total_executions == 1
    assert updated.fail_count == 1
    assert updated.last_execution_result == "failed"


@pytest.mark.unit
@pytest.mark.asyncio
async def test_record_execution_nonexistent(db_session: AsyncSession) -> None:
    """Test recording execution for nonexistent test case."""
    repo = CaseRepository(db_session)

    with pytest.raises(ValueError, match="not found"):
        await repo.record_execution(str(uuid4()), result="passed")


# ============================================================================
# DELETE OPERATIONS
# ============================================================================


@pytest.mark.unit
@pytest.mark.asyncio
async def test_delete_soft(db_session: AsyncSession) -> None:
    """Test soft deleting test case."""
    project_repo = ProjectRepository(db_session)
    project = await project_repo.create(name=unique_project_name())
    await db_session.commit()

    repo = CaseRepository(db_session)
    tc = await repo.create(project_id=project.id, title="Test Case")
    await db_session.commit()

    result = await repo.delete(tc.id, soft=True)

    assert result is True

    # Should not be found by normal get
    deleted = await repo.get_by_id(tc.id)
    assert deleted is None


@pytest.mark.unit
@pytest.mark.asyncio
async def test_delete_hard(db_session: AsyncSession) -> None:
    """Test hard deleting test case."""
    project_repo = ProjectRepository(db_session)
    project = await project_repo.create(name=unique_project_name())
    await db_session.commit()

    repo = CaseRepository(db_session)
    tc = await repo.create(project_id=project.id, title="Test Case")
    await db_session.commit()

    result = await repo.delete(tc.id, soft=False)

    assert result is True


@pytest.mark.unit
@pytest.mark.asyncio
async def test_delete_nonexistent(db_session: AsyncSession) -> None:
    """Test deleting nonexistent test case."""
    repo = CaseRepository(db_session)
    result = await repo.delete(str(uuid4()))
    assert result is False


# ============================================================================
# AGGREGATION OPERATIONS
# ============================================================================


@pytest.mark.unit
@pytest.mark.asyncio
async def test_count_by_status(db_session: AsyncSession) -> None:
    """Test counting test cases by status."""
    project_repo = ProjectRepository(db_session)
    project = await project_repo.create(name=unique_project_name())
    await db_session.commit()

    repo = CaseRepository(db_session)
    tc1 = await repo.create(project_id=project.id, title="TC 1")
    await repo.create(project_id=project.id, title="TC 2")
    await repo.submit_for_review(tc1.id)
    await db_session.commit()

    counts = await repo.count_by_status(project.id)

    assert counts.get("draft") == 1 or counts.get("draft", 0) == 1
    assert counts.get("review") == 1 or counts.get("review", 0) == 1


@pytest.mark.unit
@pytest.mark.asyncio
async def test_count_by_type(db_session: AsyncSession) -> None:
    """Test counting test cases by type."""
    project_repo = ProjectRepository(db_session)
    project = await project_repo.create(name=unique_project_name())
    await db_session.commit()

    repo = CaseRepository(db_session)
    await repo.create(project_id=project.id, title="TC 1", test_type="functional")
    await repo.create(project_id=project.id, title="TC 2", test_type="e2e")
    await db_session.commit()

    counts = await repo.count_by_type(project.id)

    assert len(counts) >= COUNT_TWO


@pytest.mark.unit
@pytest.mark.asyncio
async def test_count_by_priority(db_session: AsyncSession) -> None:
    """Test counting test cases by priority."""
    project_repo = ProjectRepository(db_session)
    project = await project_repo.create(name=unique_project_name())
    await db_session.commit()

    repo = CaseRepository(db_session)
    await repo.create(project_id=project.id, title="TC 1", priority="high")
    await repo.create(project_id=project.id, title="TC 2", priority="low")
    await db_session.commit()

    counts = await repo.count_by_priority(project.id)

    assert len(counts) >= COUNT_TWO


@pytest.mark.unit
@pytest.mark.asyncio
async def test_count_by_automation_status(db_session: AsyncSession) -> None:
    """Test counting test cases by automation status."""
    project_repo = ProjectRepository(db_session)
    project = await project_repo.create(name=unique_project_name())
    await db_session.commit()

    repo = CaseRepository(db_session)
    await repo.create(project_id=project.id, title="TC 1", automation_status="automated")
    await repo.create(project_id=project.id, title="TC 2", automation_status="not_automated")
    await db_session.commit()

    counts = await repo.count_by_automation_status(project.id)

    assert len(counts) >= COUNT_TWO


@pytest.mark.unit
@pytest.mark.asyncio
async def test_get_execution_summary(db_session: AsyncSession) -> None:
    """Test getting execution summary."""
    project_repo = ProjectRepository(db_session)
    project = await project_repo.create(name=unique_project_name())
    await db_session.commit()

    repo = CaseRepository(db_session)
    tc1 = await repo.create(project_id=project.id, title="TC 1")
    tc2 = await repo.create(project_id=project.id, title="TC 2")
    await repo.record_execution(tc1.id, result="passed")
    await repo.record_execution(tc1.id, result="passed")
    await repo.record_execution(tc2.id, result="failed")
    await db_session.commit()

    summary = await repo.get_execution_summary(project.id)

    assert summary["total_runs"] == COUNT_THREE
    assert summary["total_passed"] == COUNT_TWO
    assert summary["total_failed"] == 1


# ============================================================================
# ACTIVITY OPERATIONS
# ============================================================================


@pytest.mark.unit
@pytest.mark.asyncio
async def test_get_activities(db_session: AsyncSession) -> None:
    """Test getting activity log."""
    project_repo = ProjectRepository(db_session)
    project = await project_repo.create(name=unique_project_name())
    await db_session.commit()

    repo = CaseRepository(db_session)
    tc = await repo.create(project_id=project.id, title="Test Case")
    await repo.submit_for_review(tc.id)
    await db_session.commit()

    activities = await repo.get_activities(tc.id)

    # Should have "created" and "status_transition" activities
    assert len(activities) >= COUNT_TWO
    activity_types = [a.activity_type for a in activities]
    assert "created" in activity_types
