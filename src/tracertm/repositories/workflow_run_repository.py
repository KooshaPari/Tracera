"""Repository for workflow run tracking."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import TYPE_CHECKING, Any
from uuid import uuid4

from sqlalchemy import select, update

from tracertm.models.workflow_run import WorkflowRun

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession


class WorkflowRunRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create_run(
        self,
        workflow_name: str,
        payload: dict[str, Any] | None = None,
        project_id: str | None = None,
        graph_id: str | None = None,
        external_run_id: str | None = None,
        created_by_user_id: str | None = None,
    ) -> WorkflowRun:
        run = WorkflowRun(
            id=str(uuid4()),
            workflow_name=workflow_name,
            status="queued",
            payload=payload or {},
            result={},
            project_id=project_id,
            graph_id=graph_id,
            external_run_id=external_run_id,
            created_by_user_id=created_by_user_id,
        )
        self.session.add(run)
        await self.session.flush()
        return run

    async def list_runs(
        self,
        project_id: str,
        status: str | None = None,
        workflow_name: str | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> list[WorkflowRun]:
        query = select(WorkflowRun).where(WorkflowRun.project_id == project_id)
        if status:
            query = query.where(WorkflowRun.status == status)
        if workflow_name:
            query = query.where(WorkflowRun.workflow_name == workflow_name)
        query = query.order_by(WorkflowRun.created_at.desc()).offset(offset).limit(limit)
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def update_by_external_id(
        self,
        external_run_id: str,
        status: str,
        result: dict[str, Any] | None = None,
        error_message: str | None = None,
        started_at: datetime | None = None,
        completed_at: datetime | None = None,
    ) -> None:
        update_data: dict[str, Any] = {
            "status": status,
            "updated_at": datetime.now(UTC),
        }
        if result is not None:
            update_data["result"] = result
        if error_message is not None:
            update_data["error_message"] = error_message
        if started_at is not None:
            update_data["started_at"] = started_at
        if completed_at is not None:
            update_data["completed_at"] = completed_at

        await self.session.execute(
            update(WorkflowRun).where(WorkflowRun.external_run_id == external_run_id).values(**update_data),
        )
