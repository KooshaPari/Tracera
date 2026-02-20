from typing import Any

import pytest

from tracertm.repositories.project_repository import ProjectRepository

pytestmark = pytest.mark.integration


@pytest.mark.asyncio
async def test_project_create_and_get(async_session: Any) -> None:
    repo = ProjectRepository(async_session)
    project = await repo.create(name="Alpha", description="desc")

    by_id = await repo.get_by_id(str(project.id))
    by_name = await repo.get_by_name("Alpha")

    assert by_id is not None and by_id.id == project.id
    assert by_name is not None and by_name.name == "Alpha"


@pytest.mark.asyncio
async def test_project_update(async_session: Any) -> None:
    repo = ProjectRepository(async_session)
    project = await repo.create(name="Alpha", description="desc")

    updated = await repo.update(str(project.id), name="Beta", description="new", metadata={"m": 1})
    assert updated is not None
    assert updated.name == "Beta"
    assert updated.description == "new"
    assert updated.metadata == {"m": 1}
