"""Comprehensive unit tests for ProcessRepository to achieve 85%+ coverage.

Tests for:
- create() - process creation with various options
- get_by_id() - retrieving process by ID
- get_by_number() - retrieving process by process number
- list_all() - listing with filters and pagination
- update() - updating with optimistic locking
- create_version() - creating new process versions
- activate_version() - activating process versions
- deprecate() - deprecating processes
- delete() - soft and hard delete
- count_by_status() - counting processes by status
- count_by_category() - counting processes by category
- create_execution() - creating process executions
- get_execution_by_id() - retrieving executions
- list_executions() - listing executions
- start_execution() - starting executions
- advance_execution() - advancing execution to next stage
- complete_execution() - completing executions
- fail_execution() - marking executions as failed
- cancel_execution() - canceling executions
"""

from uuid import uuid4

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from tests.test_constants import COUNT_FIVE, COUNT_THREE, COUNT_TWO
from tracertm.core.concurrency import ConcurrencyError
from tracertm.repositories.process_repository import ProcessRepository
from tracertm.repositories.project_repository import ProjectRepository


def unique_project_name() -> str:
    """Generate a unique project name for tests."""
    return f"Test Project {uuid4().hex[:8]}"


# ============================================================================
# CREATE OPERATIONS
# ============================================================================


@pytest.mark.unit
@pytest.mark.asyncio
async def test_create_process_basic(db_session: AsyncSession) -> None:
    """Test creating process with basic fields."""
    project_repo = ProjectRepository(db_session)
    project = await project_repo.create(name=unique_project_name())
    await db_session.commit()

    repo = ProcessRepository(db_session)
    process = await repo.create(
        project_id=project.id,
        name="Test Process",
    )

    assert process.id is not None
    assert process.process_number is not None
    assert process.process_number.startswith("PROC-")
    assert process.name == "Test Process"
    assert process.status == "draft"
    assert process.version == 1
    assert process.version_number == 1
    assert process.is_active_version is True


@pytest.mark.unit
@pytest.mark.asyncio
async def test_create_process_with_description(db_session: AsyncSession) -> None:
    """Test creating process with description and purpose."""
    project_repo = ProjectRepository(db_session)
    project = await project_repo.create(name=unique_project_name())
    await db_session.commit()

    repo = ProcessRepository(db_session)
    process = await repo.create(
        project_id=project.id,
        name="Test Process",
        description="Process description",
        purpose="Process purpose",
    )

    assert process.description == "Process description"
    assert process.purpose == "Process purpose"


@pytest.mark.unit
@pytest.mark.asyncio
async def test_create_process_with_classification(db_session: AsyncSession) -> None:
    """Test creating process with classification fields."""
    project_repo = ProjectRepository(db_session)
    project = await project_repo.create(name=unique_project_name())
    await db_session.commit()

    repo = ProcessRepository(db_session)
    process = await repo.create(
        project_id=project.id,
        name="Test Process",
        category="operational",
        tags=["critical", "automated"],
    )

    assert process.category == "operational"
    assert process.tags == ["critical", "automated"]


@pytest.mark.unit
@pytest.mark.asyncio
async def test_create_process_with_stages(db_session: AsyncSession) -> None:
    """Test creating process with stage definitions."""
    project_repo = ProjectRepository(db_session)
    project = await project_repo.create(name=unique_project_name())
    await db_session.commit()

    stages = [
        {"id": "1", "name": "Initiate", "order": 1},
        {"id": "2", "name": "Review", "order": 2},
        {"id": "3", "name": "Approve", "order": 3},
    ]

    repo = ProcessRepository(db_session)
    process = await repo.create(
        project_id=project.id,
        name="Test Process",
        stages=stages,
    )

    assert process.stages == stages


@pytest.mark.unit
@pytest.mark.asyncio
async def test_create_process_with_swimlanes(db_session: AsyncSession) -> None:
    """Test creating process with swimlane definitions."""
    project_repo = ProjectRepository(db_session)
    project = await project_repo.create(name=unique_project_name())
    await db_session.commit()

    swimlanes = [
        {"id": "1", "name": "Requester", "role": "user"},
        {"id": "2", "name": "Approver", "role": "manager"},
    ]

    repo = ProcessRepository(db_session)
    process = await repo.create(
        project_id=project.id,
        name="Test Process",
        swimlanes=swimlanes,
    )

    assert process.swimlanes == swimlanes


@pytest.mark.unit
@pytest.mark.asyncio
async def test_create_process_with_inputs_outputs(db_session: AsyncSession) -> None:
    """Test creating process with inputs and outputs."""
    project_repo = ProjectRepository(db_session)
    project = await project_repo.create(name=unique_project_name())
    await db_session.commit()

    inputs = [{"name": "Request Form", "type": "document", "required": True}]
    outputs = [{"name": "Approval Record", "type": "document"}]

    repo = ProcessRepository(db_session)
    process = await repo.create(
        project_id=project.id,
        name="Test Process",
        inputs=inputs,
        outputs=outputs,
    )

    assert process.inputs == inputs
    assert process.outputs == outputs


@pytest.mark.unit
@pytest.mark.asyncio
async def test_create_process_with_triggers(db_session: AsyncSession) -> None:
    """Test creating process with triggers and exit criteria."""
    project_repo = ProjectRepository(db_session)
    project = await project_repo.create(name=unique_project_name())
    await db_session.commit()

    triggers = [{"type": "event", "name": "New Request Submitted"}]
    exit_criteria = ["All stages completed", "Manager approved"]

    repo = ProcessRepository(db_session)
    process = await repo.create(
        project_id=project.id,
        name="Test Process",
        triggers=triggers,
        exit_criteria=exit_criteria,
    )

    assert process.triggers == triggers
    assert process.exit_criteria == exit_criteria


@pytest.mark.unit
@pytest.mark.asyncio
async def test_create_process_with_bpmn(db_session: AsyncSession) -> None:
    """Test creating process with BPMN XML."""
    project_repo = ProjectRepository(db_session)
    project = await project_repo.create(name=unique_project_name())
    await db_session.commit()

    bpmn_xml = "<bpmn>...</bpmn>"

    repo = ProcessRepository(db_session)
    process = await repo.create(
        project_id=project.id,
        name="Test Process",
        bpmn_xml=bpmn_xml,
    )

    assert process.bpmn_xml == bpmn_xml


@pytest.mark.unit
@pytest.mark.asyncio
async def test_create_process_with_ownership(db_session: AsyncSession) -> None:
    """Test creating process with ownership fields."""
    project_repo = ProjectRepository(db_session)
    project = await project_repo.create(name=unique_project_name())
    await db_session.commit()

    repo = ProcessRepository(db_session)
    process = await repo.create(
        project_id=project.id,
        name="Test Process",
        owner="john.doe@example.com",
        responsible_team="Platform Team",
    )

    assert process.owner == "john.doe@example.com"
    assert process.responsible_team == "Platform Team"


@pytest.mark.unit
@pytest.mark.asyncio
async def test_create_process_with_metrics(db_session: AsyncSession) -> None:
    """Test creating process with metrics."""
    project_repo = ProjectRepository(db_session)
    project = await project_repo.create(name=unique_project_name())
    await db_session.commit()

    repo = ProcessRepository(db_session)
    process = await repo.create(
        project_id=project.id,
        name="Test Process",
        expected_duration_hours=8,
        sla_hours=24,
    )

    assert process.expected_duration_hours == 8
    assert process.sla_hours == 24


@pytest.mark.unit
@pytest.mark.asyncio
async def test_create_process_with_metadata(db_session: AsyncSession) -> None:
    """Test creating process with custom metadata."""
    project_repo = ProjectRepository(db_session)
    project = await project_repo.create(name=unique_project_name())
    await db_session.commit()

    repo = ProcessRepository(db_session)
    process = await repo.create(
        project_id=project.id,
        name="Test Process",
        metadata={"custom_field": "custom_value"},
    )

    assert process.process_metadata == {"custom_field": "custom_value"}


# ============================================================================
# GET_BY_ID OPERATIONS
# ============================================================================


@pytest.mark.unit
@pytest.mark.asyncio
async def test_get_by_id_found(db_session: AsyncSession) -> None:
    """Test retrieving process by ID when found."""
    project_repo = ProjectRepository(db_session)
    project = await project_repo.create(name=unique_project_name())
    await db_session.commit()

    repo = ProcessRepository(db_session)
    created = await repo.create(project_id=project.id, name="Test Process")
    await db_session.commit()

    found = await repo.get_by_id(created.id)
    assert found is not None
    assert found.id == created.id
    assert found.name == "Test Process"


@pytest.mark.unit
@pytest.mark.asyncio
async def test_get_by_id_not_found(db_session: AsyncSession) -> None:
    """Test retrieving process by ID when not found."""
    repo = ProcessRepository(db_session)
    found = await repo.get_by_id(str(uuid4()))
    assert found is None


@pytest.mark.unit
@pytest.mark.asyncio
async def test_get_by_id_excludes_deleted(db_session: AsyncSession) -> None:
    """Test that get_by_id excludes soft-deleted processes."""
    project_repo = ProjectRepository(db_session)
    project = await project_repo.create(name=unique_project_name())
    await db_session.commit()

    repo = ProcessRepository(db_session)
    process = await repo.create(project_id=project.id, name="Test Process")
    await db_session.commit()

    await repo.delete(process.id, soft=True)
    await db_session.commit()

    found = await repo.get_by_id(process.id)
    assert found is None


@pytest.mark.unit
@pytest.mark.asyncio
async def test_get_by_id_scoped_to_project(db_session: AsyncSession) -> None:
    """Test retrieving process by ID scoped to project."""
    project_repo = ProjectRepository(db_session)
    project1 = await project_repo.create(name=unique_project_name())
    project2 = await project_repo.create(name=unique_project_name())
    await db_session.commit()

    repo = ProcessRepository(db_session)
    process = await repo.create(project_id=project1.id, name="Test Process")
    await db_session.commit()

    # Should find with correct project
    found1 = await repo.get_by_id(process.id, project_id=project1.id)
    assert found1 is not None

    # Should not find with wrong project
    found2 = await repo.get_by_id(process.id, project_id=project2.id)
    assert found2 is None


# ============================================================================
# GET_BY_NUMBER OPERATIONS
# ============================================================================


@pytest.mark.unit
@pytest.mark.asyncio
async def test_get_by_number_found(db_session: AsyncSession) -> None:
    """Test retrieving process by process number when found."""
    project_repo = ProjectRepository(db_session)
    project = await project_repo.create(name=unique_project_name())
    await db_session.commit()

    repo = ProcessRepository(db_session)
    created = await repo.create(project_id=project.id, name="Test Process")
    await db_session.commit()

    found = await repo.get_by_number(created.process_number)
    assert found is not None
    assert found.process_number == created.process_number


@pytest.mark.unit
@pytest.mark.asyncio
async def test_get_by_number_not_found(db_session: AsyncSession) -> None:
    """Test retrieving process by number when not found."""
    repo = ProcessRepository(db_session)
    found = await repo.get_by_number("PROC-NONEXISTENT")
    assert found is None


# ============================================================================
# LIST_ALL OPERATIONS
# ============================================================================


@pytest.mark.unit
@pytest.mark.asyncio
async def test_list_all_basic(db_session: AsyncSession) -> None:
    """Test listing processes for a project."""
    project_repo = ProjectRepository(db_session)
    project = await project_repo.create(name=unique_project_name())
    await db_session.commit()

    repo = ProcessRepository(db_session)
    await repo.create(project_id=project.id, name="Process 1")
    await repo.create(project_id=project.id, name="Process 2")
    await repo.create(project_id=project.id, name="Process 3")
    await db_session.commit()

    processes = await repo.list_all(project_id=project.id)
    assert len(processes) == COUNT_THREE


@pytest.mark.unit
@pytest.mark.asyncio
async def test_list_all_excludes_deleted(db_session: AsyncSession) -> None:
    """Test listing processes excludes deleted by default."""
    project_repo = ProjectRepository(db_session)
    project = await project_repo.create(name=unique_project_name())
    await db_session.commit()

    repo = ProcessRepository(db_session)
    p1 = await repo.create(project_id=project.id, name="Process 1")
    await repo.create(project_id=project.id, name="Process 2")
    await db_session.commit()

    await repo.delete(p1.id, soft=True)
    await db_session.commit()

    processes = await repo.list_all(project_id=project.id)
    assert len(processes) == 1


@pytest.mark.unit
@pytest.mark.asyncio
async def test_list_all_include_deleted(db_session: AsyncSession) -> None:
    """Test listing processes can include deleted."""
    project_repo = ProjectRepository(db_session)
    project = await project_repo.create(name=unique_project_name())
    await db_session.commit()

    repo = ProcessRepository(db_session)
    p1 = await repo.create(project_id=project.id, name="Process 1")
    await repo.create(project_id=project.id, name="Process 2")
    await db_session.commit()

    await repo.delete(p1.id, soft=True)
    await db_session.commit()

    processes = await repo.list_all(project_id=project.id, include_deleted=True)
    assert len(processes) == COUNT_TWO


@pytest.mark.unit
@pytest.mark.asyncio
async def test_list_all_filter_by_status(db_session: AsyncSession) -> None:
    """Test filtering processes by status."""
    project_repo = ProjectRepository(db_session)
    project = await project_repo.create(name=unique_project_name())
    await db_session.commit()

    repo = ProcessRepository(db_session)
    p1 = await repo.create(project_id=project.id, name="Process 1")
    await repo.create(project_id=project.id, name="Process 2")
    await db_session.commit()

    # Activate one process
    await repo.activate_version(p1.id)
    await db_session.commit()

    draft_processes = await repo.list_all(project_id=project.id, status="draft")
    active_processes = await repo.list_all(project_id=project.id, status="active")

    assert len(draft_processes) == 1
    assert len(active_processes) == 1


@pytest.mark.unit
@pytest.mark.asyncio
async def test_list_all_filter_by_category(db_session: AsyncSession) -> None:
    """Test filtering processes by category."""
    project_repo = ProjectRepository(db_session)
    project = await project_repo.create(name=unique_project_name())
    await db_session.commit()

    repo = ProcessRepository(db_session)
    await repo.create(project_id=project.id, name="Process 1", category="operational")
    await repo.create(project_id=project.id, name="Process 2", category="support")
    await db_session.commit()

    operational = await repo.list_all(project_id=project.id, category="operational")
    assert len(operational) == 1
    assert operational[0].name == "Process 1"


@pytest.mark.unit
@pytest.mark.asyncio
async def test_list_all_filter_by_owner(db_session: AsyncSession) -> None:
    """Test filtering processes by owner."""
    project_repo = ProjectRepository(db_session)
    project = await project_repo.create(name=unique_project_name())
    await db_session.commit()

    repo = ProcessRepository(db_session)
    await repo.create(project_id=project.id, name="Process 1", owner="alice")
    await repo.create(project_id=project.id, name="Process 2", owner="bob")
    await db_session.commit()

    alice_processes = await repo.list_all(project_id=project.id, owner="alice")
    assert len(alice_processes) == 1
    assert alice_processes[0].name == "Process 1"


@pytest.mark.unit
@pytest.mark.asyncio
async def test_list_all_filter_active_only(db_session: AsyncSession) -> None:
    """Test filtering only active versions."""
    project_repo = ProjectRepository(db_session)
    project = await project_repo.create(name=unique_project_name())
    await db_session.commit()

    repo = ProcessRepository(db_session)
    p1 = await repo.create(project_id=project.id, name="Process 1")
    await repo.create(project_id=project.id, name="Process 2")
    await db_session.commit()

    # Create a new version of p1 (which starts as inactive)
    await repo.create_version(p1.id)
    await db_session.commit()

    # All processes including inactive versions
    all_processes = await repo.list_all(project_id=project.id)
    # Only active versions
    active_only = await repo.list_all(project_id=project.id, active_only=True)

    assert len(all_processes) == COUNT_THREE
    assert len(active_only) == COUNT_TWO


@pytest.mark.unit
@pytest.mark.asyncio
async def test_list_all_pagination(db_session: AsyncSession) -> None:
    """Test pagination in list_all."""
    project_repo = ProjectRepository(db_session)
    project = await project_repo.create(name=unique_project_name())
    await db_session.commit()

    repo = ProcessRepository(db_session)
    for i in range(10):
        await repo.create(project_id=project.id, name=f"Process {i}")
    await db_session.commit()

    page1 = await repo.list_all(project_id=project.id, limit=5, offset=0)
    page2 = await repo.list_all(project_id=project.id, limit=5, offset=5)

    assert len(page1) == COUNT_FIVE
    assert len(page2) == COUNT_FIVE


# ============================================================================
# UPDATE OPERATIONS
# ============================================================================


@pytest.mark.unit
@pytest.mark.asyncio
async def test_update_basic_fields(db_session: AsyncSession) -> None:
    """Test updating basic process fields."""
    project_repo = ProjectRepository(db_session)
    project = await project_repo.create(name=unique_project_name())
    await db_session.commit()

    repo = ProcessRepository(db_session)
    process = await repo.create(project_id=project.id, name="Original Name")
    await db_session.commit()

    updated = await repo.update(
        process.id,
        expected_version=1,
        name="Updated Name",
        description="Updated Description",
    )

    assert updated.name == "Updated Name"
    assert updated.description == "Updated Description"
    assert updated.version == COUNT_TWO


@pytest.mark.unit
@pytest.mark.asyncio
async def test_update_optimistic_locking_failure(db_session: AsyncSession) -> None:
    """Test that update fails with stale version."""
    project_repo = ProjectRepository(db_session)
    project = await project_repo.create(name=unique_project_name())
    await db_session.commit()

    repo = ProcessRepository(db_session)
    process = await repo.create(project_id=project.id, name="Test")
    await db_session.commit()

    # First update
    await repo.update(process.id, expected_version=1, name="First Update")
    await db_session.commit()

    # Try to update with stale version
    with pytest.raises(ConcurrencyError):
        await repo.update(process.id, expected_version=1, name="Second Update")


@pytest.mark.unit
@pytest.mark.asyncio
async def test_update_not_found(db_session: AsyncSession) -> None:
    """Test updating non-existent process."""
    repo = ProcessRepository(db_session)

    with pytest.raises(ValueError, match="not found"):
        await repo.update(str(uuid4()), expected_version=1, name="Test")


# ============================================================================
# CREATE_VERSION OPERATIONS
# ============================================================================


@pytest.mark.unit
@pytest.mark.asyncio
async def test_create_version(db_session: AsyncSession) -> None:
    """Test creating a new version of a process."""
    project_repo = ProjectRepository(db_session)
    project = await project_repo.create(name=unique_project_name())
    await db_session.commit()

    repo = ProcessRepository(db_session)
    original = await repo.create(
        project_id=project.id,
        name="Test Process",
        stages=[{"id": "1", "name": "Stage 1"}],
    )
    await db_session.commit()

    new_version = await repo.create_version(
        original.id,
        version_notes="Minor improvements",
    )

    assert new_version.id != original.id
    assert new_version.version_number == COUNT_TWO
    assert new_version.is_active_version is False  # New versions start inactive
    assert new_version.parent_version_id == original.id
    assert new_version.version_notes == "Minor improvements"
    assert new_version.name == original.name
    assert new_version.stages == original.stages


@pytest.mark.unit
@pytest.mark.asyncio
async def test_create_version_not_found(db_session: AsyncSession) -> None:
    """Test creating version for non-existent process."""
    repo = ProcessRepository(db_session)

    with pytest.raises(ValueError, match="not found"):
        await repo.create_version(str(uuid4()))


# ============================================================================
# ACTIVATE_VERSION OPERATIONS
# ============================================================================


@pytest.mark.unit
@pytest.mark.asyncio
async def test_activate_version(db_session: AsyncSession) -> None:
    """Test activating a process version."""
    project_repo = ProjectRepository(db_session)
    project = await project_repo.create(name=unique_project_name())
    await db_session.commit()

    repo = ProcessRepository(db_session)
    process = await repo.create(project_id=project.id, name="Test Process")
    await db_session.commit()

    activated = await repo.activate_version(process.id, activated_by="admin")

    assert activated.is_active_version is True
    assert activated.status == "active"
    assert activated.activated_at is not None
    assert activated.activated_by == "admin"


@pytest.mark.unit
@pytest.mark.asyncio
async def test_activate_version_deactivates_others(db_session: AsyncSession) -> None:
    """Test that activating a version deactivates others with same name."""
    project_repo = ProjectRepository(db_session)
    project = await project_repo.create(name=unique_project_name())
    await db_session.commit()

    repo = ProcessRepository(db_session)
    p1 = await repo.create(project_id=project.id, name="Test Process")
    await db_session.commit()

    # Create new version
    p2 = await repo.create_version(p1.id)
    await db_session.commit()

    # Activate first version
    await repo.activate_version(p1.id)
    await db_session.commit()

    # Activate second version - should deactivate first
    await repo.activate_version(p2.id)
    await db_session.commit()

    # Refresh first process
    await db_session.refresh(p1)

    assert p1.is_active_version is False
    assert p2.is_active_version is True


@pytest.mark.unit
@pytest.mark.asyncio
async def test_activate_version_not_found(db_session: AsyncSession) -> None:
    """Test activating non-existent process."""
    repo = ProcessRepository(db_session)

    with pytest.raises(ValueError, match="not found"):
        await repo.activate_version(str(uuid4()))


# ============================================================================
# DEPRECATE OPERATIONS
# ============================================================================


@pytest.mark.unit
@pytest.mark.asyncio
async def test_deprecate(db_session: AsyncSession) -> None:
    """Test deprecating a process."""
    project_repo = ProjectRepository(db_session)
    project = await project_repo.create(name=unique_project_name())
    await db_session.commit()

    repo = ProcessRepository(db_session)
    process = await repo.create(project_id=project.id, name="Test Process")
    await db_session.commit()

    deprecated = await repo.deprecate(
        process.id,
        deprecation_reason="Replaced by new process",
        deprecated_by="admin",
    )

    assert deprecated.status == "deprecated"
    assert deprecated.deprecated_at is not None
    assert deprecated.deprecated_by == "admin"
    assert deprecated.deprecation_reason == "Replaced by new process"


@pytest.mark.unit
@pytest.mark.asyncio
async def test_deprecate_not_found(db_session: AsyncSession) -> None:
    """Test deprecating non-existent process."""
    repo = ProcessRepository(db_session)

    with pytest.raises(ValueError, match="not found"):
        await repo.deprecate(str(uuid4()))


# ============================================================================
# DELETE OPERATIONS
# ============================================================================


@pytest.mark.unit
@pytest.mark.asyncio
async def test_delete_soft(db_session: AsyncSession) -> None:
    """Test soft delete of process."""
    project_repo = ProjectRepository(db_session)
    project = await project_repo.create(name=unique_project_name())
    await db_session.commit()

    repo = ProcessRepository(db_session)
    process = await repo.create(project_id=project.id, name="Test")
    await db_session.commit()

    result = await repo.delete(process.id, soft=True)
    assert result is True

    found = await repo.get_by_id(process.id)
    assert found is None


@pytest.mark.unit
@pytest.mark.asyncio
async def test_delete_hard(db_session: AsyncSession) -> None:
    """Test hard delete of process."""
    project_repo = ProjectRepository(db_session)
    project = await project_repo.create(name=unique_project_name())
    await db_session.commit()

    repo = ProcessRepository(db_session)
    process = await repo.create(project_id=project.id, name="Test")
    await db_session.commit()

    result = await repo.delete(process.id, soft=False)
    assert result is True


@pytest.mark.unit
@pytest.mark.asyncio
async def test_delete_not_found(db_session: AsyncSession) -> None:
    """Test delete of non-existent process."""
    repo = ProcessRepository(db_session)
    result = await repo.delete(str(uuid4()), soft=True)
    assert result is False


# ============================================================================
# COUNT OPERATIONS
# ============================================================================


@pytest.mark.unit
@pytest.mark.asyncio
async def test_count_by_status(db_session: AsyncSession) -> None:
    """Test counting processes by status."""
    project_repo = ProjectRepository(db_session)
    project = await project_repo.create(name=unique_project_name())
    await db_session.commit()

    repo = ProcessRepository(db_session)
    p1 = await repo.create(project_id=project.id, name="Process 1")
    await repo.create(project_id=project.id, name="Process 2")
    await repo.create(project_id=project.id, name="Process 3")
    await db_session.commit()

    await repo.activate_version(p1.id)
    await db_session.commit()

    counts = await repo.count_by_status(project.id)
    assert counts.get("draft") == COUNT_TWO
    assert counts.get("active") == 1


@pytest.mark.unit
@pytest.mark.asyncio
async def test_count_by_category(db_session: AsyncSession) -> None:
    """Test counting processes by category."""
    project_repo = ProjectRepository(db_session)
    project = await project_repo.create(name=unique_project_name())
    await db_session.commit()

    repo = ProcessRepository(db_session)
    await repo.create(project_id=project.id, name="Process 1", category="operational")
    await repo.create(project_id=project.id, name="Process 2", category="operational")
    await repo.create(project_id=project.id, name="Process 3", category="support")
    await db_session.commit()

    counts = await repo.count_by_category(project.id)
    assert counts.get("operational") == COUNT_TWO
    assert counts.get("support") == 1


# ============================================================================
# EXECUTION OPERATIONS
# ============================================================================


@pytest.mark.unit
@pytest.mark.asyncio
async def test_create_execution(db_session: AsyncSession) -> None:
    """Test creating a process execution."""
    project_repo = ProjectRepository(db_session)
    project = await project_repo.create(name=unique_project_name())
    await db_session.commit()

    repo = ProcessRepository(db_session)
    process = await repo.create(project_id=project.id, name="Test Process")
    await db_session.commit()

    execution = await repo.create_execution(
        process.id,
        initiated_by="user1",
        context_data={"key": "value"},
    )

    assert execution.id is not None
    assert execution.execution_number is not None
    assert execution.execution_number.startswith("EXE-")
    assert execution.process_id == process.id
    assert execution.status == "pending"
    assert execution.initiated_by == "user1"
    assert execution.context_data == {"key": "value"}


@pytest.mark.unit
@pytest.mark.asyncio
async def test_create_execution_process_not_found(db_session: AsyncSession) -> None:
    """Test creating execution for non-existent process."""
    repo = ProcessRepository(db_session)

    with pytest.raises(ValueError, match="not found"):
        await repo.create_execution(str(uuid4()))


@pytest.mark.unit
@pytest.mark.asyncio
async def test_get_execution_by_id(db_session: AsyncSession) -> None:
    """Test retrieving execution by ID."""
    project_repo = ProjectRepository(db_session)
    project = await project_repo.create(name=unique_project_name())
    await db_session.commit()

    repo = ProcessRepository(db_session)
    process = await repo.create(project_id=project.id, name="Test Process")
    await db_session.commit()

    execution = await repo.create_execution(process.id)
    await db_session.commit()

    found = await repo.get_execution_by_id(execution.id)
    assert found is not None
    assert found.id == execution.id


@pytest.mark.unit
@pytest.mark.asyncio
async def test_list_executions(db_session: AsyncSession) -> None:
    """Test listing executions for a process."""
    project_repo = ProjectRepository(db_session)
    project = await project_repo.create(name=unique_project_name())
    await db_session.commit()

    repo = ProcessRepository(db_session)
    process = await repo.create(project_id=project.id, name="Test Process")
    await db_session.commit()

    await repo.create_execution(process.id)
    await repo.create_execution(process.id)
    await repo.create_execution(process.id)
    await db_session.commit()

    executions = await repo.list_executions(process.id)
    assert len(executions) == COUNT_THREE


@pytest.mark.unit
@pytest.mark.asyncio
async def test_list_executions_filter_by_status(db_session: AsyncSession) -> None:
    """Test filtering executions by status."""
    project_repo = ProjectRepository(db_session)
    project = await project_repo.create(name=unique_project_name())
    await db_session.commit()

    repo = ProcessRepository(db_session)
    process = await repo.create(project_id=project.id, name="Test Process")
    await db_session.commit()

    e1 = await repo.create_execution(process.id)
    await repo.create_execution(process.id)
    await db_session.commit()

    await repo.start_execution(e1.id)
    await db_session.commit()

    pending = await repo.list_executions(process.id, status="pending")
    in_progress = await repo.list_executions(process.id, status="in_progress")

    assert len(pending) == 1
    assert len(in_progress) == 1


@pytest.mark.unit
@pytest.mark.asyncio
async def test_start_execution(db_session: AsyncSession) -> None:
    """Test starting a process execution."""
    project_repo = ProjectRepository(db_session)
    project = await project_repo.create(name=unique_project_name())
    await db_session.commit()

    repo = ProcessRepository(db_session)
    process = await repo.create(project_id=project.id, name="Test Process")
    await db_session.commit()

    execution = await repo.create_execution(process.id)
    await db_session.commit()

    started = await repo.start_execution(execution.id)

    assert started.status == "in_progress"
    assert started.started_at is not None


@pytest.mark.unit
@pytest.mark.asyncio
async def test_start_execution_not_found(db_session: AsyncSession) -> None:
    """Test starting non-existent execution."""
    repo = ProcessRepository(db_session)

    with pytest.raises(ValueError, match="not found"):
        await repo.start_execution(str(uuid4()))


@pytest.mark.unit
@pytest.mark.asyncio
async def test_advance_execution(db_session: AsyncSession) -> None:
    """Test advancing execution to next stage."""
    project_repo = ProjectRepository(db_session)
    project = await project_repo.create(name=unique_project_name())
    await db_session.commit()

    repo = ProcessRepository(db_session)
    process = await repo.create(project_id=project.id, name="Test Process")
    await db_session.commit()

    execution = await repo.create_execution(process.id)
    await db_session.commit()

    # Start and set initial stage
    await repo.start_execution(execution.id)
    await db_session.commit()

    # Advance to first stage
    advanced = await repo.advance_execution(execution.id, "stage_1")

    assert advanced.current_stage_id == "stage_1"

    # Advance to next stage
    advanced2 = await repo.advance_execution(execution.id, "stage_2")

    assert advanced2.current_stage_id == "stage_2"
    assert "stage_1" in advanced2.completed_stages


@pytest.mark.unit
@pytest.mark.asyncio
async def test_advance_execution_not_found(db_session: AsyncSession) -> None:
    """Test advancing non-existent execution."""
    repo = ProcessRepository(db_session)

    with pytest.raises(ValueError, match="not found"):
        await repo.advance_execution(str(uuid4()), "stage_1")


@pytest.mark.unit
@pytest.mark.asyncio
async def test_complete_execution(db_session: AsyncSession) -> None:
    """Test completing a process execution."""
    project_repo = ProjectRepository(db_session)
    project = await project_repo.create(name=unique_project_name())
    await db_session.commit()

    repo = ProcessRepository(db_session)
    process = await repo.create(project_id=project.id, name="Test Process")
    await db_session.commit()

    execution = await repo.create_execution(process.id)
    await repo.start_execution(execution.id)
    await db_session.commit()

    completed = await repo.complete_execution(
        execution.id,
        completed_by="user1",
        result_summary="Successfully completed",
        output_item_ids=["item1", "item2"],
    )

    assert completed.status == "completed"
    assert completed.completed_at is not None
    assert completed.completed_by == "user1"
    assert completed.result_summary == "Successfully completed"
    assert completed.output_item_ids == ["item1", "item2"]


@pytest.mark.unit
@pytest.mark.asyncio
async def test_complete_execution_not_found(db_session: AsyncSession) -> None:
    """Test completing non-existent execution."""
    repo = ProcessRepository(db_session)

    with pytest.raises(ValueError, match="not found"):
        await repo.complete_execution(str(uuid4()))


@pytest.mark.unit
@pytest.mark.asyncio
async def test_fail_execution(db_session: AsyncSession) -> None:
    """Test marking execution as failed."""
    project_repo = ProjectRepository(db_session)
    project = await project_repo.create(name=unique_project_name())
    await db_session.commit()

    repo = ProcessRepository(db_session)
    process = await repo.create(project_id=project.id, name="Test Process")
    await db_session.commit()

    execution = await repo.create_execution(process.id)
    await repo.start_execution(execution.id)
    await db_session.commit()

    failed = await repo.fail_execution(
        execution.id,
        result_summary="Error occurred during processing",
    )

    assert failed.status == "failed"
    assert failed.completed_at is not None
    assert failed.result_summary == "Error occurred during processing"


@pytest.mark.unit
@pytest.mark.asyncio
async def test_fail_execution_not_found(db_session: AsyncSession) -> None:
    """Test failing non-existent execution."""
    repo = ProcessRepository(db_session)

    with pytest.raises(ValueError, match="not found"):
        await repo.fail_execution(str(uuid4()))


@pytest.mark.unit
@pytest.mark.asyncio
async def test_cancel_execution(db_session: AsyncSession) -> None:
    """Test canceling a process execution."""
    project_repo = ProjectRepository(db_session)
    project = await project_repo.create(name=unique_project_name())
    await db_session.commit()

    repo = ProcessRepository(db_session)
    process = await repo.create(project_id=project.id, name="Test Process")
    await db_session.commit()

    execution = await repo.create_execution(process.id)
    await repo.start_execution(execution.id)
    await db_session.commit()

    cancelled = await repo.cancel_execution(
        execution.id,
        result_summary="Cancelled by user request",
    )

    assert cancelled.status == "cancelled"
    assert cancelled.completed_at is not None
    assert cancelled.result_summary == "Cancelled by user request"


@pytest.mark.unit
@pytest.mark.asyncio
async def test_cancel_execution_not_found(db_session: AsyncSession) -> None:
    """Test canceling non-existent execution."""
    repo = ProcessRepository(db_session)

    with pytest.raises(ValueError, match="not found"):
        await repo.cancel_execution(str(uuid4()))
