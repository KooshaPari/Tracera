"""Test run result and activity API routes."""

from __future__ import annotations

from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession

from tracertm.api.config.rate_limiting import enforce_rate_limit
from tracertm.api.deps import auth_guard, get_db

router = APIRouter(prefix="/api/v1", tags=["test-run-results"])


def ensure_project_access(project_id: str, claims: dict[str, object] | None) -> None:
    """Check if user has access to project."""
    from tracertm.api.security import ensure_project_access as _ensure_project_access

    _ensure_project_access(project_id, claims)


@router.post("/test-runs/{run_id}/results")
async def submit_test_result(
    request: Request,
    run_id: str,
    result_data: dict[str, Any],
    claims: Annotated[dict[str, Any], Depends(auth_guard)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Submit a single test result."""
    enforce_rate_limit(request, claims)

    from tracertm.repositories.test_run_repository import TestRunRepository

    repo = TestRunRepository(db)
    run = await repo.get_by_id(run_id)
    if not run:
        raise HTTPException(status_code=404, detail="Test run not found")
    assert run is not None

    ensure_project_access(run.project_id, claims)

    result = await repo.add_result(
        run_id=run_id,
        test_case_id=result_data["test_case_id"],
        status=result_data["status"],
        started_at=result_data.get("started_at"),
        completed_at=result_data.get("completed_at"),
        duration_seconds=result_data.get("duration_seconds"),
        executed_by=result_data.get("executed_by") or claims.get("sub"),
        actual_result=result_data.get("actual_result"),
        failure_reason=result_data.get("failure_reason"),
        error_message=result_data.get("error_message"),
        stack_trace=result_data.get("stack_trace"),
        screenshots=result_data.get("screenshots"),
        logs_url=result_data.get("logs_url"),
        attachments=result_data.get("attachments"),
        step_results=result_data.get("step_results"),
        linked_defect_ids=result_data.get("linked_defect_ids"),
        created_defect_id=result_data.get("created_defect_id"),
        retry_count=result_data.get("retry_count", 0),
        is_flaky=result_data.get("is_flaky", False),
        notes=result_data.get("notes"),
        metadata=result_data.get("metadata"),
    )
    await db.commit()

    return {"id": result.id, "run_id": run_id, "test_case_id": result_data["test_case_id"]}


@router.post("/test-runs/{run_id}/bulk-results")
async def submit_bulk_test_results(
    request: Request,
    run_id: str,
    bulk_data: dict[str, Any],
    claims: Annotated[dict[str, Any], Depends(auth_guard)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Submit multiple test results at once."""
    enforce_rate_limit(request, claims)

    from tracertm.repositories.test_run_repository import TestRunRepository

    repo = TestRunRepository(db)
    run = await repo.get_by_id(run_id)
    if not run:
        raise HTTPException(status_code=404, detail="Test run not found")
    assert run is not None

    ensure_project_access(run.project_id, claims)

    results = await repo.add_bulk_results(run_id, bulk_data.get("results", []))
    await db.commit()

    return {
        "run_id": run_id,
        "submitted_count": len(results),
        "result_ids": [r.id for r in results],
    }


@router.get("/test-runs/{run_id}/results")
async def get_test_run_results(
    request: Request,
    run_id: str,
    status: str | None = None,
    claims: dict[str, Any] = Depends(auth_guard),
    db: AsyncSession = Depends(get_db),
):
    """Get all results for a test run."""
    enforce_rate_limit(request, claims)

    from tracertm.repositories.test_run_repository import TestRunRepository

    repo = TestRunRepository(db)
    run = await repo.get_by_id(run_id)
    if not run:
        raise HTTPException(status_code=404, detail="Test run not found")
    assert run is not None

    ensure_project_access(run.project_id, claims)

    results = await repo.get_results(run_id, status)

    return {
        "run_id": run_id,
        "results": [
            {
                "id": r.id,
                "run_id": r.run_id,
                "test_case_id": r.test_case_id,
                "status": r.status.value if hasattr(r.status, "value") else r.status,
                "started_at": r.started_at.isoformat() if r.started_at else None,
                "completed_at": r.completed_at.isoformat() if r.completed_at else None,
                "duration_seconds": r.duration_seconds,
                "executed_by": r.executed_by,
                "actual_result": r.actual_result,
                "failure_reason": r.failure_reason,
                "error_message": r.error_message,
                "screenshots": r.screenshots,
                "logs_url": r.logs_url,
                "step_results": r.step_results,
                "linked_defect_ids": r.linked_defect_ids,
                "retry_count": r.retry_count,
                "is_flaky": r.is_flaky,
                "notes": r.notes,
                "metadata": r.run_metadata,
                "created_at": r.created_at.isoformat(),
            }
            for r in results
        ],
        "total": len(results),
    }


@router.get("/test-runs/{run_id}/activities")
async def get_test_run_activities(
    request: Request,
    run_id: str,
    limit: int = 50,
    claims: dict[str, Any] = Depends(auth_guard),
    db: AsyncSession = Depends(get_db),
):
    """Get activity log for a test run."""
    enforce_rate_limit(request, claims)

    from tracertm.repositories.test_run_repository import TestRunRepository

    repo = TestRunRepository(db)
    run = await repo.get_by_id(run_id)
    if not run:
        raise HTTPException(status_code=404, detail="Test run not found")
    assert run is not None

    ensure_project_access(run.project_id, claims)

    activities = await repo.get_activities(run_id, limit)

    return {
        "run_id": run_id,
        "activities": [
            {
                "id": a.id,
                "run_id": a.run_id,
                "activity_type": a.activity_type,
                "from_value": a.from_value,
                "to_value": a.to_value,
                "description": a.description,
                "performed_by": a.performed_by,
                "metadata": a.run_metadata,
                "created_at": a.created_at.isoformat(),
            }
            for a in activities
        ],
    }
