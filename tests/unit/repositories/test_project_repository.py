"""Unit tests for ProjectRepository."""

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from tests.test_constants import COUNT_THREE
from tracertm.repositories.project_repository import ProjectRepository


@pytest.mark.unit
@pytest.mark.asyncio
async def test_create_project(db_session: AsyncSession) -> None:
    """Test creating a project."""
    repo = ProjectRepository(db_session)

    project = await repo.create(
        name="Test Project",
        description="Test description",
    )

    assert project.id is not None
    assert project.name == "Test Project"
    assert project.description == "Test description"


@pytest.mark.unit
@pytest.mark.asyncio
async def test_get_by_id(db_session: AsyncSession) -> None:
    """Test retrieving a project by ID."""
    repo = ProjectRepository(db_session)
    created = await repo.create(name="Test Project", description="Test")

    retrieved = await repo.get_by_id(created.id)
    assert retrieved is not None
    assert retrieved.id == created.id
    assert retrieved.name == created.name


@pytest.mark.unit
@pytest.mark.asyncio
async def test_get_by_name(db_session: AsyncSession) -> None:
    """Test retrieving a project by name."""
    repo = ProjectRepository(db_session)
    created = await repo.create(name="Unique Project", description="Test")

    retrieved = await repo.get_by_name("Unique Project")
    assert retrieved is not None
    assert retrieved.id == created.id


@pytest.mark.unit
@pytest.mark.asyncio
async def test_update_project(db_session: AsyncSession) -> None:
    """Test updating a project."""
    repo = ProjectRepository(db_session)
    project = await repo.create(name="Original Name", description="Original")

    updated = await repo.update(
        project_id=project.id,
        name="Updated Name",
        description="Updated description",
    )

    assert updated is not None
    u = updated
    assert u.name == "Updated Name"
    assert u.description == "Updated description"


@pytest.mark.unit
@pytest.mark.asyncio
async def test_get_all_projects(db_session: AsyncSession) -> None:
    """Test listing all projects."""
    repo = ProjectRepository(db_session)

    await repo.create(name="Project 1", description="Test 1")
    await repo.create(name="Project 2", description="Test 2")
    await repo.create(name="Project 3", description="Test 3")

    projects = await repo.get_all()
    assert len(projects) == COUNT_THREE


@pytest.mark.unit
@pytest.mark.asyncio
async def test_get_by_name_not_found(db_session: AsyncSession) -> None:
    """Test getting project by name when not found."""
    repo = ProjectRepository(db_session)

    project = await repo.get_by_name("nonexistent")
    assert project is None


@pytest.mark.unit
@pytest.mark.asyncio
async def test_update_nonexistent_project(db_session: AsyncSession) -> None:
    """Test updating non-existent project returns None."""
    repo = ProjectRepository(db_session)

    result = await repo.update(
        project_id="nonexistent",
        name="Updated",
    )

    # Should return None or raise error
    assert result is None or isinstance(result, Exception)


@pytest.mark.unit
@pytest.mark.asyncio
async def test_project_with_description(db_session: AsyncSession) -> None:
    """Test creating project with description."""
    repo = ProjectRepository(db_session)

    project = await repo.create(
        name="Test Project",
        description="Detailed description with special chars: !@#$%",
    )

    retrieved = await repo.get_by_id(project.id)
    assert retrieved is not None
    r = retrieved
    assert r.description == "Detailed description with special chars: !@#$%"
