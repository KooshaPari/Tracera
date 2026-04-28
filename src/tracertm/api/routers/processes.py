"""Process management API endpoints for TraceRTM."""

from __future__ import annotations

from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession

from tracertm.api.config.rate_limiting import enforce_rate_limit
from tracertm.api.deps import auth_guard, get_db
from tracertm.repositories.process_repository import ProcessRepository
from tracertm.schemas.process import (
    ProcessActivation,
    ProcessCreate,
    ProcessDeprecation,
    ProcessExecutionComplete,
    ProcessExecutionCreate,
    ProcessUpdate,
    ProcessVersionCreate,
)

router = APIRouter(prefix="/api/v1", tags=["processes"])


def ensure_project_access(project_id: str, claims: dict[str, Any] | None) -> None:
    """Check if user has access to project."""
    from tracertm.api.security import ensure_project_access as _ensure_project_access

    _ensure_project_access(project_id, claims)


def ensure_write_permission(claims: dict[str, Any] | None, action: str) -> None:
    """Check if user has write permission."""
    from tracertm.api.security import ensure_write_permission as _ensure_write_permission

    _ensure_write_permission(claims, action=action)


def _serialize_process_list_item(process: object) -> dict[str, object]:
    created_at = getattr(process, "created_at", None)
    updated_at = getattr(process, "updated_at", None)
    return {
        "id": str(getattr(process, "id", "")),
        "process_number": getattr(process, "process_number", ""),
        "project_id": str(getattr(process, "project_id", "") or ""),
        "name": getattr(process, "name", ""),
        "status": getattr(process, "status", ""),
        "category": getattr(process, "category", None),
        "owner": getattr(process, "owner", None),
        "version_number": getattr(process, "version_number", 0),
        "is_active_version": getattr(process, "is_active_version", False),
        "created_at": created_at.isoformat() if created_at else None,
        "updated_at": updated_at.isoformat() if updated_at else None,
    }


def _serialize_process_detail(process: object) -> dict[str, object]:
    created_at = getattr(process, "created_at", None)
    updated_at = getattr(process, "updated_at", None)
    activated_at = getattr(process, "activated_at", None)
    deprecated_at = getattr(process, "deprecated_at", None)
    return {
        "id": str(getattr(process, "id", "")),
        "process_number": getattr(process, "process_number", ""),
        "project_id": str(getattr(process, "project_id", "") or ""),
        "name": getattr(process, "name", ""),
        "description": getattr(process, "description", None),
        "purpose": getattr(process, "purpose", None),
        "status": getattr(process, "status", ""),
        "category": getattr(process, "category", None),
        "tags": getattr(process, "tags", None),
        "version_number": getattr(process, "version_number", 0),
        "is_active_version": getattr(process, "is_active_version", False),
        "parent_version_id": getattr(process, "parent_version_id", None),
        "version_notes": getattr(process, "version_notes", None),
        "stages": getattr(process, "stages", None),
        "swimlanes": getattr(process, "swimlanes", None),
        "inputs": getattr(process, "inputs", None),
        "outputs": getattr(process, "outputs", None),
        "triggers": getattr(process, "triggers", None),
        "exit_criteria": getattr(process, "exit_criteria", None),
        "bpmn_xml": getattr(process, "bpmn_xml", None),
        "bpmn_diagram_url": getattr(process, "bpmn_diagram_url", None),
        "owner": getattr(process, "owner", None),
        "responsible_team": getattr(process, "responsible_team", None),
        "expected_duration_hours": getattr(process, "expected_duration_hours", None),
        "sla_hours": getattr(process, "sla_hours", None),
        "activated_at": activated_at.isoformat() if activated_at else None,
        "activated_by": getattr(process, "activated_by", None),
        "deprecated_at": deprecated_at.isoformat() if deprecated_at else None,
        "deprecated_by": getattr(process, "deprecated_by", None),
        "deprecation_reason": getattr(process, "deprecation_reason", None),
        "related_process_ids": getattr(process, "related_process_ids", None),
        "metadata": getattr(process, "process_metadata", {}),
        "version": getattr(process, "version", 0),
        "created_at": created_at.isoformat() if created_at else None,
        "updated_at": updated_at.isoformat() if updated_at else None,
    }


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


@router.get("/processes")
async def list_processes(
    request: Request,
    project_id: str,
    status: str | None = None,
    category: str | None = None,
    owner: str | None = None,
    active_only: bool = False,
    skip: int = 0,
    limit: int = 100,
    claims: dict[str, Any] = Depends(auth_guard),
    db: AsyncSession = Depends(get_db),
):
    """List processes in a project with optional filters."""
    if not (request and request.headers.get("X-Bulk-Operation") == "true"):
        enforce_rate_limit(request, claims)
    ensure_project_access(project_id, claims)

    repo = ProcessRepository(db)
    processes = await repo.list_all(
        project_id=project_id,
        status=status,
        category=category,
        owner=owner,
        active_only=active_only,
        limit=limit,
        offset=skip,
    )

    return {
        "total": len(processes),
        "processes": [_serialize_process_list_item(process) for process in processes],
    }


@router.get("/processes/{process_id}")
async def get_process(
    request: Request,
    process_id: str,
    claims: Annotated[dict[str, Any], Depends(auth_guard)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Get a specific process by ID."""
    enforce_rate_limit(request, claims)

    repo = ProcessRepository(db)
    process = await repo.get_by_id(process_id)

    if not process:
        raise HTTPException(status_code=404, detail="Process not found")

    return _serialize_process_detail(process)


@router.post("/processes")
async def create_process(
    request: Request,
    project_id: str,
    process_data: ProcessCreate,
    claims: Annotated[dict[str, Any], Depends(auth_guard)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Create a new process."""
    enforce_rate_limit(request, claims)
    ensure_project_access(project_id, claims)
    ensure_write_permission(claims, "create")

    repo = ProcessRepository(db)

    stages = [s.model_dump() for s in process_data.stages] if process_data.stages else None
    swimlanes = [s.model_dump() for s in process_data.swimlanes] if process_data.swimlanes else None
    inputs = [i.model_dump() for i in process_data.inputs] if process_data.inputs else None
    outputs = [o.model_dump() for o in process_data.outputs] if process_data.outputs else None
    triggers = [t.model_dump() for t in process_data.triggers] if process_data.triggers else None

    process = await repo.create(
        project_id=project_id,
        name=process_data.name,
        description=process_data.description,
        purpose=process_data.purpose,
        category=process_data.category.value if process_data.category else None,
        tags=process_data.tags,
        stages=stages,
        swimlanes=swimlanes,
        inputs=inputs,
        outputs=outputs,
        triggers=triggers,
        exit_criteria=process_data.exit_criteria,
        bpmn_xml=process_data.bpmn_xml,
        owner=process_data.owner,
        responsible_team=process_data.responsible_team,
        expected_duration_hours=process_data.expected_duration_hours,
        sla_hours=process_data.sla_hours,
        related_process_ids=process_data.related_process_ids,
        metadata=process_data.metadata,
        _created_by=str(claims.get("sub", "system")),
    )
    await db.commit()

    return {"id": str(process.id), "process_number": process.process_number}


@router.put("/processes/{process_id}")
async def update_process(
    request: Request,
    process_id: str,
    process_data: ProcessUpdate,
    claims: Annotated[dict[str, Any], Depends(auth_guard)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Update a process."""
    enforce_rate_limit(request, claims)
    ensure_write_permission(claims, "update")

    repo = ProcessRepository(db)
    process = await repo.get_by_id(process_id)
    if not process:
        raise HTTPException(status_code=404, detail="Process not found")

    updates = process_data.model_dump(exclude_unset=True)

    if "category" in updates and updates["category"] is not None:
        updates["category"] = updates["category"].value

    for key in ["stages", "swimlanes", "inputs", "outputs", "triggers"]:
        if key in updates and updates[key] is not None:
            updates[key] = [
                item.model_dump() if hasattr(item, "model_dump") else item
                for item in updates[key]
            ]

    if "metadata" in updates:
        updates["process_metadata"] = updates.pop("metadata")

    process = await repo.update(
        process_id=process_id,
        expected_version=process.version,
        **updates,
    )
    await db.commit()

    return {"id": str(process.id), "version": process.version}


@router.post("/processes/{process_id}/versions")
async def create_process_version(
    request: Request,
    process_id: str,
    version_data: ProcessVersionCreate,
    claims: Annotated[dict[str, Any], Depends(auth_guard)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Create a new version of a process."""
    enforce_rate_limit(request, claims)
    ensure_write_permission(claims, "create")

    repo = ProcessRepository(db)
    try:
        new_process = await repo.create_version(
            process_id=process_id,
            version_notes=version_data.version_notes,
            _created_by=str(claims.get("sub", "system")),
        )
        await db.commit()
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

    return {
        "id": str(new_process.id),
        "process_number": new_process.process_number,
        "version_number": new_process.version_number,
        "parent_version_id": new_process.parent_version_id,
    }


@router.put("/processes/{process_id}/activate")
async def activate_process(
    request: Request,
    process_id: str,
    activation_data: ProcessActivation,
    claims: Annotated[dict[str, Any], Depends(auth_guard)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Activate a process version."""
    enforce_rate_limit(request, claims)
    ensure_write_permission(claims, "update")

    repo = ProcessRepository(db)
    try:
        process = await repo.activate_version(
            process_id=process_id,
            activated_by=activation_data.activated_by or claims.get("sub", "system"),
        )
        await db.commit()
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

    return {
        "id": str(process.id),
        "status": process.status,
        "is_active_version": process.is_active_version,
    }


@router.put("/processes/{process_id}/deprecate")
async def deprecate_process(
    request: Request,
    process_id: str,
    deprecation_data: ProcessDeprecation,
    claims: Annotated[dict[str, Any], Depends(auth_guard)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Deprecate a process."""
    enforce_rate_limit(request, claims)
    ensure_write_permission(claims, "update")

    repo = ProcessRepository(db)
    try:
        process = await repo.deprecate(
            process_id=process_id,
            deprecation_reason=deprecation_data.deprecation_reason,
            deprecated_by=deprecation_data.deprecated_by or claims.get("sub", "system"),
        )
        await db.commit()
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

    return {"id": str(process.id), "status": process.status}


@router.delete("/processes/{process_id}")
async def delete_process(
    request: Request,
    process_id: str,
    claims: Annotated[dict[str, Any], Depends(auth_guard)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Delete a process (soft delete)."""
    enforce_rate_limit(request, claims)
    ensure_write_permission(claims, "delete")

    repo = ProcessRepository(db)
    success = await repo.delete(process_id, soft=True)
    await db.commit()

    if not success:
        raise HTTPException(status_code=404, detail="Process not found")

    return {"deleted": True, "id": process_id}


@router.get("/projects/{project_id}/processes/stats")
async def get_process_stats(
    request: Request,
    project_id: str,
    claims: Annotated[dict[str, Any], Depends(auth_guard)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Get process statistics for a project."""
    enforce_rate_limit(request, claims)
    ensure_project_access(project_id, claims)

    repo = ProcessRepository(db)
    by_status = await repo.count_by_status(project_id)
    by_category = await repo.count_by_category(project_id)

    return {
        "project_id": project_id,
        "by_status": by_status,
        "by_category": by_category,
        "total": sum(by_status.values()),
    }


@router.post("/processes/{process_id}/executions")
async def create_process_execution(
    request: Request,
    process_id: str,
    execution_data: ProcessExecutionCreate,
    claims: Annotated[dict[str, Any], Depends(auth_guard)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Start a new execution of a process."""
    enforce_rate_limit(request, claims)
    ensure_write_permission(claims, "create")

    repo = ProcessRepository(db)
    try:
        execution = await repo.create_execution(
            process_id=process_id,
            initiated_by=claims.get("sub", "system"),
            trigger_item_id=execution_data.trigger_item_id,
            context_data=execution_data.context_data,
        )
        await db.commit()
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

    return {"id": str(execution.id), "execution_number": execution.execution_number}


@router.get("/processes/{process_id}/executions")
async def list_process_executions(
    request: Request,
    process_id: str,
    status: str | None = None,
    skip: int = 0,
    limit: int = 50,
    claims: dict[str, Any] = Depends(auth_guard),
    db: AsyncSession = Depends(get_db),
):
    """List executions for a process."""
    enforce_rate_limit(request, claims)

    repo = ProcessRepository(db)
    executions = await repo.list_executions(
        process_id=process_id,
        status=status,
        limit=limit,
        offset=skip,
    )

    return {
        "total": len(executions),
        "executions": [_serialize_execution(execution) for execution in executions],
    }
