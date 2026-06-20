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
    """Repository for workflow schedule CRUD and query operations."""

    def __init__(self, session: AsyncSession) -> None:
        """Initialize repository.

        Args:
            session: SQLAlchemy async session for database operations.
        """
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
        """Create a new workflow schedule.

        Args:
            schedule_id: Unique schedule identifier.
            workflow_name: Name of the workflow to schedule.
            schedule_type: Type of schedule (cron, interval, etc.).
            schedule_spec: Schedule specification details.
            project_id: Optional project association.
            task_queue: Optional task queue assignment.
            created_by_user_id: Optional user ID who created the schedule.
            description: Optional schedule description.

        Returns:
            Created WorkflowSchedule instance.
        """
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
        """List workflow schedules for a project.

        Args:
            project_id: Project ID to filter schedules.
            limit: Maximum number of schedules to return.
            offset: Number of schedules to skip.

        Returns:
            List of WorkflowSchedule instances ordered by creation date.
        """
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
        """Get workflow schedule by schedule ID.

        Args:
            schedule_id: Schedule identifier.

        Returns:
            WorkflowSchedule if found, None otherwise.
        """
        result = await self.session.execute(select(WorkflowSchedule).where(WorkflowSchedule.schedule_id == schedule_id))
        return result.scalar_one_or_none()

    async def mark_last_run(self, schedule_id: str, last_run_at: datetime) -> None:
        """Update the last run timestamp for a schedule.

        Args:
            schedule_id: Schedule identifier.
            last_run_at: Timestamp of last execution.
        """
        await self.session.execute(
            update(WorkflowSchedule)
            .where(WorkflowSchedule.schedule_id == schedule_id)
            .values(last_run_at=last_run_at, updated_at=datetime.now(UTC)),
        )

    async def delete_by_schedule_id(self, schedule_id: str) -> int:
        """Delete a workflow schedule by schedule ID.

        Args:
            schedule_id: Schedule identifier.

        Returns:
            Number of rows deleted (0 or 1).
        """
        result = await self.session.execute(delete(WorkflowSchedule).where(WorkflowSchedule.schedule_id == schedule_id))
        return getattr(result, "rowcount", 0) or 0
