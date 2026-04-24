"""Test coverage API routes."""

from __future__ import annotations

from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession

from tracertm.api.config.rate_limiting import enforce_rate_limit
from tracertm.api.deps import auth_guard, get_db

router = APIRouter(prefix="/api/v1", tags=["coverage"])


def ensure_project_access(project_id: str, claims: dict[str, object] | None) -> None:
    """Check if user has access to project."""
    from tracertm.api.security import ensure_project_access as _ensure_project_access

    _ensure_project_access(project_id, claims)


@router.get("/coverage")
async def list_test_coverage(
    request: Request,
    project_id: str,
    coverage_type: str | None = None,
    status: str | None = None,
    test_case_id: str | None = None,
    requirement_id: str | None = None,
    skip: int = 0,
    limit: int = 100,
    claims: dict[str, Any] = Depends(auth_guard),
    db: AsyncSession = Depends(get_db),
):
    """List test coverage mappings for a project with filtering."""
    enforce_rate_limit(request, claims)
    ensure_project_access(project_id, claims)

    from tracertm.repositories.test_coverage_repository import TestCoverageRepository

    repo = TestCoverageRepository(db)
    coverages, total = await repo.list_by_project(
        project_id=project_id,
        coverage_type=coverage_type,
        status=status,
        test_case_id=test_case_id,
        requirement_id=requirement_id,
        skip=skip,
        limit=limit,
    )

    return {
        "coverages": [
            {
                "id": c.id,
                "project_id": c.project_id,
                "test_case_id": c.test_case_id,
                "requirement_id": c.requirement_id,
                "coverage_type": c.coverage_type.value if hasattr(c.coverage_type, "value") else c.coverage_type,
                "status": c.status.value if hasattr(c.status, "value") else c.status,
                "coverage_percentage": c.coverage_percentage,
                "rationale": c.rationale,
                "notes": c.notes,
                "last_verified_at": c.last_verified_at.isoformat() if c.last_verified_at else None,
                "verified_by": c.verified_by,
                "last_test_result": c.last_test_result,
                "last_tested_at": c.last_tested_at.isoformat() if c.last_tested_at else None,
                "created_by": c.created_by,
                "coverage_metadata": c.coverage_metadata,
                "version": c.version,
                "created_at": c.created_at.isoformat(),
                "updated_at": c.updated_at.isoformat(),
            }
            for c in coverages
        ],
        "total": total,
        "skip": skip,
        "limit": limit,
    }


@router.post("/coverage")
async def create_test_coverage(
    request: Request,
    project_id: str,
    test_case_id: str,
    requirement_id: str,
    coverage_type: str = "direct",
    coverage_percentage: int | None = None,
    rationale: str | None = None,
    notes: str | None = None,
    claims: dict[str, Any] = Depends(auth_guard),
    db: AsyncSession = Depends(get_db),
):
    """Create a new test coverage mapping."""
    enforce_rate_limit(request, claims)
    ensure_project_access(project_id, claims)

    from tracertm.repositories.test_coverage_repository import TestCoverageRepository

    repo = TestCoverageRepository(db)

    existing = await repo.get_by_test_case_and_requirement(test_case_id, requirement_id)
    if existing:
        raise HTTPException(
            status_code=400,
            detail="Coverage mapping already exists for this test case and requirement",
        )

    coverage = await repo.create(
        project_id=project_id,
        test_case_id=test_case_id,
        requirement_id=requirement_id,
        coverage_type=coverage_type,
        coverage_percentage=coverage_percentage,
        rationale=rationale,
        notes=notes,
        created_by=claims.get("user_id"),
    )
    await db.commit()

    return {
        "id": coverage.id,
        "project_id": coverage.project_id,
        "test_case_id": coverage.test_case_id,
        "requirement_id": coverage.requirement_id,
        "coverage_type": coverage.coverage_type.value,
        "status": coverage.status.value,
    }


@router.get("/coverage/{coverage_id}")
async def get_test_coverage(
    request: Request,
    coverage_id: str,
    claims: Annotated[dict[str, Any], Depends(auth_guard)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Get a test coverage mapping by ID."""
    enforce_rate_limit(request, claims)

    from tracertm.repositories.test_coverage_repository import TestCoverageRepository

    repo = TestCoverageRepository(db)
    coverage = await repo.get_by_id(coverage_id)
    if not coverage:
        raise HTTPException(status_code=404, detail="Coverage mapping not found")
    assert coverage is not None

    ensure_project_access(coverage.project_id, claims)

    return {
        "id": coverage.id,
        "project_id": coverage.project_id,
        "test_case_id": coverage.test_case_id,
        "requirement_id": coverage.requirement_id,
        "coverage_type": coverage.coverage_type.value
        if hasattr(coverage.coverage_type, "value")
        else coverage.coverage_type,
        "status": coverage.status.value if hasattr(coverage.status, "value") else coverage.status,
        "coverage_percentage": coverage.coverage_percentage,
        "rationale": coverage.rationale,
        "notes": coverage.notes,
        "last_verified_at": coverage.last_verified_at.isoformat() if coverage.last_verified_at else None,
        "verified_by": coverage.verified_by,
        "last_test_result": coverage.last_test_result,
        "last_tested_at": coverage.last_tested_at.isoformat() if coverage.last_tested_at else None,
        "created_by": coverage.created_by,
        "coverage_metadata": coverage.coverage_metadata,
        "version": coverage.version,
        "created_at": coverage.created_at.isoformat(),
        "updated_at": coverage.updated_at.isoformat(),
    }


@router.put("/coverage/{coverage_id}")
async def update_test_coverage(
    request: Request,
    coverage_id: str,
    coverage_type: str | None = None,
    status: str | None = None,
    coverage_percentage: int | None = None,
    rationale: str | None = None,
    notes: str | None = None,
    claims: dict[str, Any] = Depends(auth_guard),
    db: AsyncSession = Depends(get_db),
):
    """Update a test coverage mapping."""
    enforce_rate_limit(request, claims)

    from tracertm.repositories.test_coverage_repository import TestCoverageRepository

    repo = TestCoverageRepository(db)
    coverage = await repo.get_by_id(coverage_id)
    if not coverage:
        raise HTTPException(status_code=404, detail="Coverage mapping not found")
    assert coverage is not None

    ensure_project_access(coverage.project_id, claims)

    updates: dict[str, Any] = {}
    if coverage_type is not None:
        updates["coverage_type"] = coverage_type
    if status is not None:
        updates["status"] = status
    if coverage_percentage is not None:
        updates["coverage_percentage"] = coverage_percentage
    if rationale is not None:
        updates["rationale"] = rationale
    if notes is not None:
        updates["notes"] = notes

    coverage = await repo.update(
        coverage_id,
        updated_by=claims.get("user_id"),
        **updates,
    )
    await db.commit()

    if coverage is None:
        raise HTTPException(status_code=404, detail="Test coverage not found after update")
    return {"id": coverage.id, "version": coverage.version}


@router.delete("/coverage/{coverage_id}")
async def delete_test_coverage(
    request: Request,
    coverage_id: str,
    claims: Annotated[dict[str, Any], Depends(auth_guard)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Delete a test coverage mapping."""
    enforce_rate_limit(request, claims)

    from tracertm.repositories.test_coverage_repository import TestCoverageRepository

    repo = TestCoverageRepository(db)
    coverage = await repo.get_by_id(coverage_id)
    if not coverage:
        raise HTTPException(status_code=404, detail="Coverage mapping not found")
    assert coverage is not None

    ensure_project_access(coverage.project_id, claims)

    await repo.delete(coverage_id)
    await db.commit()

    return {"deleted": True, "id": coverage_id}


@router.post("/coverage/{coverage_id}/verify")
async def verify_test_coverage(
    request: Request,
    coverage_id: str,
    notes: str | None = None,
    claims: dict[str, Any] = Depends(auth_guard),
    db: AsyncSession = Depends(get_db),
):
    """Mark a coverage mapping as verified."""
    enforce_rate_limit(request, claims)

    from tracertm.repositories.test_coverage_repository import TestCoverageRepository

    repo = TestCoverageRepository(db)
    coverage = await repo.get_by_id(coverage_id)
    if not coverage:
        raise HTTPException(status_code=404, detail="Coverage mapping not found")
    assert coverage is not None

    ensure_project_access(coverage.project_id, claims)

    coverage = await repo.verify_coverage(
        coverage_id,
        verified_by=str(claims.get("user_id", "unknown")),
        notes=notes,
    )
    await db.commit()

    if coverage is None:
        raise HTTPException(status_code=404, detail="Test coverage not found after verification")
    return {
        "id": coverage.id,
        "last_verified_at": coverage.last_verified_at.isoformat() if coverage.last_verified_at else None,
        "verified_by": coverage.verified_by,
    }


@router.get("/coverage/matrix")
async def get_coverage_matrix_endpoint(
    request: Request,
    project_id: str,
    requirement_view: str | None = None,
    claims: dict[str, Any] = Depends(auth_guard),
    db: AsyncSession = Depends(get_db),
):
    """Get the traceability matrix for a project."""
    enforce_rate_limit(request, claims)
    ensure_project_access(project_id, claims)

    from tracertm.repositories.test_coverage_repository import TestCoverageRepository

    repo = TestCoverageRepository(db)
    return await repo.get_traceability_matrix(project_id, requirement_view)


@router.get("/coverage/gaps")
async def get_coverage_gaps(
    request: Request,
    project_id: str,
    requirement_view: str | None = None,
    claims: dict[str, Any] = Depends(auth_guard),
    db: AsyncSession = Depends(get_db),
):
    """Find requirements that have no test coverage."""
    enforce_rate_limit(request, claims)
    ensure_project_access(project_id, claims)

    from tracertm.repositories.test_coverage_repository import TestCoverageRepository

    repo = TestCoverageRepository(db)
    return await repo.get_coverage_gaps(project_id, requirement_view)


@router.get("/test-cases/{test_case_id}/coverage")
async def get_test_case_coverage(
    request: Request,
    test_case_id: str,
    claims: Annotated[dict[str, Any], Depends(auth_guard)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Get coverage summary for a specific test case."""
    enforce_rate_limit(request, claims)

    from tracertm.repositories.test_coverage_repository import TestCoverageRepository

    repo = TestCoverageRepository(db)
    return await repo.get_test_case_coverage_summary(test_case_id)


@router.get("/requirements/{requirement_id}/coverage")
async def get_requirement_coverage(
    request: Request,
    requirement_id: str,
    claims: Annotated[dict[str, Any], Depends(auth_guard)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Get all test cases covering a specific requirement."""
    enforce_rate_limit(request, claims)

    from tracertm.repositories.test_coverage_repository import TestCoverageRepository

    repo = TestCoverageRepository(db)
    coverages = await repo.list_by_requirement(requirement_id)

    return {
        "requirement_id": requirement_id,
        "test_cases": [
            {
                "coverage_id": c.id,
                "test_case_id": c.test_case_id,
                "coverage_type": c.coverage_type.value if hasattr(c.coverage_type, "value") else c.coverage_type,
                "coverage_percentage": c.coverage_percentage,
                "last_test_result": c.last_test_result,
                "last_tested_at": c.last_tested_at.isoformat() if c.last_tested_at else None,
            }
            for c in coverages
        ],
        "total": len(coverages),
    }


@router.get("/projects/{project_id}/coverage/stats")
async def get_coverage_stats(
    request: Request,
    project_id: str,
    claims: Annotated[dict[str, Any], Depends(auth_guard)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Get coverage statistics for a project."""
    enforce_rate_limit(request, claims)
    ensure_project_access(project_id, claims)

    from tracertm.repositories.test_coverage_repository import TestCoverageRepository

    repo = TestCoverageRepository(db)
    return await repo.get_stats(project_id)


@router.get("/coverage/{coverage_id}/activities")
async def get_coverage_activities(
    request: Request,
    coverage_id: str,
    limit: int = 50,
    claims: dict[str, Any] = Depends(auth_guard),
    db: AsyncSession = Depends(get_db),
):
    """Get activity log for a coverage mapping."""
    enforce_rate_limit(request, claims)

    from tracertm.repositories.test_coverage_repository import TestCoverageRepository

    repo = TestCoverageRepository(db)
    coverage = await repo.get_by_id(coverage_id)
    if not coverage:
        raise HTTPException(status_code=404, detail="Coverage mapping not found")
    assert coverage is not None

    ensure_project_access(coverage.project_id, claims)

    activities = await repo.get_activities(coverage_id, limit)

    return {
        "coverage_id": coverage_id,
        "activities": [
            {
                "id": a.id,
                "coverage_id": a.coverage_id,
                "activity_type": a.activity_type,
                "from_value": a.from_value,
                "to_value": a.to_value,
                "description": a.description,
                "performed_by": a.performed_by,
                "activity_metadata": a.activity_metadata,
                "created_at": a.created_at.isoformat(),
            }
            for a in activities
        ],
    }
