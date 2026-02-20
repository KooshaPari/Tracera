import uuid
from typing import Any

import pytest
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from tracertm.models.project import Project
from tracertm.repositories.workflow_schedule_repository import WorkflowScheduleRepository


@pytest.mark.asyncio
async def test_create_and_list_workflow_schedule(async_db_engine: Any) -> None:
    session_maker = async_sessionmaker(async_db_engine, class_=AsyncSession, expire_on_commit=False)
    async with session_maker() as session:
        project_id = uuid.uuid4()
        project = Project(id=project_id, name="Schedule Project")
        session.add(project)
        await session.flush()

        repo = WorkflowScheduleRepository(session)
        schedule = await repo.create_schedule(
            schedule_id="schedule-test",
            workflow_name="GraphSnapshotWorkflow",
            schedule_type="cron",
            schedule_spec={"cron_expressions": ["0 2 * * *"]},
            project_id=str(project_id),
            task_queue="tracertm-tasks",
            created_by_user_id="user-1",
        )
        await session.commit()

        schedules = await repo.list_schedules(project_id=str(project_id))
        assert len(schedules) == 1
        assert schedules[0].schedule_id == schedule.schedule_id
        assert schedules[0].workflow_name == "GraphSnapshotWorkflow"
