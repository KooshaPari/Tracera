"""Repository for execution system (Execution, ExecutionArtifact, ExecutionEnvironmentConfig)."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any
from uuid import uuid4

from sqlalchemy import select

from tracertm.models.execution import Execution, ExecutionArtifact
from tracertm.models.execution_config import ExecutionEnvironmentConfig

if TYPE_CHECKING:
    from datetime import datetime

    from sqlalchemy.ext.asyncio import AsyncSession


class ExecutionRepository:
    """Repository for Execution CRUD operations."""

    def __init__(self, session: AsyncSession) -> None:
        """Initialize repository.

        Args:
            session: SQLAlchemy async session for database operations.
        """
        self.session = session

    async def create(
        self,
        project_id: str,
        execution_type: str,
        trigger_source: str,
        *,
        test_run_id: str | None = None,
        item_id: str | None = None,
        trigger_ref: str | None = None,
        config: dict[str, Any] | None = None,
    ) -> Execution:
        """Create a new execution record."""
        execution = Execution(
            id=str(uuid4()),
            project_id=project_id,
            execution_type=execution_type,
            trigger_source=trigger_source,
            status="pending",
            test_run_id=test_run_id,
            item_id=item_id,
            trigger_ref=trigger_ref,
            config=config,
        )
        self.session.add(execution)
        await self.session.flush()
        await self.session.refresh(execution)
        return execution

    async def get_by_id(self, execution_id: str) -> Execution | None:
        """Get execution by ID."""
        result = await self.session.execute(select(Execution).where(Execution.id == execution_id))
        return result.scalar_one_or_none()

    async def list_by_project(
        self,
        project_id: str,
        *,
        status: str | None = None,
        execution_type: str | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> list[Execution]:
        """List executions for a project."""
        q = select(Execution).where(Execution.project_id == project_id)
        if status:
            q = q.where(Execution.status == status)
        if execution_type:
            q = q.where(Execution.execution_type == execution_type)
        q = q.order_by(Execution.created_at.desc()).offset(offset).limit(limit)
        result = await self.session.execute(q)
        return list(result.scalars().all())

    async def update_status(
        self,
        execution_id: str,
        status: str,
        *,
        container_id: str | None = None,
        container_image: str | None = None,
        started_at: datetime | None = None,
        completed_at: datetime | None = None,
        duration_ms: int | None = None,
        exit_code: int | None = None,
        error_message: str | None = None,
        output_summary: str | None = None,
    ) -> Execution | None:
        """Update execution status and optional fields."""
        execution = await self.get_by_id(execution_id)
        if not execution:
            return None
        execution.status = status
        if container_id is not None:
            execution.container_id = container_id
        if container_image is not None:
            execution.container_image = container_image
        if started_at is not None:
            execution.started_at = started_at
        if completed_at is not None:
            execution.completed_at = completed_at
        if duration_ms is not None:
            execution.duration_ms = duration_ms
        if exit_code is not None:
            execution.exit_code = exit_code
        if error_message is not None:
            execution.error_message = error_message
        if output_summary is not None:
            execution.output_summary = output_summary
        await self.session.flush()
        await self.session.refresh(execution)
        return execution


class ExecutionArtifactRepository:
    """Repository for ExecutionArtifact CRUD operations."""

    def __init__(self, session: AsyncSession) -> None:
        """Initialize repository.

        Args:
            session: SQLAlchemy async session for database operations.
        """
        self.session = session

    async def create(
        self,
        execution_id: str,
        artifact_type: str,
        file_path: str,
        captured_at: datetime,
        *,
        item_id: str | None = None,
        thumbnail_path: str | None = None,
        file_size: int | None = None,
        mime_type: str | None = None,
        artifact_metadata: dict[str, Any] | None = None,
    ) -> ExecutionArtifact:
        """Create an execution artifact record."""
        artifact = ExecutionArtifact(
            id=str(uuid4()),
            execution_id=execution_id,
            artifact_type=artifact_type,
            file_path=file_path,
            captured_at=captured_at,
            item_id=item_id,
            thumbnail_path=thumbnail_path,
            file_size=file_size,
            mime_type=mime_type,
            artifact_metadata=artifact_metadata or {},
        )
        self.session.add(artifact)
        await self.session.flush()
        await self.session.refresh(artifact)
        return artifact

    async def get_by_id(self, artifact_id: str) -> ExecutionArtifact | None:
        """Get artifact by ID."""
        result = await self.session.execute(select(ExecutionArtifact).where(ExecutionArtifact.id == artifact_id))
        return result.scalar_one_or_none()

    async def list_by_execution(
        self,
        execution_id: str,
        *,
        artifact_type: str | None = None,
    ) -> list[ExecutionArtifact]:
        """List artifacts for an execution."""
        q = select(ExecutionArtifact).where(ExecutionArtifact.execution_id == execution_id)
        if artifact_type:
            q = q.where(ExecutionArtifact.artifact_type == artifact_type)
        q = q.order_by(ExecutionArtifact.captured_at.desc())
        result = await self.session.execute(q)
        return list(result.scalars().all())


class ExecutionEnvironmentConfigRepository:
    """Repository for ExecutionEnvironmentConfig CRUD operations."""

    def __init__(self, session: AsyncSession) -> None:
        """Initialize repository.

        Args:
            session: SQLAlchemy async session for database operations.
        """
        self.session = session

    async def get_by_project(self, project_id: str) -> ExecutionEnvironmentConfig | None:
        """Get config by project ID (one per project)."""
        result = await self.session.execute(
            select(ExecutionEnvironmentConfig).where(ExecutionEnvironmentConfig.project_id == project_id),
        )
        return result.scalar_one_or_none()

    async def create_or_update(
        self,
        project_id: str,
        **kwargs: object,
    ) -> ExecutionEnvironmentConfig:
        """Get or create execution environment config for project; update if exists."""
        existing = await self.get_by_project(project_id)
        if existing:
            for k, v in kwargs.items():
                if hasattr(existing, k):
                    setattr(existing, k, v)
            await self.session.flush()
            await self.session.refresh(existing)
            return existing
        config = ExecutionEnvironmentConfig(
            id=str(uuid4()),
            project_id=project_id,
        )
        for k, v in kwargs.items():
            if hasattr(config, k):
                setattr(config, k, v)
        self.session.add(config)
        await self.session.flush()
        await self.session.refresh(config)
        return config
