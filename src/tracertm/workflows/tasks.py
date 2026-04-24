"""Workflow task implementations for Temporal or local execution."""

from __future__ import annotations

import asyncio
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from tracertm.config.manager import ConfigManager
from tracertm.repositories.workflow_run_repository import WorkflowRunRepository
from tracertm.services.export_service import ExportService
from tracertm.services.graph_snapshot_service import GraphSnapshotService
from tracertm.services.graph_validation_service import GraphValidationService
from tracertm.services.integration_sync_processor import IntegrationSyncProcessor


@dataclass
class WorkflowUpdateConfig:
    """Configuration for updating workflow run status."""

    status: str
    result: dict[str, Any] | None = None
    error_message: str | None = None
    started: bool = False
    completed: bool = False


async def _get_async_session() -> AsyncSession:
    await asyncio.sleep(0)
    config = ConfigManager()
    database_url_raw = config.get("database_url")
    if not database_url_raw:
        msg = "Database not configured"
        raise ValueError(msg)
    database_url = str(database_url_raw)

    if database_url.startswith("sqlite:///"):
        async_database_url = database_url.replace("sqlite:///", "sqlite+aiosqlite:///", 1)
    elif database_url.startswith("sqlite://"):
        async_database_url = database_url.replace("sqlite://", "sqlite+aiosqlite://", 1)
    elif database_url.startswith("postgresql://"):
        base_url = database_url.split("?")[0]
        async_database_url = base_url.replace("postgresql://", "postgresql+asyncpg://", 1)
    else:
        async_database_url = database_url

    engine = create_async_engine(async_database_url, echo=False)
    session_factory = async_sessionmaker(engine, expire_on_commit=False)
    return session_factory()


async def _update_workflow_run(
    session: AsyncSession,
    external_run_id: str | None,
    config: WorkflowUpdateConfig,
) -> None:
    if not external_run_id:
        return
    repo = WorkflowRunRepository(session)
    now = datetime.now(UTC)
    await repo.update_by_external_id(
        external_run_id=external_run_id,
        status=config.status,
        result=config.result,
        error_message=config.error_message,
        started_at=now if config.started else None,
        completed_at=now if config.completed else None,
    )


async def graph_snapshot_task(
    project_id: str,
    graph_id: str,
    created_by: str | None = None,
    description: str | None = None,
    workflow_run_id: str | None = None,
) -> dict[str, Any]:
    """Graph snapshot task."""
    async with await _get_async_session() as session:
        await _update_workflow_run(session, workflow_run_id, WorkflowUpdateConfig("running", started=True))
        try:
            service = GraphSnapshotService(session)
            snapshot = await service.create_snapshot(
                project_id=project_id,
                graph_id=graph_id,
                created_by=created_by,
                description=description,
            )
            await session.commit()
            result = {
                "snapshot_id": snapshot.id,
                "version": snapshot.version,
                "hash": snapshot.snapshot_hash,
            }
            await _update_workflow_run(
                session,
                workflow_run_id,
                WorkflowUpdateConfig("completed", result=result, completed=True),
            )
        except Exception as exc:
            await _update_workflow_run(
                session,
                workflow_run_id,
                WorkflowUpdateConfig("failed", error_message=str(exc), completed=True),
            )
            raise
        else:
            return result


async def graph_validation_task(project_id: str, graph_id: str, workflow_run_id: str | None = None) -> dict[str, Any]:
    """Graph validation task."""
    async with await _get_async_session() as session:
        await _update_workflow_run(session, workflow_run_id, WorkflowUpdateConfig("running", started=True))
        try:
            service = GraphValidationService(session)
            result = await service.validate_graph(project_id=project_id, graph_id=graph_id)
            await _update_workflow_run(
                session,
                workflow_run_id,
                WorkflowUpdateConfig("completed", result=result, completed=True),
            )
        except Exception as exc:
            await _update_workflow_run(
                session,
                workflow_run_id,
                WorkflowUpdateConfig("failed", error_message=str(exc), completed=True),
            )
            raise
        else:
            return result


async def graph_export_task(project_id: str, workflow_run_id: str | None = None) -> dict[str, Any]:
    """Graph export task."""
    async with await _get_async_session() as session:
        await _update_workflow_run(session, workflow_run_id, WorkflowUpdateConfig(status="running", started=True))
        try:
            service = ExportService(session)
            export = await service.export_to_json(project_id)
            result = {"format": "graph_json", "content": export}
            await _update_workflow_run(
                session,
                workflow_run_id,
                WorkflowUpdateConfig(status="completed", result=result, completed=True),
            )
        except Exception as exc:
            await _update_workflow_run(
                session,
                workflow_run_id,
                WorkflowUpdateConfig(status="failed", error_message=str(exc), completed=True),
            )
            raise
        else:
            return result


async def graph_diff_task(
    project_id: str,
    graph_id: str,
    from_version: int,
    to_version: int,
    workflow_run_id: str | None = None,
) -> dict[str, Any]:
    """Graph diff task."""
    async with await _get_async_session() as session:
        await _update_workflow_run(session, workflow_run_id, WorkflowUpdateConfig(status="running", started=True))
        try:
            service = GraphSnapshotService(session)
            result = await service.diff_snapshots(
                project_id=project_id,
                graph_id=graph_id,
                from_version=from_version,
                to_version=to_version,
            )
            await _update_workflow_run(
                session,
                workflow_run_id,
                WorkflowUpdateConfig(status="completed", result=result, completed=True),
            )
        except Exception as exc:
            await _update_workflow_run(
                session,
                workflow_run_id,
                WorkflowUpdateConfig(status="failed", error_message=str(exc), completed=True),
            )
            raise
        else:
            return result


async def integration_sync_task(limit: int = 50, workflow_run_id: str | None = None) -> dict[str, Any]:
    """Integration sync task."""
    async with await _get_async_session() as session:
        await _update_workflow_run(session, workflow_run_id, WorkflowUpdateConfig(status="running", started=True))
        try:
            processor = IntegrationSyncProcessor(session)
            result = await processor.process_pending(limit=limit)
            await session.commit()
            await _update_workflow_run(
                session,
                workflow_run_id,
                WorkflowUpdateConfig(status="completed", result=result, completed=True),
            )
        except Exception as exc:
            await _update_workflow_run(
                session,
                workflow_run_id,
                WorkflowUpdateConfig(status="failed", error_message=str(exc), completed=True),
            )
            raise
        else:
            return result


async def integration_retry_task(limit: int = 50, workflow_run_id: str | None = None) -> dict[str, Any]:
    """Integration retry task."""
    async with await _get_async_session() as session:
        await _update_workflow_run(session, workflow_run_id, WorkflowUpdateConfig("running", started=True))
        try:
            processor = IntegrationSyncProcessor(session)
            result = await processor.process_retryable(limit=limit)
            await session.commit()
            await _update_workflow_run(
                session,
                workflow_run_id,
                WorkflowUpdateConfig("completed", result=result, completed=True),
            )
        except Exception as exc:
            await _update_workflow_run(
                session,
                workflow_run_id,
                WorkflowUpdateConfig("failed", error_message=str(exc), completed=True),
            )
            raise
        else:
            return result
