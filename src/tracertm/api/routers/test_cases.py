"""Test case management API routes for TraceRTM."""

from __future__ import annotations

from typing import TYPE_CHECKING, Annotated, Any

from fastapi import APIRouter, Depends, HTTPException, Request

from tracertm.api.config.rate_limiting import enforce_rate_limit
from tracertm.api.deps import auth_guard, get_db
from tracertm.repositories.test_case_repository import TestCaseRepository
from tracertm.schemas.test_case import (
    TestCaseCreate,
    TestCaseDeprecation,
    TestCaseReview,
    TestCaseStatusTransition,
    TestCaseUpdate,
)

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(tags=["Test Cases"])


def ensure_project_access(project_id: str, claims: dict[str, Any] | None) -> None:
    """Check if user has access to a project."""
    from tracertm.api.security import ensure_project_access as _ensure_project_access

    _ensure_project_access(project_id, claims)


def ensure_write_permission(claims: dict[str, Any] | None, action: str) -> None:
    """Check if user has write permission."""
    from tracertm.api.security import ensure_write_permission as _ensure_write_permission

    _ensure_write_permission(claims, action=action)


@router.get("/api/v1/test-cases")
async def list_test_cases(
    request: Request,
    project_id: str,
    status: str | None = None,
    test_type: str | None = None,
    priority: str | None = None,
    automation_status: str | None = None,
    category: str | None = None,
    assigned_to: str | None = None,
    search: str | None = None,
    skip: int = 0,
    limit: int = 100,
    claims: dict[str, Any] = Depends(auth_guard),
    db: AsyncSession = Depends(get_db),
):
    """List test cases in a project with optional filters."""
    if not (request and request.headers.get("X-Bulk-Operation") == "true"):
        enforce_rate_limit(request, claims)
    ensure_project_access(project_id, claims)

    repo = TestCaseRepository(db)
    test_cases = await repo.list_all(
        project_id=project_id,
        status=status,
        test_type=test_type,
        priority=priority,
        automation_status=automation_status,
        category=category,
        assigned_to=assigned_to,
        search=search,
        limit=limit,
        offset=skip,
    )

    return {
        "total": len(test_cases),
        "test_cases": [
            {
                "id": str(tc.id),
                "test_case_number": tc.test_case_number,
                "project_id": str(tc.project_id),
                "title": tc.title,
                "status": tc.status,
                "test_type": tc.test_type,
                "priority": tc.priority,
                "category": tc.category,
                "automation_status": tc.automation_status,
                "assigned_to": tc.assigned_to,
                "last_executed_at": tc.last_executed_at.isoformat() if tc.last_executed_at else None,
                "last_execution_result": tc.last_execution_result,
                "total_executions": tc.total_executions,
                "pass_count": tc.pass_count,
                "fail_count": tc.fail_count,
                "created_at": tc.created_at.isoformat() if tc.created_at else None,
                "updated_at": tc.updated_at.isoformat() if tc.updated_at else None,
            }
            for tc in test_cases
        ],
    }


@router.get("/api/v1/test-cases/{test_case_id}")
async def get_test_case(
    request: Request,
    test_case_id: str,
    claims: Annotated[dict[str, Any], Depends(auth_guard)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Get a specific test case by ID."""
    enforce_rate_limit(request, claims)

    repo = TestCaseRepository(db)
    tc = await repo.get_by_id(test_case_id)

    if not tc:
        raise HTTPException(status_code=404, detail="Test case not found")

    return {
        "id": str(tc.id),
        "test_case_number": tc.test_case_number,
        "project_id": str(tc.project_id),
        "title": tc.title,
        "description": tc.description,
        "objective": tc.objective,
        "status": tc.status,
        "test_type": tc.test_type,
        "priority": tc.priority,
        "category": tc.category,
        "tags": tc.tags,
        "preconditions": tc.preconditions,
        "test_steps": tc.test_steps,
        "expected_result": tc.expected_result,
        "postconditions": tc.postconditions,
        "test_data": tc.test_data,
        "automation_status": tc.automation_status,
        "automation_script_path": tc.automation_script_path,
        "automation_framework": tc.automation_framework,
        "automation_notes": tc.automation_notes,
        "estimated_duration_minutes": tc.estimated_duration_minutes,
        "created_by": tc.created_by,
        "assigned_to": tc.assigned_to,
        "reviewed_by": tc.reviewed_by,
        "approved_by": tc.approved_by,
        "reviewed_at": tc.reviewed_at.isoformat() if tc.reviewed_at else None,
        "approved_at": tc.approved_at.isoformat() if tc.approved_at else None,
        "deprecated_at": tc.deprecated_at.isoformat() if tc.deprecated_at else None,
        "deprecation_reason": tc.deprecation_reason,
        "last_executed_at": tc.last_executed_at.isoformat() if tc.last_executed_at else None,
        "last_execution_result": tc.last_execution_result,
        "total_executions": tc.total_executions,
        "pass_count": tc.pass_count,
        "fail_count": tc.fail_count,
        "metadata": tc.test_case_metadata,
        "version": tc.version,
        "created_at": tc.created_at.isoformat() if tc.created_at else None,
        "updated_at": tc.updated_at.isoformat() if tc.updated_at else None,
    }


@router.post("/api/v1/test-cases")
async def create_test_case(
    request: Request,
    project_id: str,
    test_case_data: TestCaseCreate,
    claims: Annotated[dict[str, Any], Depends(auth_guard)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Create a new test case."""
    enforce_rate_limit(request, claims)
    ensure_project_access(project_id, claims)
    ensure_write_permission(claims, "create")

    repo = TestCaseRepository(db)

    test_steps = None
    if test_case_data.test_steps:
        test_steps = [step.model_dump() for step in test_case_data.test_steps]

    tc = await repo.create(
        project_id=project_id,
        title=test_case_data.title,
        description=test_case_data.description,
        objective=test_case_data.objective,
        test_type=test_case_data.test_type.value,
        priority=test_case_data.priority.value,
        category=test_case_data.category,
        tags=test_case_data.tags,
        preconditions=test_case_data.preconditions,
        test_steps=test_steps,
        expected_result=test_case_data.expected_result,
        postconditions=test_case_data.postconditions,
        test_data=test_case_data.test_data,
        automation_status=test_case_data.automation_status.value,
        automation_script_path=test_case_data.automation_script_path,
        automation_framework=test_case_data.automation_framework,
        automation_notes=test_case_data.automation_notes,
        estimated_duration_minutes=test_case_data.estimated_duration_minutes,
        assigned_to=test_case_data.assigned_to,
        metadata=test_case_data.metadata,
        created_by=claims.get("sub", "system"),
    )
    await db.commit()

    return {"id": str(tc.id), "test_case_number": tc.test_case_number}


@router.put("/api/v1/test-cases/{test_case_id}")
async def update_test_case(
    request: Request,
    test_case_id: str,
    test_case_data: TestCaseUpdate,
    claims: Annotated[dict[str, Any], Depends(auth_guard)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Update a test case."""
    enforce_rate_limit(request, claims)
    ensure_write_permission(claims, "update")

    repo = TestCaseRepository(db)
    tc = await repo.get_by_id(test_case_id)
    if not tc:
        raise HTTPException(status_code=404, detail="Test case not found")

    updates = test_case_data.model_dump(exclude_unset=True)

    for key in ["test_type", "priority", "automation_status"]:
        if key in updates and updates[key] is not None:
            updates[key] = updates[key].value

    if "test_steps" in updates and updates["test_steps"] is not None:
        updates["test_steps"] = [
            step.model_dump() if hasattr(step, "model_dump") else step for step in updates["test_steps"]
        ]

    if "metadata" in updates:
        updates["test_case_metadata"] = updates.pop("metadata")

    tc = await repo.update(
        test_case_id=test_case_id,
        expected_version=tc.version,
        performed_by=claims.get("sub", "system"),
        **updates,
    )
    await db.commit()

    return {"id": str(tc.id), "version": tc.version}


@router.post("/api/v1/test-cases/{test_case_id}/status")
async def transition_test_case_status(
    request: Request,
    test_case_id: str,
    transition: TestCaseStatusTransition,
    claims: Annotated[dict[str, Any], Depends(auth_guard)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Transition test case to a new status."""
    enforce_rate_limit(request, claims)
    ensure_write_permission(claims, "update")

    repo = TestCaseRepository(db)
    try:
        tc = await repo.transition_status(
            test_case_id=test_case_id,
            to_status=transition.new_status.value,
            reason=transition.reason,
            performed_by=transition.performed_by or claims.get("sub", "system"),
        )
        await db.commit()
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e

    return {"id": str(tc.id), "status": tc.status, "version": tc.version}


@router.post("/api/v1/test-cases/{test_case_id}/submit-review")
async def submit_test_case_for_review(
    request: Request,
    test_case_id: str,
    review_data: TestCaseReview,
    claims: Annotated[dict[str, Any], Depends(auth_guard)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Submit a test case for review."""
    enforce_rate_limit(request, claims)
    ensure_write_permission(claims, "update")

    repo = TestCaseRepository(db)
    try:
        tc = await repo.submit_for_review(
            test_case_id=test_case_id,
            reviewer=review_data.reviewer,
            performed_by=claims.get("sub", "system"),
        )
        await db.commit()
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e

    return {"id": str(tc.id), "status": tc.status, "reviewed_by": tc.reviewed_by}


@router.post("/api/v1/test-cases/{test_case_id}/approve")
async def approve_test_case(
    request: Request,
    test_case_id: str,
    review_data: TestCaseReview,
    claims: Annotated[dict[str, Any], Depends(auth_guard)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Approve a test case after review."""
    enforce_rate_limit(request, claims)
    ensure_write_permission(claims, "update")

    repo = TestCaseRepository(db)
    try:
        tc = await repo.approve(
            test_case_id=test_case_id,
            reviewer_notes=review_data.notes,
            performed_by=claims.get("sub", "system"),
        )
        await db.commit()
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e

    return {"id": str(tc.id), "status": tc.status, "approved_by": tc.approved_by}


@router.post("/api/v1/test-cases/{test_case_id}/deprecate")
async def deprecate_test_case(
    request: Request,
    test_case_id: str,
    deprecation_data: TestCaseDeprecation,
    claims: Annotated[dict[str, Any], Depends(auth_guard)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Deprecate a test case."""
    enforce_rate_limit(request, claims)
    ensure_write_permission(claims, "update")

    repo = TestCaseRepository(db)
    try:
        tc = await repo.deprecate(
            test_case_id=test_case_id,
            reason=deprecation_data.reason,
            replacement_test_case_id=deprecation_data.replacement_test_case_id,
            performed_by=deprecation_data.deprecated_by or claims.get("sub", "system"),
        )
        await db.commit()
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e

    return {"id": str(tc.id), "status": tc.status}


@router.get("/api/v1/test-cases/{test_case_id}/activities")
async def get_test_case_activities(
    request: Request,
    test_case_id: str,
    limit: int = 50,
    claims: dict[str, Any] = Depends(auth_guard),
    db: AsyncSession = Depends(get_db),
):
    """Get activity log for a test case."""
    enforce_rate_limit(request, claims)

    repo = TestCaseRepository(db)
    activities = await repo.get_activities(test_case_id, limit=limit)

    return {
        "test_case_id": test_case_id,
        "activities": [
            {
                "id": str(a.id),
                "test_case_id": str(a.test_case_id),
                "activity_type": a.activity_type,
                "from_value": a.from_value,
                "to_value": a.to_value,
                "description": a.description,
                "performed_by": a.performed_by,
                "metadata": a.activity_metadata,
                "created_at": a.created_at.isoformat() if a.created_at else None,
            }
            for a in activities
        ],
    }


@router.delete("/api/v1/test-cases/{test_case_id}")
async def delete_test_case(
    request: Request,
    test_case_id: str,
    claims: Annotated[dict[str, Any], Depends(auth_guard)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Delete a test case (soft delete)."""
    enforce_rate_limit(request, claims)
    ensure_write_permission(claims, "delete")

    repo = TestCaseRepository(db)
    success = await repo.delete(test_case_id, soft=True)
    await db.commit()

    if not success:
        raise HTTPException(status_code=404, detail="Test case not found")

    return {"deleted": True, "id": test_case_id}


@router.get("/api/v1/projects/{project_id}/test-cases/stats")
async def get_test_case_stats(
    request: Request,
    project_id: str,
    claims: Annotated[dict[str, Any], Depends(auth_guard)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Get test case statistics for a project."""
    enforce_rate_limit(request, claims)
    ensure_project_access(project_id, claims)

    repo = TestCaseRepository(db)
    by_status = await repo.count_by_status(project_id)
    by_type = await repo.count_by_type(project_id)
    by_priority = await repo.count_by_priority(project_id)
    by_automation_status = await repo.count_by_automation_status(project_id)
    execution_summary = await repo.get_execution_summary(project_id)

    return {
        "project_id": project_id,
        "total": sum(by_status.values()),
        "by_status": by_status,
        "by_type": by_type,
        "by_priority": by_priority,
        "by_automation_status": by_automation_status,
        "execution_summary": execution_summary,
    }
