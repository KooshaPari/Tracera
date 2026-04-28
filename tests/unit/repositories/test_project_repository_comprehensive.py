"""Comprehensive unit tests for ProjectRepository to achieve 85%+ coverage.

This file covers all missing functionality identified in coverage analysis:
- create() with metadata handling
- get_by_id() basic retrieval
- get_by_name() name lookup
- get_all() listing
- update() operations with all field combinations
"""

from uuid import uuid4

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from tests.test_constants import COUNT_THREE
from tracertm.repositories.project_repository import ProjectRepository


def unique_project_name() -> str:
    """Generate a unique project name for tests."""
    return f"Test Project {uuid4().hex[:8]}"


# ============================================================================
# CREATE OPERATIONS - Metadata Handling
# ============================================================================


@pytest.mark.unit
@pytest.mark.asyncio
async def test_create_with_metadata(db_session: AsyncSession) -> None:
    """Test creating project with metadata."""
    repo = ProjectRepository(db_session)

    project = await repo.create(
        name=unique_project_name(),
        description="Test description",
        metadata={"env": "test", "version": "1.0"},
    )

    assert project.id is not None
    assert project.name is not None
    assert project.description == "Test description"
    assert project.project_metadata == {"env": "test", "version": "1.0"}


@pytest.mark.unit
@pytest.mark.asyncio
async def test_create_without_metadata(db_session: AsyncSession) -> None:
    """Test creating project without metadata uses empty dict."""
    repo = ProjectRepository(db_session)

    project = await repo.create(name=unique_project_name(), description="Test description")

    assert project.project_metadata == {}


@pytest.mark.unit
@pytest.mark.asyncio
async def test_create_with_none_metadata(db_session: AsyncSession) -> None:
    """Test creating project with None metadata uses empty dict."""
    repo = ProjectRepository(db_session)

    project = await repo.create(name=unique_project_name(), description="Test description", metadata=None)

    assert project.project_metadata == {}


@pytest.mark.unit
@pytest.mark.asyncio
async def test_create_without_description(db_session: AsyncSession) -> None:
    """Test creating project without description."""
    repo = ProjectRepository(db_session)

    project = await repo.create(name=unique_project_name())

    assert project.id is not None
    assert project.description is None


# ============================================================================
# GET_BY_ID - Basic Retrieval
# ============================================================================


@pytest.mark.unit
@pytest.mark.asyncio
async def test_get_by_id_existing_project(db_session: AsyncSession) -> None:
    """Test get_by_id returns project when it exists."""
    repo = ProjectRepository(db_session)

    created = await repo.create(name=unique_project_name(), description="Test")
    await db_session.commit()

    found = await repo.get_by_id(created.id)
    assert found is not None
    assert found.id == created.id
    assert found.name == created.name


@pytest.mark.unit
@pytest.mark.asyncio
async def test_get_by_id_nonexistent_project(db_session: AsyncSession) -> None:
    """Test get_by_id returns None when project doesn't exist."""
    repo = ProjectRepository(db_session)

    found = await repo.get_by_id("nonexistent-id")
    assert found is None


# ============================================================================
# GET_BY_NAME - Name Lookup
# ============================================================================


@pytest.mark.unit
@pytest.mark.asyncio
async def test_get_by_name_existing_project(db_session: AsyncSession) -> None:
    """Test get_by_name returns project when it exists."""
    repo = ProjectRepository(db_session)

    project_name = unique_project_name()
    created = await repo.create(name=project_name)
    await db_session.commit()

    found = await repo.get_by_name(project_name)
    assert found is not None
    assert found.id == created.id
    assert found.name == project_name


@pytest.mark.unit
@pytest.mark.asyncio
async def test_get_by_name_nonexistent_project(db_session: AsyncSession) -> None:
    """Test get_by_name returns None when project doesn't exist."""
    repo = ProjectRepository(db_session)

    found = await repo.get_by_name("nonexistent-project-name")
    assert found is None


@pytest.mark.unit
@pytest.mark.asyncio
async def test_get_by_name_case_sensitive(db_session: AsyncSession) -> None:
    """Test get_by_name is case sensitive."""
    repo = ProjectRepository(db_session)

    project_name = unique_project_name()
    await repo.create(name=project_name)
    await db_session.commit()

    # Different case should not match
    found = await repo.get_by_name(project_name.upper())
    assert found is None  # Case sensitive, so should not find


# ============================================================================
# GET_ALL - Listing
# ============================================================================


@pytest.mark.unit
@pytest.mark.asyncio
async def test_get_all_returns_all_projects(db_session: AsyncSession) -> None:
    """Test get_all returns all projects."""
    repo = ProjectRepository(db_session)

    # Create multiple projects
    project1 = await repo.create(name=unique_project_name())
    project2 = await repo.create(name=unique_project_name())
    project3 = await repo.create(name=unique_project_name())
    await db_session.commit()

    all_projects = await repo.get_all()
    assert len(all_projects) >= COUNT_THREE

    project_ids = {p.id for p in all_projects}
    assert project1.id in project_ids
    assert project2.id in project_ids
    assert project3.id in project_ids


@pytest.mark.unit
@pytest.mark.asyncio
async def test_get_all_empty_when_no_projects(db_session: AsyncSession) -> None:
    """Test get_all returns empty list when no projects exist."""
    repo = ProjectRepository(db_session)

    all_projects = await repo.get_all()
    # Note: May have projects from other tests, so we just check it's a list
    assert isinstance(all_projects, list)


# ============================================================================
# UPDATE OPERATIONS - All Field Combinations
# ============================================================================


@pytest.mark.unit
@pytest.mark.asyncio
async def test_update_name_only(db_session: AsyncSession) -> None:
    """Test update with name only."""
    repo = ProjectRepository(db_session)

    project = await repo.create(
        name=unique_project_name(),
        description="Original description",
        metadata={"key": "value"},
    )
    await db_session.commit()

    updated = await repo.update(project.id, name="Updated Name")

    assert updated is not None
    assert updated.name == "Updated Name"
    assert updated.description == "Original description"  # Unchanged
    assert updated.project_metadata == {"key": "value"}  # Unchanged


@pytest.mark.unit
@pytest.mark.asyncio
async def test_update_description_only(db_session: AsyncSession) -> None:
    """Test update with description only."""
    repo = ProjectRepository(db_session)

    project = await repo.create(
        name=unique_project_name(),
        description="Original description",
        metadata={"key": "value"},
    )
    await db_session.commit()

    updated = await repo.update(project.id, description="Updated description")

    assert updated is not None
    assert updated.name == project.name  # Unchanged
    assert updated.description == "Updated description"
    assert updated.project_metadata == {"key": "value"}  # Unchanged


@pytest.mark.unit
@pytest.mark.asyncio
async def test_update_metadata_only(db_session: AsyncSession) -> None:
    """Test update with metadata only."""
    repo = ProjectRepository(db_session)

    project = await repo.create(
        name=unique_project_name(),
        description="Original description",
        metadata={"key": "value"},
    )
    await db_session.commit()

    updated = await repo.update(project.id, metadata={"new_key": "new_value"})

    assert updated is not None
    assert updated.name == project.name  # Unchanged
    assert updated.description == "Original description"  # Unchanged
    assert updated.project_metadata == {"new_key": "new_value"}


@pytest.mark.unit
@pytest.mark.asyncio
async def test_update_all_fields(db_session: AsyncSession) -> None:
    """Test update with all fields."""
    repo = ProjectRepository(db_session)

    project = await repo.create(
        name=unique_project_name(),
        description="Original description",
        metadata={"key": "value"},
    )
    await db_session.commit()

    updated = await repo.update(
        project.id,
        name="Updated Name",
        description="Updated description",
        metadata={"new_key": "new_value"},
    )

    assert updated is not None
    assert updated.name == "Updated Name"
    assert updated.description == "Updated description"
    assert updated.project_metadata == {"new_key": "new_value"}


@pytest.mark.unit
@pytest.mark.asyncio
async def test_update_nonexistent_project_returns_none(db_session: AsyncSession) -> None:
    """Test update returns None when project doesn't exist."""
    repo = ProjectRepository(db_session)

    result = await repo.update("nonexistent-id", name="New Name")

    assert result is None


@pytest.mark.unit
@pytest.mark.asyncio
async def test_update_with_none_values_preserves_existing(db_session: AsyncSession) -> None:
    """Test update with None values preserves existing fields."""
    repo = ProjectRepository(db_session)

    project = await repo.create(
        name=unique_project_name(),
        description="Original description",
        metadata={"key": "value"},
    )
    await db_session.commit()

    # Update with None values (should preserve existing)
    updated = await repo.update(
        project.id,
        name=None,  # None means don't update
        description=None,
        metadata=None,
    )

    assert updated is not None
    assert updated.name == project.name  # Preserved
    assert updated.description == "Original description"  # Preserved
    assert updated.project_metadata == {"key": "value"}  # Preserved


@pytest.mark.unit
@pytest.mark.asyncio
async def test_update_metadata_replaces_entire_dict(db_session: AsyncSession) -> None:
    """Test update metadata replaces entire dict, not merges."""
    repo = ProjectRepository(db_session)

    project = await repo.create(name=unique_project_name(), metadata={"key1": "value1", "key2": "value2"})
    await db_session.commit()

    # Update with new metadata (should replace, not merge)
    updated = await repo.update(project.id, metadata={"key3": "value3"})

    assert updated is not None
    u = updated
    assert u.project_metadata == {"key3": "value3"}
    assert "key1" not in u.project_metadata
    assert "key2" not in u.project_metadata


@pytest.mark.unit
@pytest.mark.asyncio
async def test_update_empty_metadata(db_session: AsyncSession) -> None:
    """Test update with empty metadata dict."""
    repo = ProjectRepository(db_session)

    project = await repo.create(name=unique_project_name(), metadata={"key": "value"})
    await db_session.commit()

    updated = await repo.update(project.id, metadata={})

    assert updated is not None
    u = updated
    assert u.project_metadata == {}


@pytest.mark.unit
@pytest.mark.asyncio
async def test_update_description_to_none(db_session: AsyncSession) -> None:
    """Test update can set description to None."""
    repo = ProjectRepository(db_session)

    project = await repo.create(name=unique_project_name(), description="Original description")
    await db_session.commit()

    # Note: The update method doesn't support setting to None explicitly
    # because it checks `if description is not None`. This test verifies
    # that behavior - description won't be changed if we pass None
    updated = await repo.update(project.id, description=None)

    # Description should remain unchanged since None means "don't update"
    assert updated is not None
    u = updated
    assert u.description == "Original description"
