"""Test suite management API routes."""

from __future__ import annotations

from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession

from tracertm.api.config.rate_limiting import enforce_rate_limit
from tracertm.api.deps import auth_guard, get_db

router = APIRouter(prefix="/api/v1", tags=["test-suites"])


def ensure_project_access(project_id: str, claims: dict[str, object] | None) -> None:
    """Check if user has access to project."""
    from tracertm.api.security import ensure_project_access as _ensure_project_access

    _ensure_project_access(project_id, claims)


@router.get("/test-suites")
async def list_test_suites(
    request: Request,
    project_id: str,
    status: str | None = None,
    category: str | None = None,
    parent_id: str | None = None,
    owner: str | None = None,
    search: str | None = None,
    skip: int = 0,
    limit: int = 50,
    claims: dict[str, Any] = Depends(auth_guard),
    db: AsyncSession = Depends(get_db),
):
    """List test suites for a project with filtering."""
    enforce_rate_limit(request, claims)
    ensure_project_access(project_id, claims)

    from tracertm.repositories.test_suite_repository import TestSuiteRepository

    repo = TestSuiteRepository(db)
    suites, total = await repo.list_by_project(
        project_id=project_id,
        status=status,
        category=category,
        parent_id=parent_id,
        owner=owner,
        search=search,
        skip=skip,
        limit=limit,
    )

    return {
        "test_suites": [
            {
                "id": s.id,
                "suite_number": s.suite_number,
                "project_id": s.project_id,
                "name": s.name,
                "description": s.description,
                "objective": s.objective,
                "status": s.status.value if hasattr(s.status, "value") else s.status,
                "parent_id": s.parent_id,
                "order_index": s.order_index,
                "category": s.category,
                "tags": s.tags,
                "is_parallel_execution": s.is_parallel_execution,
                "estimated_duration_minutes": s.estimated_duration_minutes,
                "required_environment": s.required_environment,
                "owner": s.owner,
                "responsible_team": s.responsible_team,
                "total_test_cases": s.total_test_cases,
                "automated_count": s.automated_count,
                "last_run_at": s.last_run_at.isoformat() if s.last_run_at else None,
                "last_run_result": s.last_run_result,
                "pass_rate": s.pass_rate,
                "metadata": s.suite_metadata,
                "version": s.version,
                "created_at": s.created_at.isoformat(),
                "updated_at": s.updated_at.isoformat(),
            }
            for s in suites
        ],
        "total": total,
    }


@router.get("/test-suites/{suite_id}")
async def get_test_suite(
    request: Request,
    suite_id: str,
    claims: Annotated[dict[str, Any], Depends(auth_guard)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Get a test suite by ID."""
    enforce_rate_limit(request, claims)

    from tracertm.repositories.test_suite_repository import TestSuiteRepository

    repo = TestSuiteRepository(db)
    suite = await repo.get_by_id(suite_id)
    if not suite:
        raise HTTPException(status_code=404, detail="Test suite not found")
    assert suite is not None

    ensure_project_access(suite.project_id, claims)

    return {
        "id": suite.id,
        "suite_number": suite.suite_number,
        "project_id": suite.project_id,
        "name": suite.name,
        "description": suite.description,
        "objective": suite.objective,
        "status": suite.status.value if hasattr(suite.status, "value") else suite.status,
        "parent_id": suite.parent_id,
        "order_index": suite.order_index,
        "category": suite.category,
        "tags": suite.tags,
        "is_parallel_execution": suite.is_parallel_execution,
        "estimated_duration_minutes": suite.estimated_duration_minutes,
        "required_environment": suite.required_environment,
        "environment_variables": suite.environment_variables,
        "setup_instructions": suite.setup_instructions,
        "teardown_instructions": suite.teardown_instructions,
        "owner": suite.owner,
        "responsible_team": suite.responsible_team,
        "total_test_cases": suite.total_test_cases,
        "automated_count": suite.automated_count,
        "last_run_at": suite.last_run_at.isoformat() if suite.last_run_at else None,
        "last_run_result": suite.last_run_result,
        "pass_rate": suite.pass_rate,
        "metadata": suite.suite_metadata,
        "version": suite.version,
        "created_at": suite.created_at.isoformat(),
        "updated_at": suite.updated_at.isoformat(),
    }


@router.post("/test-suites")
async def create_test_suite(
    request: Request,
    project_id: str,
    suite_data: dict[str, Any],
    claims: Annotated[dict[str, Any], Depends(auth_guard)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Create a new test suite."""
    enforce_rate_limit(request, claims)
    ensure_project_access(project_id, claims)

    from tracertm.repositories.test_suite_repository import TestSuiteRepository

    repo = TestSuiteRepository(db)
    suite = await repo.create(
        project_id=project_id,
        name=suite_data["name"],
        description=suite_data.get("description"),
        objective=suite_data.get("objective"),
        parent_id=suite_data.get("parent_id"),
        order_index=suite_data.get("order_index", 0),
        category=suite_data.get("category"),
        tags=suite_data.get("tags"),
        is_parallel_execution=suite_data.get("is_parallel_execution", False),
        estimated_duration_minutes=suite_data.get("estimated_duration_minutes"),
        required_environment=suite_data.get("required_environment"),
        environment_variables=suite_data.get("environment_variables"),
        setup_instructions=suite_data.get("setup_instructions"),
        teardown_instructions=suite_data.get("teardown_instructions"),
        owner=suite_data.get("owner"),
        responsible_team=suite_data.get("responsible_team"),
        metadata=suite_data.get("metadata"),
        created_by=claims.get("sub"),
    )
    await db.commit()

    return {"id": suite.id, "suite_number": suite.suite_number}


@router.put("/test-suites/{suite_id}")
async def update_test_suite(
    request: Request,
    suite_id: str,
    suite_data: dict[str, Any],
    claims: Annotated[dict[str, Any], Depends(auth_guard)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Update a test suite."""
    enforce_rate_limit(request, claims)

    from tracertm.repositories.test_suite_repository import TestSuiteRepository

    repo = TestSuiteRepository(db)
    suite = await repo.get_by_id(suite_id)
    if not suite:
        raise HTTPException(status_code=404, detail="Test suite not found")
    assert suite is not None

    ensure_project_access(suite.project_id, claims)

    updates = {k: v for k, v in suite_data.items() if v is not None}
    if "metadata" in updates:
        updates["suite_metadata"] = updates.pop("metadata")

    updated = await repo.update(suite_id, updated_by=claims.get("sub"), **updates)
    if not updated:
        raise HTTPException(status_code=404, detail="Test suite not found")
    await db.commit()

    return {"id": updated.id, "version": updated.version}


@router.post("/test-suites/{suite_id}/status")
async def transition_test_suite_status(
    request: Request,
    suite_id: str,
    status_data: dict[str, Any],
    claims: Annotated[dict[str, Any], Depends(auth_guard)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Transition test suite status."""
    enforce_rate_limit(request, claims)

    from tracertm.repositories.test_suite_repository import TestSuiteRepository

    repo = TestSuiteRepository(db)
    suite = await repo.get_by_id(suite_id)
    if not suite:
        raise HTTPException(status_code=404, detail="Test suite not found")
    assert suite is not None

    ensure_project_access(suite.project_id, claims)

    updated = await repo.transition_status(
        suite_id=suite_id,
        new_status=status_data["new_status"],
        reason=status_data.get("reason"),
        performed_by=claims.get("sub"),
    )
    await db.commit()

    if updated is None:
        raise HTTPException(status_code=404, detail="Test suite not found")
    return {
        "id": updated.id,
        "status": updated.status.value if hasattr(updated.status, "value") else updated.status,
        "version": updated.version,
    }


@router.post("/test-suites/{suite_id}/test-cases")
async def add_test_case_to_suite(
    request: Request,
    suite_id: str,
    tc_data: dict[str, Any],
    claims: Annotated[dict[str, Any], Depends(auth_guard)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Add a test case to a suite."""
    enforce_rate_limit(request, claims)

    from tracertm.repositories.test_suite_repository import TestSuiteRepository

    repo = TestSuiteRepository(db)
    suite = await repo.get_by_id(suite_id)
    if not suite:
        raise HTTPException(status_code=404, detail="Test suite not found")
    assert suite is not None

    ensure_project_access(suite.project_id, claims)

    association = await repo.add_test_case(
        suite_id=suite_id,
        test_case_id=tc_data["test_case_id"],
        order_index=tc_data.get("order_index", 0),
        is_mandatory=tc_data.get("is_mandatory", True),
        skip_reason=tc_data.get("skip_reason"),
        custom_parameters=tc_data.get("custom_parameters"),
        added_by=claims.get("sub"),
    )
    await db.commit()

    return {"id": association.id, "suite_id": suite_id, "test_case_id": tc_data["test_case_id"]}


@router.delete("/test-suites/{suite_id}/test-cases/{test_case_id}")
async def remove_test_case_from_suite(
    request: Request,
    suite_id: str,
    test_case_id: str,
    claims: Annotated[dict[str, Any], Depends(auth_guard)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Remove a test case from a suite."""
    enforce_rate_limit(request, claims)

    from tracertm.repositories.test_suite_repository import TestSuiteRepository

    repo = TestSuiteRepository(db)
    suite = await repo.get_by_id(suite_id)
    if not suite:
        raise HTTPException(status_code=404, detail="Test suite not found")
    assert suite is not None

    ensure_project_access(suite.project_id, claims)

    success = await repo.remove_test_case(suite_id, test_case_id, claims.get("sub"))
    await db.commit()

    if not success:
        raise HTTPException(status_code=404, detail="Test case not in suite")

    return {"removed": True}


@router.get("/test-suites/{suite_id}/test-cases")
async def get_suite_test_cases(
    request: Request,
    suite_id: str,
    claims: Annotated[dict[str, Any], Depends(auth_guard)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Get test cases in a suite."""
    enforce_rate_limit(request, claims)

    from tracertm.repositories.test_suite_repository import TestSuiteRepository

    repo = TestSuiteRepository(db)
    suite = await repo.get_by_id(suite_id)
    if not suite:
        raise HTTPException(status_code=404, detail="Test suite not found")
    assert suite is not None

    ensure_project_access(suite.project_id, claims)

    associations = await repo.get_test_cases(suite_id)

    return {
        "suite_id": suite_id,
        "test_cases": [
            {
                "id": a.id,
                "test_case_id": a.test_case_id,
                "order_index": a.order_index,
                "is_mandatory": a.is_mandatory,
                "skip_reason": a.skip_reason,
                "custom_parameters": a.custom_parameters,
            }
            for a in associations
        ],
    }


@router.get("/test-suites/{suite_id}/activities")
async def get_test_suite_activities(
    request: Request,
    suite_id: str,
    limit: int = 50,
    claims: dict[str, Any] = Depends(auth_guard),
    db: AsyncSession = Depends(get_db),
):
    """Get activity log for a test suite."""
    enforce_rate_limit(request, claims)

    from tracertm.repositories.test_suite_repository import TestSuiteRepository

    repo = TestSuiteRepository(db)
    suite = await repo.get_by_id(suite_id)
    if not suite:
        raise HTTPException(status_code=404, detail="Test suite not found")
    assert suite is not None

    ensure_project_access(suite.project_id, claims)

    activities = await repo.get_activities(suite_id, limit)

    return {
        "suite_id": suite_id,
        "activities": [
            {
                "id": a.id,
                "suite_id": a.suite_id,
                "activity_type": a.activity_type,
                "from_value": a.from_value,
                "to_value": a.to_value,
                "description": a.description,
                "performed_by": a.performed_by,
                "metadata": a.activity_metadata,
                "created_at": a.created_at.isoformat(),
            }
            for a in activities
        ],
    }


@router.delete("/test-suites/{suite_id}")
async def delete_test_suite(
    request: Request,
    suite_id: str,
    claims: Annotated[dict[str, Any], Depends(auth_guard)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Delete a test suite."""
    enforce_rate_limit(request, claims)

    from tracertm.repositories.test_suite_repository import TestSuiteRepository

    repo = TestSuiteRepository(db)
    suite = await repo.get_by_id(suite_id)
    if not suite:
        raise HTTPException(status_code=404, detail="Test suite not found")
    assert suite is not None

    ensure_project_access(suite.project_id, claims)

    await repo.delete(suite_id)
    await db.commit()

    return {"deleted": True, "id": suite_id}


@router.get("/projects/{project_id}/test-suites/stats")
async def get_test_suite_stats(
    request: Request,
    project_id: str,
    claims: Annotated[dict[str, Any], Depends(auth_guard)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Get test suite statistics for a project."""
    enforce_rate_limit(request, claims)
    ensure_project_access(project_id, claims)

    from tracertm.repositories.test_suite_repository import TestSuiteRepository

    repo = TestSuiteRepository(db)
    return await repo.get_stats(project_id)
