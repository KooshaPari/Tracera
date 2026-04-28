"""Problem management API endpoints for TraceRTM."""

from __future__ import annotations

from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession

from tracertm.api.config.rate_limiting import enforce_rate_limit
from tracertm.api.deps import auth_guard, get_db
from tracertm.repositories.problem_repository import ProblemRepository
from tracertm.schemas.problem import (
    PermanentFixUpdate,
    ProblemClosure,
    ProblemCreate,
    ProblemStatusTransition,
    ProblemUpdate,
    RCARequest,
    WorkaroundUpdate,
)

router = APIRouter(prefix="/api/v1", tags=["problems"])


def ensure_project_access(project_id: str, claims: dict[str, Any] | None) -> None:
    """Check if user has access to project."""
    from tracertm.api.security import ensure_project_access as _ensure_project_access

    _ensure_project_access(project_id, claims)


def ensure_write_permission(claims: dict[str, Any] | None, action: str) -> None:
    """Check if user has write permission."""
    from tracertm.api.security import ensure_write_permission as _ensure_write_permission

    _ensure_write_permission(claims, action=action)


def _serialize_problem_list_item(problem: object) -> dict[str, Any]:
    created_at = getattr(problem, "created_at", None)
    updated_at = getattr(problem, "updated_at", None)
    return {
        "id": str(getattr(problem, "id", "")),
        "problem_number": getattr(problem, "problem_number", ""),
        "project_id": str(getattr(problem, "project_id", "") or ""),
        "title": getattr(problem, "title", ""),
        "status": getattr(problem, "status", ""),
        "priority": getattr(problem, "priority", ""),
        "impact_level": getattr(problem, "impact_level", ""),
        "category": getattr(problem, "category", None),
        "assigned_to": getattr(problem, "assigned_to", None),
        "assigned_team": getattr(problem, "assigned_team", None),
        "root_cause_identified": getattr(problem, "root_cause_identified", False),
        "workaround_available": getattr(problem, "workaround_available", False),
        "created_at": created_at.isoformat() if created_at else None,
        "updated_at": updated_at.isoformat() if updated_at else None,
    }


def _serialize_problem_detail(problem: object) -> dict[str, Any]:
    created_at = getattr(problem, "created_at", None)
    updated_at = getattr(problem, "updated_at", None)
    rca_completed_at = getattr(problem, "rca_completed_at", None)
    permanent_fix_implemented_at = getattr(problem, "permanent_fix_implemented_at", None)
    closed_at = getattr(problem, "closed_at", None)
    target_resolution_date = getattr(problem, "target_resolution_date", None)
    return {
        "id": str(getattr(problem, "id", "")),
        "problem_number": getattr(problem, "problem_number", ""),
        "project_id": str(getattr(problem, "project_id", "") or ""),
        "title": getattr(problem, "title", ""),
        "description": getattr(problem, "description", None),
        "status": getattr(problem, "status", ""),
        "resolution_type": getattr(problem, "resolution_type", None),
        "category": getattr(problem, "category", None),
        "sub_category": getattr(problem, "sub_category", None),
        "tags": getattr(problem, "tags", None),
        "impact_level": getattr(problem, "impact_level", ""),
        "urgency": getattr(problem, "urgency", ""),
        "priority": getattr(problem, "priority", ""),
        "affected_systems": getattr(problem, "affected_systems", None),
        "affected_users_estimated": getattr(problem, "affected_users_estimated", None),
        "business_impact_description": getattr(problem, "business_impact_description", None),
        "rca_performed": getattr(problem, "rca_performed", False),
        "rca_method": getattr(problem, "rca_method", None),
        "rca_notes": getattr(problem, "rca_notes", None),
        "rca_data": getattr(problem, "rca_data", None),
        "root_cause_identified": getattr(problem, "root_cause_identified", False),
        "root_cause_description": getattr(problem, "root_cause_description", None),
        "root_cause_category": getattr(problem, "root_cause_category", None),
        "root_cause_confidence": getattr(problem, "root_cause_confidence", None),
        "rca_completed_at": rca_completed_at.isoformat() if rca_completed_at else None,
        "rca_completed_by": getattr(problem, "rca_completed_by", None),
        "workaround_available": getattr(problem, "workaround_available", False),
        "workaround_description": getattr(problem, "workaround_description", None),
        "workaround_effectiveness": getattr(problem, "workaround_effectiveness", None),
        "permanent_fix_available": getattr(problem, "permanent_fix_available", False),
        "permanent_fix_description": getattr(problem, "permanent_fix_description", None),
        "permanent_fix_implemented_at": (
            permanent_fix_implemented_at.isoformat() if permanent_fix_implemented_at else None
        ),
        "permanent_fix_change_id": getattr(problem, "permanent_fix_change_id", None),
        "known_error_id": getattr(problem, "known_error_id", None),
        "knowledge_article_id": getattr(problem, "knowledge_article_id", None),
        "assigned_to": getattr(problem, "assigned_to", None),
        "assigned_team": getattr(problem, "assigned_team", None),
        "owner": getattr(problem, "owner", None),
        "closed_by": getattr(problem, "closed_by", None),
        "closed_at": closed_at.isoformat() if closed_at else None,
        "closure_notes": getattr(problem, "closure_notes", None),
        "target_resolution_date": (
            target_resolution_date.isoformat() if target_resolution_date else None
        ),
        "metadata": getattr(problem, "problem_metadata", {}),
        "version": getattr(problem, "version", 0),
        "created_at": created_at.isoformat() if created_at else None,
        "updated_at": updated_at.isoformat() if updated_at else None,
    }


def _serialize_problem_activity(activity: object) -> dict[str, Any]:
    created_at = getattr(activity, "created_at", None)
    return {
        "id": str(getattr(activity, "id", "")),
        "problem_id": str(getattr(activity, "problem_id", "")),
        "activity_type": getattr(activity, "activity_type", None),
        "from_value": getattr(activity, "from_value", None),
        "to_value": getattr(activity, "to_value", None),
        "description": getattr(activity, "description", None),
        "performed_by": getattr(activity, "performed_by", None),
        "metadata": getattr(activity, "activity_metadata", None),
        "created_at": created_at.isoformat() if created_at else None,
    }


@router.get("/problems")
async def list_problems(
    request: Request,
    project_id: str,
    status: str | None = None,
    priority: str | None = None,
    impact_level: str | None = None,
    category: str | None = None,
    assigned_to: str | None = None,
    skip: int = 0,
    limit: int = 100,
    claims: dict[str, Any] = Depends(auth_guard),
    db: AsyncSession = Depends(get_db),
):
    """List problems in a project with optional filters."""
    if not (request and request.headers.get("X-Bulk-Operation") == "true"):
        enforce_rate_limit(request, claims)
    ensure_project_access(project_id, claims)

    repo = ProblemRepository(db)
    problems = await repo.list_all(
        project_id=project_id,
        status=status,
        priority=priority,
        impact_level=impact_level,
        category=category,
        assigned_to=assigned_to,
        limit=limit,
        offset=skip,
    )

    return {
        "total": len(problems),
        "problems": [_serialize_problem_list_item(problem) for problem in problems],
    }


@router.get("/problems/{problem_id}")
async def get_problem(
    request: Request,
    problem_id: str,
    claims: Annotated[dict[str, Any], Depends(auth_guard)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Get a specific problem by ID."""
    enforce_rate_limit(request, claims)

    repo = ProblemRepository(db)
    problem = await repo.get_by_id(problem_id)

    if not problem:
        raise HTTPException(status_code=404, detail="Problem not found")

    return _serialize_problem_detail(problem)


@router.post("/problems")
async def create_problem(
    request: Request,
    project_id: str,
    problem_data: ProblemCreate,
    claims: Annotated[dict[str, Any], Depends(auth_guard)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Create a new problem."""
    enforce_rate_limit(request, claims)
    ensure_project_access(project_id, claims)
    ensure_write_permission(claims, "create")

    repo = ProblemRepository(db)
    problem = await repo.create(
        project_id=project_id,
        title=problem_data.title,
        description=problem_data.description,
        category=problem_data.category,
        sub_category=problem_data.sub_category,
        tags=problem_data.tags,
        impact_level=problem_data.impact_level.value,
        urgency=problem_data.urgency.value,
        priority=problem_data.priority.value,
        affected_systems=problem_data.affected_systems,
        affected_users_estimated=problem_data.affected_users_estimated,
        business_impact_description=problem_data.business_impact_description,
        assigned_to=problem_data.assigned_to,
        assigned_team=problem_data.assigned_team,
        owner=problem_data.owner,
        target_resolution_date=problem_data.target_resolution_date,
        metadata=problem_data.metadata,
        created_by=claims.get("sub", "system"),
    )
    await db.commit()

    return {"id": str(problem.id), "problem_number": problem.problem_number}


@router.put("/problems/{problem_id}")
async def update_problem(
    request: Request,
    problem_id: str,
    problem_data: ProblemUpdate,
    claims: Annotated[dict[str, Any], Depends(auth_guard)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Update a problem."""
    enforce_rate_limit(request, claims)
    ensure_write_permission(claims, "update")

    repo = ProblemRepository(db)
    problem = await repo.get_by_id(problem_id)
    if not problem:
        raise HTTPException(status_code=404, detail="Problem not found")

    updates = problem_data.model_dump(exclude_unset=True)
    for key in ["impact_level", "urgency", "priority"]:
        if key in updates and updates[key] is not None:
            updates[key] = updates[key].value

    if "metadata" in updates:
        updates["problem_metadata"] = updates.pop("metadata")

    problem = await repo.update(
        problem_id=problem_id,
        expected_version=problem.version,
        performed_by=claims.get("sub", "system"),
        **updates,
    )
    await db.commit()

    return {"id": str(problem.id), "version": problem.version}


@router.post("/problems/{problem_id}/status")
async def transition_problem_status(
    request: Request,
    problem_id: str,
    transition: ProblemStatusTransition,
    claims: Annotated[dict[str, Any], Depends(auth_guard)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Transition problem to a new status."""
    enforce_rate_limit(request, claims)
    ensure_write_permission(claims, "update")

    repo = ProblemRepository(db)
    try:
        problem = await repo.transition_status(
            problem_id=problem_id,
            to_status=transition.to_status.value,
            reason=transition.reason,
            performed_by=transition.performed_by or claims.get("sub", "system"),
        )
        await db.commit()
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    return {"id": str(problem.id), "status": problem.status, "version": problem.version}


@router.post("/problems/{problem_id}/rca")
async def record_problem_rca(
    request: Request,
    problem_id: str,
    rca_data: RCARequest,
    claims: Annotated[dict[str, Any], Depends(auth_guard)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Record Root Cause Analysis for a problem."""
    enforce_rate_limit(request, claims)
    ensure_write_permission(claims, "update")

    repo = ProblemRepository(db)
    problem = await repo.record_rca(
        problem_id=problem_id,
        rca_method=rca_data.rca_method.value,
        rca_notes=rca_data.rca_notes,
        rca_data=rca_data.rca_data,
        root_cause_identified=rca_data.root_cause_identified,
        root_cause_description=rca_data.root_cause_description,
        root_cause_category=(
            rca_data.root_cause_category.value if rca_data.root_cause_category else None
        ),
        root_cause_confidence=rca_data.root_cause_confidence,
        performed_by=rca_data.performed_by or claims.get("sub", "system"),
    )
    await db.commit()

    return {
        "id": str(problem.id),
        "rca_performed": problem.rca_performed,
        "root_cause_identified": problem.root_cause_identified,
    }


@router.put("/problems/{problem_id}/workaround")
async def update_problem_workaround(
    request: Request,
    problem_id: str,
    workaround_data: WorkaroundUpdate,
    claims: Annotated[dict[str, Any], Depends(auth_guard)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Update workaround information for a problem."""
    enforce_rate_limit(request, claims)
    ensure_write_permission(claims, "update")

    repo = ProblemRepository(db)
    problem = await repo.update_workaround(
        problem_id=problem_id,
        workaround_available=workaround_data.workaround_available,
        workaround_description=workaround_data.workaround_description,
        workaround_effectiveness=workaround_data.workaround_effectiveness,
        performed_by=claims.get("sub", "system"),
    )
    await db.commit()

    return {"id": str(problem.id), "workaround_available": problem.workaround_available}


@router.put("/problems/{problem_id}/permanent-fix")
async def update_problem_permanent_fix(
    request: Request,
    problem_id: str,
    fix_data: PermanentFixUpdate,
    claims: Annotated[dict[str, Any], Depends(auth_guard)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Update permanent fix information for a problem."""
    enforce_rate_limit(request, claims)
    ensure_write_permission(claims, "update")

    repo = ProblemRepository(db)
    problem = await repo.update_permanent_fix(
        problem_id=problem_id,
        permanent_fix_available=fix_data.permanent_fix_available,
        permanent_fix_description=fix_data.permanent_fix_description,
        permanent_fix_change_id=fix_data.permanent_fix_change_id,
        performed_by=claims.get("sub", "system"),
    )
    await db.commit()

    return {"id": str(problem.id), "permanent_fix_available": problem.permanent_fix_available}


@router.post("/problems/{problem_id}/close")
async def close_problem(
    request: Request,
    problem_id: str,
    closure_data: ProblemClosure,
    claims: Annotated[dict[str, Any], Depends(auth_guard)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Close a problem."""
    enforce_rate_limit(request, claims)
    ensure_write_permission(claims, "update")

    repo = ProblemRepository(db)
    problem = await repo.close(
        problem_id=problem_id,
        resolution_type=closure_data.resolution_type.value,
        closure_notes=closure_data.closure_notes,
        closed_by=closure_data.closed_by or claims.get("sub", "system"),
    )
    await db.commit()

    return {"id": str(problem.id), "status": problem.status, "resolution_type": problem.resolution_type}


@router.get("/problems/{problem_id}/activities")
async def get_problem_activities(
    request: Request,
    problem_id: str,
    limit: int = 50,
    claims: dict[str, Any] = Depends(auth_guard),
    db: AsyncSession = Depends(get_db),
):
    """Get activity log for a problem."""
    enforce_rate_limit(request, claims)

    repo = ProblemRepository(db)
    activities = await repo.get_activities(problem_id, limit=limit)

    return {
        "problem_id": problem_id,
        "activities": [_serialize_problem_activity(activity) for activity in activities],
    }


@router.delete("/problems/{problem_id}")
async def delete_problem(
    request: Request,
    problem_id: str,
    claims: Annotated[dict[str, Any], Depends(auth_guard)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Delete a problem (soft delete)."""
    enforce_rate_limit(request, claims)
    ensure_write_permission(claims, "delete")

    repo = ProblemRepository(db)
    success = await repo.delete(problem_id, soft=True)
    await db.commit()

    if not success:
        raise HTTPException(status_code=404, detail="Problem not found")

    return {"deleted": True, "id": problem_id}


@router.get("/projects/{project_id}/problems/stats")
async def get_problem_stats(
    request: Request,
    project_id: str,
    claims: Annotated[dict[str, Any], Depends(auth_guard)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Get problem statistics for a project."""
    enforce_rate_limit(request, claims)
    ensure_project_access(project_id, claims)

    repo = ProblemRepository(db)
    by_status = await repo.count_by_status(project_id)
    by_priority = await repo.count_by_priority(project_id)

    return {
        "project_id": project_id,
        "by_status": by_status,
        "by_priority": by_priority,
        "total": sum(by_status.values()),
    }
