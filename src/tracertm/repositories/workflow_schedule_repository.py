"""Repository for workflow schedule tracking."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import TYPE_CHECKING, Any
from uuid import uuid4

from sqlalchemy import delete, select, update

from tracertm.models.workflow_schedule import WorkflowSchedule

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession


class WorkflowScheduleRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create_schedule(
        self,
        schedule_id: str,
        workflow_name: str,
        schedule_type: str,
        schedule_spec: dict[str, Any],
        project_id: str | None = None,
        task_queue: str | None = None,
        created_by_user_id: str | None = None,
        description: str | None = None,
    ) -> WorkflowSchedule:
        schedule = WorkflowSchedule(
            id=uuid4(),
            schedule_id=schedule_id,
            workflow_name=workflow_name,
            schedule_type=schedule_type,
            schedule_spec=schedule_spec,
            project_id=project_id,
            task_queue=task_queue,
            created_by_user_id=created_by_user_id,
            description=description,
            status="active",
        )
        self.session.add(schedule)
        await self.session.flush()
        return schedule

    async def list_schedules(
        self,
        project_id: str,
        limit: int = 100,
        offset: int = 0,
    ) -> list[WorkflowSchedule]:
        query = (
            select(WorkflowSchedule)
            .where(WorkflowSchedule.project_id == project_id)
            .order_by(WorkflowSchedule.created_at.desc())
            .offset(offset)
            .limit(limit)
        )
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def get_by_schedule_id(self, schedule_id: str) -> WorkflowSchedule | None:
        result = await self.session.execute(select(WorkflowSchedule).where(WorkflowSchedule.schedule_id == schedule_id))
        return result.scalar_one_or_none()

    async def mark_last_run(self, schedule_id: str, last_run_at: datetime) -> None:
        await self.session.execute(
            update(WorkflowSchedule)
            .where(WorkflowSchedule.schedule_id == schedule_id)
            .values(last_run_at=last_run_at, updated_at=datetime.now(UTC)),
        )

    async def delete_by_schedule_id(self, schedule_id: str) -> int:
        result = await self.session.execute(delete(WorkflowSchedule).where(WorkflowSchedule.schedule_id == schedule_id))
        return getattr(result, "rowcount", 0) or 0
