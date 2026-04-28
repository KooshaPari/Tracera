"""Test run management API routes."""

from __future__ import annotations

from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession

from tracertm.api.config.rate_limiting import enforce_rate_limit
from tracertm.api.deps import auth_guard, get_db

router = APIRouter(prefix="/api/v1", tags=["test-runs"])


def ensure_project_access(project_id: str, claims: dict[str, object] | None) -> None:
    """Check if user has access to project."""
    from tracertm.api.security import ensure_project_access as _ensure_project_access

    _ensure_project_access(project_id, claims)


@router.get("/test-runs")
async def list_test_runs(
    request: Request,
    project_id: str,
    status: str | None = None,
    run_type: str | None = None,
    suite_id: str | None = None,
    environment: str | None = None,
    initiated_by: str | None = None,
    skip: int = 0,
    limit: int = 50,
    claims: dict[str, Any] = Depends(auth_guard),
    db: AsyncSession = Depends(get_db),
):
    """List test runs for a project with filtering."""
    enforce_rate_limit(request, claims)
    ensure_project_access(project_id, claims)

    from tracertm.repositories.test_run_repository import TestRunRepository

    repo = TestRunRepository(db)
    runs, total = await repo.list_by_project(
        project_id=project_id,
        status=status,
        run_type=run_type,
        suite_id=suite_id,
        environment=environment,
        initiated_by=initiated_by,
        skip=skip,
        limit=limit,
    )

    return {
        "test_runs": [
            {
                "id": r.id,
                "run_number": r.run_number,
                "project_id": r.project_id,
                "suite_id": r.suite_id,
                "name": r.name,
                "description": r.description,
                "status": r.status.value if hasattr(r.status, "value") else r.status,
                "run_type": r.run_type.value if hasattr(r.run_type, "value") else r.run_type,
                "environment": r.environment,
                "build_number": r.build_number,
                "build_url": r.build_url,
                "branch": r.branch,
                "commit_sha": r.commit_sha,
                "scheduled_at": r.scheduled_at.isoformat() if r.scheduled_at else None,
                "started_at": r.started_at.isoformat() if r.started_at else None,
                "completed_at": r.completed_at.isoformat() if r.completed_at else None,
                "duration_seconds": r.duration_seconds,
                "initiated_by": r.initiated_by,
                "executed_by": r.executed_by,
                "total_tests": r.total_tests,
                "passed_count": r.passed_count,
                "failed_count": r.failed_count,
                "skipped_count": r.skipped_count,
                "blocked_count": r.blocked_count,
                "error_count": r.error_count,
                "pass_rate": r.pass_rate,
                "tags": r.tags,
                "external_run_id": r.external_run_id,
                "metadata": r.run_metadata,
                "version": r.version,
                "created_at": r.created_at.isoformat(),
                "updated_at": r.updated_at.isoformat(),
            }
            for r in runs
        ],
        "total": total,
    }


@router.get("/test-runs/{run_id}")
async def get_test_run(
    request: Request,
    run_id: str,
    claims: Annotated[dict[str, Any], Depends(auth_guard)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Get a test run by ID."""
    enforce_rate_limit(request, claims)

    from tracertm.repositories.test_run_repository import TestRunRepository

    repo = TestRunRepository(db)
    run = await repo.get_by_id(run_id)
    if not run:
        raise HTTPException(status_code=404, detail="Test run not found")
    assert run is not None

    ensure_project_access(run.project_id, claims)

    return {
        "id": run.id,
        "run_number": run.run_number,
        "project_id": run.project_id,
        "suite_id": run.suite_id,
        "name": run.name,
        "description": run.description,
        "status": run.status.value if hasattr(run.status, "value") else run.status,
        "run_type": run.run_type.value if hasattr(run.run_type, "value") else run.run_type,
        "environment": run.environment,
        "build_number": run.build_number,
        "build_url": run.build_url,
        "branch": run.branch,
        "commit_sha": run.commit_sha,
        "scheduled_at": run.scheduled_at.isoformat() if run.scheduled_at else None,
        "started_at": run.started_at.isoformat() if run.started_at else None,
        "completed_at": run.completed_at.isoformat() if run.completed_at else None,
        "duration_seconds": run.duration_seconds,
        "initiated_by": run.initiated_by,
        "executed_by": run.executed_by,
        "total_tests": run.total_tests,
        "passed_count": run.passed_count,
        "failed_count": run.failed_count,
        "skipped_count": run.skipped_count,
        "blocked_count": run.blocked_count,
        "error_count": run.error_count,
        "pass_rate": run.pass_rate,
        "notes": run.notes,
        "failure_summary": run.failure_summary,
        "tags": run.tags,
        "external_run_id": run.external_run_id,
        "webhook_id": run.webhook_id,
        "metadata": run.run_metadata,
        "version": run.version,
        "created_at": run.created_at.isoformat(),
        "updated_at": run.updated_at.isoformat(),
    }


@router.post("/test-runs")
async def create_test_run(
    request: Request,
    project_id: str,
    run_data: dict[str, Any],
    claims: Annotated[dict[str, Any], Depends(auth_guard)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Create a new test run."""
    enforce_rate_limit(request, claims)
    ensure_project_access(project_id, claims)

    from tracertm.repositories.test_run_repository import TestRunRepository

    repo = TestRunRepository(db)
    run = await repo.create(
        project_id=project_id,
        name=run_data["name"],
        description=run_data.get("description"),
        suite_id=run_data.get("suite_id"),
        run_type=run_data.get("run_type", "manual"),
        environment=run_data.get("environment"),
        build_number=run_data.get("build_number"),
        build_url=run_data.get("build_url"),
        branch=run_data.get("branch"),
        commit_sha=run_data.get("commit_sha"),
        scheduled_at=run_data.get("scheduled_at"),
        initiated_by=claims.get("sub"),
        tags=run_data.get("tags"),
        external_run_id=run_data.get("external_run_id"),
        webhook_id=run_data.get("webhook_id"),
        metadata=run_data.get("metadata"),
    )
    await db.commit()

    return {"id": run.id, "run_number": run.run_number}


@router.put("/test-runs/{run_id}")
async def update_test_run(
    request: Request,
    run_id: str,
    run_data: dict[str, Any],
    claims: Annotated[dict[str, Any], Depends(auth_guard)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Update a test run."""
    enforce_rate_limit(request, claims)

    from tracertm.repositories.test_run_repository import TestRunRepository

    repo = TestRunRepository(db)
    run = await repo.get_by_id(run_id)
    if not run:
        raise HTTPException(status_code=404, detail="Test run not found")
    assert run is not None

    ensure_project_access(run.project_id, claims)

    updates = {k: v for k, v in run_data.items() if v is not None}
    if "metadata" in updates:
        updates["run_metadata"] = updates.pop("metadata")

    updated = await repo.update(run_id, updated_by=claims.get("sub"), **updates)
    await db.commit()

    if updated is None:
        raise HTTPException(status_code=404, detail="Test run not found after update")
    return {"id": updated.id, "version": updated.version}


@router.post("/test-runs/{run_id}/start")
async def start_test_run(
    request: Request,
    run_id: str,
    start_data: dict[str, Any] | None = None,
    claims: dict[str, Any] = Depends(auth_guard),
    db: AsyncSession = Depends(get_db),
):
    """Start a test run."""
    enforce_rate_limit(request, claims)

    from tracertm.repositories.test_run_repository import TestRunRepository

    repo = TestRunRepository(db)
    run = await repo.get_by_id(run_id)
    if not run:
        raise HTTPException(status_code=404, detail="Test run not found")
    assert run is not None

    ensure_project_access(run.project_id, claims)

    start_data = start_data or {}
    updated = await repo.start(
        run_id=run_id,
        executed_by=start_data.get("executed_by") or claims.get("sub"),
    )
    await db.commit()

    if updated is None:
        raise HTTPException(status_code=404, detail="Test run not found after start")
    return {
        "id": updated.id,
        "status": updated.status.value if hasattr(updated.status, "value") else updated.status,
        "started_at": updated.started_at.isoformat() if updated.started_at else None,
    }


@router.post("/test-runs/{run_id}/complete")
async def complete_test_run(
    request: Request,
    run_id: str,
    complete_data: dict[str, Any] | None = None,
    claims: dict[str, Any] = Depends(auth_guard),
    db: AsyncSession = Depends(get_db),
):
    """Complete a test run."""
    enforce_rate_limit(request, claims)

    from tracertm.repositories.test_run_repository import TestRunRepository

    repo = TestRunRepository(db)
    run = await repo.get_by_id(run_id)
    if not run:
        raise HTTPException(status_code=404, detail="Test run not found")
    assert run is not None

    ensure_project_access(run.project_id, claims)

    complete_data = complete_data or {}
    updated = await repo.complete(
        run_id=run_id,
        status=complete_data.get("status"),
        notes=complete_data.get("notes"),
        failure_summary=complete_data.get("failure_summary"),
        completed_by=claims.get("sub"),
    )
    await db.commit()

    if updated is None:
        raise HTTPException(status_code=404, detail="Test run not found after complete")
    return {
        "id": updated.id,
        "status": updated.status.value if hasattr(updated.status, "value") else updated.status,
        "completed_at": updated.completed_at.isoformat() if updated.completed_at else None,
        "pass_rate": updated.pass_rate,
    }


@router.post("/test-runs/{run_id}/cancel")
async def cancel_test_run(
    request: Request,
    run_id: str,
    cancel_data: dict[str, Any] | None = None,
    claims: dict[str, Any] = Depends(auth_guard),
    db: AsyncSession = Depends(get_db),
):
    """Cancel a test run."""
    enforce_rate_limit(request, claims)

    from tracertm.repositories.test_run_repository import TestRunRepository

    repo = TestRunRepository(db)
    run = await repo.get_by_id(run_id)
    if not run:
        raise HTTPException(status_code=404, detail="Test run not found")
    assert run is not None

    ensure_project_access(run.project_id, claims)

    cancel_data = cancel_data or {}
    updated = await repo.cancel(
        run_id=run_id,
        reason=cancel_data.get("reason"),
        cancelled_by=claims.get("sub"),
    )
    await db.commit()

    if updated is None:
        raise HTTPException(status_code=404, detail="Test run not found after cancel")
    return {
        "id": updated.id,
        "status": updated.status.value if hasattr(updated.status, "value") else updated.status,
    }


@router.delete("/test-runs/{run_id}")
async def delete_test_run(
    request: Request,
    run_id: str,
    claims: Annotated[dict[str, Any], Depends(auth_guard)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Delete a test run."""
    enforce_rate_limit(request, claims)

    from tracertm.repositories.test_run_repository import TestRunRepository

    repo = TestRunRepository(db)
    run = await repo.get_by_id(run_id)
    if not run:
        raise HTTPException(status_code=404, detail="Test run not found")
    assert run is not None

    ensure_project_access(run.project_id, claims)

    await repo.delete(run_id)
    await db.commit()

    return {"deleted": True, "id": run_id}


@router.get("/projects/{project_id}/test-runs/stats")
async def get_test_run_stats(
    request: Request,
    project_id: str,
    claims: Annotated[dict[str, Any], Depends(auth_guard)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Get test run statistics for a project."""
    enforce_rate_limit(request, claims)
    ensure_project_access(project_id, claims)

    from tracertm.repositories.test_run_repository import TestRunRepository

    repo = TestRunRepository(db)
    stats = await repo.get_stats(project_id)

    stats["recent_runs"] = [
        {
            "id": r.id,
            "run_number": r.run_number,
            "name": r.name,
            "status": r.status.value if hasattr(r.status, "value") else r.status,
            "pass_rate": r.pass_rate,
            "created_at": r.created_at.isoformat(),
        }
        for r in stats.get("recent_runs", [])
    ]

    return stats
