"""Repository for workflow run tracking."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import TYPE_CHECKING, Any
from uuid import uuid4

from sqlalchemy import column, select, update

from tracertm.models.workflow_run import WorkflowRun

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession


class WorkflowRunRepository:
    """Repository for workflow run operations and tracking."""

    def __init__(self, session: AsyncSession) -> None:
        """Initialize repository.

        Args:
            session: SQLAlchemy async session for database operations.
        """
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
        """Create a new workflow run.

        Args:
            workflow_name: Name of the workflow to run.
            payload: Optional workflow input payload.
            project_id: Optional associated project ID.
            graph_id: Optional associated graph ID.
            external_run_id: Optional external workflow system run ID.
            created_by_user_id: Optional user ID who triggered the run.

        Returns:
            Created WorkflowRun instance.
        """
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
        """List workflow runs with optional filtering.

        Args:
            project_id: Project ID to filter by.
            status: Optional status filter (queued, running, completed, failed).
            workflow_name: Optional workflow name filter.
            limit: Maximum number of results (default 100).
            offset: Number of results to skip (default 0).

        Returns:
            List of matching WorkflowRun instances.
        """
        query = select(WorkflowRun).where(column("project_id") == project_id)
        if status:
            query = query.where(WorkflowRun.status == status)
        if workflow_name:
            query = query.where(column("workflow_name") == workflow_name)
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
        """Update workflow run by external ID.

        Args:
            external_run_id: External workflow system run ID.
            status: New status value.
            result: Optional workflow result data.
            error_message: Optional error message if failed.
            started_at: Optional workflow start timestamp.
            completed_at: Optional workflow completion timestamp.
        """
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
            update(WorkflowRun).where(column("external_run_id") == external_run_id).values(**update_data),
        )
