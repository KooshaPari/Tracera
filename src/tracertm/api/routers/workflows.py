"""FastAPI routes for workflow runs and schedules."""

from __future__ import annotations

import os
from typing import Annotated, Any, cast

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from tracertm.api.deps import auth_guard, get_db
from tracertm.models.graph import Graph
from tracertm.repositories.workflow_run_repository import WorkflowRunRepository
from tracertm.repositories.workflow_schedule_repository import WorkflowScheduleRepository

router = APIRouter(tags=["Workflows"])


def ensure_project_access(project_id: str, claims: dict[str, Any] | None) -> None:
    """Check if user has access to project."""
    from tracertm.api.security import ensure_project_access as _ensure_project_access

    _ensure_project_access(project_id, claims)


def ensure_write_permission(claims: dict[str, Any] | None, action: str) -> None:
    """Check if the current user can perform a write action."""
    from tracertm.api.security import ensure_write_permission as _ensure_write_permission

    _ensure_write_permission(claims, action)


@router.get("/projects/{project_id}/workflows/runs")
async def list_workflow_runs(
    project_id: str,
    status: str | None = None,
    workflow_name: str | None = None,
    limit: int = 100,
    offset: int = 0,
    claims: dict[str, Any] = Depends(auth_guard),
    db: AsyncSession = Depends(get_db),
):
    """List workflow runs for a project."""
    ensure_project_access(project_id, claims)

    repo = WorkflowRunRepository(db)
    runs_result = await repo.list_runs(
        project_id=project_id,
        status=status,
        workflow_name=workflow_name,
        limit=limit,
        offset=offset,
    )
    runs = cast("list[Any]", runs_result)
    return {
        "runs": [
            {
                "id": r.id,
                "project_id": r.project_id,
                "graph_id": r.graph_id,
                "workflow_name": r.workflow_name,
                "status": r.status,
                "external_run_id": r.external_run_id,
                "payload": r.payload,
                "result": r.result,
                "error_message": r.error_message,
                "created_by_user_id": r.created_by_user_id,
                "started_at": r.started_at.isoformat() if r.started_at else None,
                "completed_at": r.completed_at.isoformat() if r.completed_at else None,
                "created_at": r.created_at.isoformat() if r.created_at else None,
                "updated_at": r.updated_at.isoformat() if r.updated_at else None,
            }
            for r in runs
        ],
        "total": len(runs),
    }


@router.post("/projects/{project_id}/workflows/schedules/bootstrap")
async def bootstrap_workflow_schedules(
    project_id: str,
    claims: Annotated[dict[str, Any], Depends(auth_guard)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Create default Temporal schedules for graph snapshots and integration retries."""
    ensure_project_access(project_id, claims)

    service = TemporalService()
    repo = WorkflowScheduleRepository(db)

    created: list[dict[str, Any]] = []
    skipped: list[dict[str, Any]] = []
    errors: list[dict[str, Any]] = []

    graph_result = await db.execute(
        select(Graph.id).where(
            Graph.project_id == project_id,
            Graph.graph_type == "default",
        ),
    )
    graph_id = graph_result.scalar_one_or_none()
    if not graph_id:
        errors.append({"message": "Default graph not found for project"})
        return {"created": created, "skipped": skipped, "errors": errors}

    timezone = os.getenv("TEMPORAL_SCHEDULE_TIMEZONE", "UTC")
    snapshot_cron = os.getenv("TEMPORAL_SCHEDULE_GRAPH_SNAPSHOT_CRON", "0 2 * * *")
    retry_interval = int(os.getenv("TEMPORAL_SCHEDULE_INTEGRATION_RETRY_INTERVAL_SECONDS", "900"))
    retry_limit = int(os.getenv("TEMPORAL_SCHEDULE_INTEGRATION_RETRY_LIMIT", "50"))
    created_by_obj = claims.get("sub")
    created_by = cast("str", created_by_obj) if created_by_obj else "" if claims else None

    schedules: list[dict[str, Any]] = [
        {
            "schedule_id": f"project-{project_id}-graph-snapshot",
            "workflow_name": "GraphSnapshotWorkflow",
            "schedule_type": "cron",
            "cron_expressions": [snapshot_cron],
            "args": [project_id, graph_id, created_by, "Automated snapshot"],
            "description": "Automated graph snapshot",
        },
        {
            "schedule_id": f"project-{project_id}-integration-retry",
            "workflow_name": "IntegrationRetryWorkflow",
            "schedule_type": "interval",
            "interval_seconds": retry_interval,
            "args": [retry_limit],
            "description": "Automated integration retries",
        },
    ]

    for schedule in schedules:
        existing = await repo.get_by_schedule_id(cast("str", schedule["schedule_id"]))
        if existing:
            skipped.append({
                "schedule_id": schedule["schedule_id"],
                "reason": "already tracked",
            })
            continue
        try:
            await service.create_schedule(
                schedule_id=cast("str", schedule["schedule_id"]),
                workflow_name=cast("str", schedule["workflow_name"]),
                args=cast("list[Any]", schedule["args"]),
                cron_expressions=cast("list[str] | None", schedule.get("cron_expressions")),
                interval_seconds=cast("int | None", schedule.get("interval_seconds")),
                timezone=timezone,
            )
            await repo.create_schedule(
                schedule_id=cast("str", schedule["schedule_id"]),
                workflow_name=cast("str", schedule["workflow_name"]),
                schedule_type=cast("str", schedule["schedule_type"]),
                schedule_spec={
                    "cron_expressions": schedule.get("cron_expressions"),
                    "interval_seconds": schedule.get("interval_seconds"),
                    "timezone": timezone,
                },
                project_id=project_id,
                task_queue=service.settings.task_queue if service.settings else None,
                created_by_user_id=created_by,
                description=cast("str | None", schedule.get("description")),
            )
            created.append({
                "schedule_id": schedule["schedule_id"],
                "workflow_name": schedule["workflow_name"],
            })
        except (AttributeError, KeyError, OSError, RuntimeError, TypeError, ValueError) as exc:
            errors.append({
                "schedule_id": schedule["schedule_id"],
                "message": str(exc),
            })

    if created:
        await db.commit()
    return {"created": created, "skipped": skipped, "errors": errors}


@router.get("/projects/{project_id}/workflows/schedules")
async def list_workflow_schedules(
    project_id: str,
    claims: Annotated[dict[str, Any], Depends(auth_guard)],
    limit: int = 100,
    offset: int = 0,
    db: AsyncSession = Depends(get_db),
):
    """List Temporal schedules scoped to a project."""
    ensure_project_access(project_id, claims)

    repo = WorkflowScheduleRepository(db)
    schedules = await repo.list_schedules(project_id=project_id, limit=limit, offset=offset)
    return {
        "schedules": [
            {
                "id": s.id,
                "project_id": s.project_id,
                "schedule_id": s.schedule_id,
                "workflow_name": s.workflow_name,
                "schedule_type": s.schedule_type,
                "schedule_spec": s.schedule_spec,
                "task_queue": s.task_queue,
                "status": s.status,
                "created_by_user_id": s.created_by_user_id,
                "last_run_at": s.last_run_at.isoformat() if s.last_run_at else None,
                "description": s.description,
                "created_at": s.created_at.isoformat() if s.created_at else None,
                "updated_at": s.updated_at.isoformat() if s.updated_at else None,
            }
            for s in schedules
        ],
        "total": len(schedules),
    }


@router.delete("/projects/{project_id}/workflows/schedules/{cron_id}")
async def delete_workflow_schedule(
    project_id: str,
    cron_id: str,
    claims: Annotated[dict[str, Any], Depends(auth_guard)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Delete a Temporal schedule."""
    ensure_project_access(project_id, claims)

    repo = WorkflowScheduleRepository(db)
    schedule = await repo.get_by_schedule_id(cron_id)
    if schedule and schedule.project_id != project_id:
        raise HTTPException(status_code=403, detail="Schedule does not belong to this project")
    if schedule is None:
        raise HTTPException(status_code=404, detail="Schedule not found")

    service = TemporalService()
    try:
        await service.delete_schedule(cron_id)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    deleted = await repo.delete_by_schedule_id(cron_id)
    await db.commit()
    return {"deleted": deleted > 0, "schedule_id": cron_id}


from tracertm.api.routers import workflows_triggers as _workflows_triggers  # noqa: F401
