import pytest

from tracertm.models.project import Project
from tracertm.repositories.project_repository import ProjectRepository

pytestmark = pytest.mark.integration


@pytest.mark.asyncio
async def test_project_create_and_get(async_session):
    repo = ProjectRepository(async_session)
    project = await repo.create(name="Alpha", description="desc")

    by_id = await repo.get_by_id(project.id)
    by_name = await repo.get_by_name("Alpha")

    assert by_id.id == project.id
    assert by_name.name == "Alpha"


@pytest.mark.asyncio
async def test_project_update(async_session):
    repo = ProjectRepository(async_session)
    project = await repo.create(name="Alpha", description="desc")

    updated = await repo.update(project.id, name="Beta", description="new", metadata={"m": 1})
    assert updated.name == "Beta"
    assert updated.description == "new"
    assert updated.metadata == {"m": 1}
