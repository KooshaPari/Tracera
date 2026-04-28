"""Global execution API endpoints for TraceRTM."""

from __future__ import annotations

from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession

from tracertm.api.config.rate_limiting import enforce_rate_limit
from tracertm.api.deps import auth_guard, get_db
from tracertm.repositories.process_repository import ProcessRepository
from tracertm.schemas.process import ProcessExecutionComplete

router = APIRouter(prefix="/api/v1", tags=["executions"])


def ensure_write_permission(claims: dict[str, Any] | None, action: str) -> None:
    """Check if user has write permission."""
    from tracertm.api.security import ensure_write_permission as _ensure_write_permission

    _ensure_write_permission(claims, action=action)


def _serialize_execution(execution: object) -> dict[str, object]:
    created_at = getattr(execution, "created_at", None)
    updated_at = getattr(execution, "updated_at", None)
    started_at = getattr(execution, "started_at", None)
    completed_at = getattr(execution, "completed_at", None)
    return {
        "id": str(getattr(execution, "id", "")),
        "process_id": str(getattr(execution, "process_id", "")),
        "execution_number": getattr(execution, "execution_number", ""),
        "status": getattr(execution, "status", ""),
        "current_stage_id": getattr(execution, "current_stage_id", None),
        "completed_stages": getattr(execution, "completed_stages", None),
        "started_at": started_at.isoformat() if started_at else None,
        "completed_at": completed_at.isoformat() if completed_at else None,
        "initiated_by": getattr(execution, "initiated_by", None),
        "completed_by": getattr(execution, "completed_by", None),
        "trigger_item_id": getattr(execution, "trigger_item_id", None),
        "context_data": getattr(execution, "context_data", {}),
        "result_summary": getattr(execution, "result_summary", None),
        "output_item_ids": getattr(execution, "output_item_ids", None),
        "created_at": created_at.isoformat() if created_at else None,
        "updated_at": updated_at.isoformat() if updated_at else None,
    }


@router.get("/executions/{execution_id}")
async def get_execution_by_id(
    request: Request,
    execution_id: str,
    claims: Annotated[dict[str, Any], Depends(auth_guard)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Get a specific process execution."""
    enforce_rate_limit(request, claims)

    repo = ProcessRepository(db)
    execution = await repo.get_execution_by_id(execution_id)

    if not execution:
        raise HTTPException(status_code=404, detail="Execution not found")

    return _serialize_execution(execution)


@router.post("/executions/{execution_id}/start")
async def start_execution(
    request: Request,
    execution_id: str,
    claims: Annotated[dict[str, Any], Depends(auth_guard)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Start a pending execution."""
    enforce_rate_limit(request, claims)
    ensure_write_permission(claims, "update")

    repo = ProcessRepository(db)
    try:
        execution = await repo.start_execution(execution_id)
        await db.commit()
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

    return {"id": str(execution.id), "status": execution.status}


@router.post("/executions/{execution_id}/advance")
async def advance_execution(
    request: Request,
    execution_id: str,
    stage_id: str,
    claims: Annotated[dict[str, Any], Depends(auth_guard)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Advance execution to next stage."""
    enforce_rate_limit(request, claims)
    ensure_write_permission(claims, "update")

    repo = ProcessRepository(db)
    try:
        execution = await repo.advance_execution(execution_id, stage_id)
        await db.commit()
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

    return {
        "id": str(execution.id),
        "current_stage_id": execution.current_stage_id,
        "completed_stages": execution.completed_stages,
    }


@router.post("/executions/{execution_id}/complete")
async def complete_execution(
    request: Request,
    execution_id: str,
    completion_data: ProcessExecutionComplete,
    claims: Annotated[dict[str, Any], Depends(auth_guard)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Complete a process execution."""
    enforce_rate_limit(request, claims)
    ensure_write_permission(claims, "update")

    repo = ProcessRepository(db)
    try:
        execution = await repo.complete_execution(
            execution_id=execution_id,
            completed_by=completion_data.completed_by or claims.get("sub", "system"),
            result_summary=completion_data.result_summary,
            output_item_ids=completion_data.output_item_ids,
        )
        await db.commit()
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

    return {"id": str(execution.id), "status": execution.status}
