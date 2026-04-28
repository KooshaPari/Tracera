"""QA metrics dashboard API routes."""

from __future__ import annotations

import operator
from datetime import UTC, datetime, timedelta
from typing import Annotated, Any

from fastapi import APIRouter, Depends, Request
from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from tracertm.api.config.rate_limiting import enforce_rate_limit
from tracertm.api.deps import auth_guard, get_db

router = APIRouter(prefix="/api/v1/qa/metrics", tags=["qa-metrics"])


def ensure_project_access(project_id: str, claims: dict[str, object] | None) -> None:
    """Check if user has access to project."""
    from tracertm.api.security import ensure_project_access as _ensure_project_access

    _ensure_project_access(project_id, claims)


@router.get("/summary")
async def get_qa_metrics_summary(
    request: Request,
    project_id: str,
    claims: Annotated[dict[str, Any], Depends(auth_guard)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Get comprehensive QA metrics summary for dashboard."""
    enforce_rate_limit(request, claims)
    ensure_project_access(project_id, claims)

    from tracertm.repositories.test_case_repository import TestCaseRepository
    from tracertm.repositories.test_coverage_repository import TestCoverageRepository
    from tracertm.repositories.test_run_repository import TestRunRepository
    from tracertm.repositories.test_suite_repository import TestSuiteRepository

    test_case_repo = TestCaseRepository(db)
    test_suite_repo = TestSuiteRepository(db)
    test_run_repo = TestRunRepository(db)
    coverage_repo = TestCoverageRepository(db)

    test_case_stats = await test_case_repo.get_stats(project_id)
    test_suite_stats = await test_suite_repo.get_stats(project_id)
    test_run_stats = await test_run_repo.get_stats(project_id)
    coverage_stats = await coverage_repo.get_stats(project_id)

    coverage_matrix = await coverage_repo.get_traceability_matrix(project_id)

    return {
        "project_id": project_id,
        "test_cases": {
            "total": test_case_stats.get("total", 0),
            "by_status": test_case_stats.get("by_status", {}),
            "by_priority": test_case_stats.get("by_priority", {}),
            "automated_count": test_case_stats.get("automated_count", 0),
            "manual_count": test_case_stats.get("manual_count", 0),
            "automation_percentage": (
                round(test_case_stats.get("automated_count", 0) / test_case_stats.get("total", 1) * 100, 1)
                if test_case_stats.get("total", 0) > 0
                else 0
            ),
        },
        "test_suites": {
            "total": test_suite_stats.get("total", 0),
            "by_status": test_suite_stats.get("by_status", {}),
            "total_test_cases": test_suite_stats.get("total_test_cases", 0),
        },
        "test_runs": {
            "total": test_run_stats.get("total_runs", 0),
            "by_status": test_run_stats.get("by_status", {}),
            "by_type": test_run_stats.get("by_type", {}),
            "average_pass_rate": test_run_stats.get("average_pass_rate", 0),
            "average_duration_seconds": test_run_stats.get("average_duration_seconds", 0),
        },
        "coverage": {
            "total_requirements": coverage_matrix.get("total_requirements", 0),
            "covered_requirements": coverage_matrix.get("covered_requirements", 0),
            "uncovered_requirements": coverage_matrix.get("uncovered_requirements", 0),
            "coverage_percentage": coverage_matrix.get("coverage_percentage", 0),
            "total_mappings": coverage_stats.get("total_mappings", 0),
            "by_type": coverage_stats.get("by_type", {}),
        },
    }


@router.get("/pass-rate")
async def get_pass_rate_trend(
    request: Request,
    project_id: str,
    days: int = 30,
    claims: dict[str, Any] = Depends(auth_guard),
    db: AsyncSession = Depends(get_db),
):
    """Get pass rate trend data for charts."""
    enforce_rate_limit(request, claims)
    ensure_project_access(project_id, claims)

    from tracertm.models.test_run import TestRun

    cutoff_date = datetime.now(UTC) - timedelta(days=days)

    result = await db.execute(
        select(
            func.date(TestRun.completed_at).label("date"),
            func.count().label("total_runs"),
            func.avg(TestRun.pass_rate).label("avg_pass_rate"),
            func.sum(TestRun.passed_count).label("total_passed"),
            func.sum(TestRun.failed_count).label("total_failed"),
        )
        .where(
            and_(
                TestRun.project_id == project_id,
                TestRun.completed_at >= cutoff_date,
                TestRun.completed_at.isnot(None),
            ),
        )
        .group_by(func.date(TestRun.completed_at))
        .order_by(func.date(TestRun.completed_at)),
    )

    rows = result.all()

    return {
        "project_id": project_id,
        "days": days,
        "trend": [
            {
                "date": str(row.date) if row.date else None,
                "total_runs": row.total_runs or 0,
                "avg_pass_rate": round(float(row.avg_pass_rate or 0), 2),
                "total_passed": row.total_passed or 0,
                "total_failed": row.total_failed or 0,
            }
            for row in rows
        ],
    }


@router.get("/coverage")
async def get_coverage_metrics(
    request: Request,
    project_id: str,
    claims: Annotated[dict[str, Any], Depends(auth_guard)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Get detailed coverage metrics."""
    enforce_rate_limit(request, claims)
    ensure_project_access(project_id, claims)

    from tracertm.repositories.test_coverage_repository import TestCoverageRepository

    repo = TestCoverageRepository(db)

    matrix = await repo.get_traceability_matrix(project_id)
    gaps = await repo.get_coverage_gaps(project_id)
    stats = await repo.get_stats(project_id)

    coverage_by_view = {}
    for item in matrix.get("matrix", []):
        view = item.get("requirement_view", "Unknown")
        if view not in coverage_by_view:
            coverage_by_view[view] = {"total": 0, "covered": 0, "percentage": 0.0}
        coverage_by_view[view]["total"] += 1
        if item.get("is_covered"):
            coverage_by_view[view]["covered"] += 1

    for view_stats in coverage_by_view.values():
        total = view_stats["total"]
        covered = view_stats["covered"]
        view_stats["percentage"] = round(covered / total * 100, 1) if total > 0 else 0.0

    return {
        "project_id": project_id,
        "overall": {
            "total_requirements": matrix.get("total_requirements", 0),
            "covered_requirements": matrix.get("covered_requirements", 0),
            "coverage_percentage": matrix.get("coverage_percentage", 0),
        },
        "by_view": coverage_by_view,
        "by_type": stats.get("by_type", {}),
        "gaps_count": gaps.get("uncovered_count", 0),
        "high_priority_gaps": len([g for g in gaps.get("gaps", []) if g.get("priority") in {"high", "critical"}]),
    }


@router.get("/defect-density")
async def get_defect_density(
    request: Request,
    project_id: str,
    claims: Annotated[dict[str, Any], Depends(auth_guard)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Get defect density metrics (failed tests per test case)."""
    enforce_rate_limit(request, claims)
    ensure_project_access(project_id, claims)

    from tracertm.models.test_run import TestResult, TestRun

    result = await db.execute(
        select(
            TestResult.test_case_id,
            func.count().label("total_executions"),
            func.sum(func.case((TestResult.status == "failed", 1), else_=0)).label("failure_count"),
        )
        .join(TestRun, TestRun.id == TestResult.run_id)
        .where(TestRun.project_id == project_id)
        .group_by(TestResult.test_case_id),
    )

    rows = result.all()

    test_cases_with_failures = []
    total_executions = 0
    total_failures = 0

    for row in rows:
        total_executions += row.total_executions or 0
        failures = row.failure_count or 0
        total_failures += failures

        if failures > 0:
            failure_rate = round(failures / (row.total_executions or 1) * 100, 2)
            test_cases_with_failures.append({
                "test_case_id": row.test_case_id,
                "total_executions": row.total_executions,
                "failure_count": failures,
                "failure_rate": failure_rate,
            })

    test_cases_with_failures.sort(key=operator.itemgetter("failure_count"), reverse=True)

    return {
        "project_id": project_id,
        "overall_defect_density": (round(total_failures / total_executions * 100, 2) if total_executions > 0 else 0),
        "total_executions": total_executions,
        "total_failures": total_failures,
        "test_cases_with_failures": len(test_cases_with_failures),
        "top_failing_tests": test_cases_with_failures[:10],
    }


@router.get("/flaky-tests")
async def get_flaky_tests(
    request: Request,
    project_id: str,
    claims: Annotated[dict[str, Any], Depends(auth_guard)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Get flaky test analysis."""
    enforce_rate_limit(request, claims)
    ensure_project_access(project_id, claims)

    from tracertm.models.test_run import TestResult, TestRun

    flaky_result = await db.execute(
        select(
            TestResult.test_case_id,
            func.count().label("flaky_count"),
        )
        .join(TestRun, TestRun.id == TestResult.run_id)
        .where(
            and_(
                TestRun.project_id == project_id,
                TestResult.is_flaky.is_(True),
            ),
        )
        .group_by(TestResult.test_case_id)
        .order_by(func.count().desc()),
    )

    flaky_tests = [
        {
            "test_case_id": row.test_case_id,
            "flaky_occurrences": row.flaky_count,
        }
        for row in flaky_result.all()
    ]

    inconsistent_result = await db.execute(
        select(
            TestResult.test_case_id,
            func.date(TestResult.completed_at).label("date"),
            func.count(func.distinct(TestResult.status)).label("status_count"),
        )
        .join(TestRun, TestRun.id == TestResult.run_id)
        .where(
            and_(
                TestRun.project_id == project_id,
                TestResult.completed_at.isnot(None),
            ),
        )
        .group_by(TestResult.test_case_id, func.date(TestResult.completed_at))
        .having(func.count(func.distinct(TestResult.status)) > 1),
    )

    inconsistent_days = {}
    for row in inconsistent_result.all():
        tc_id = row.test_case_id
        if tc_id not in inconsistent_days:
            inconsistent_days[tc_id] = 0
        inconsistent_days[tc_id] += 1

    potentially_flaky = [
        {
            "test_case_id": tc_id,
            "inconsistent_days": count,
        }
        for tc_id, count in sorted(inconsistent_days.items(), key=operator.itemgetter(1), reverse=True)
    ][:20]

    return {
        "project_id": project_id,
        "marked_flaky": flaky_tests[:20],
        "marked_flaky_count": len(flaky_tests),
        "potentially_flaky": potentially_flaky,
        "potentially_flaky_count": len(inconsistent_days),
    }


@router.get("/execution-history")
async def get_execution_history(
    request: Request,
    project_id: str,
    days: int = 7,
    claims: dict[str, Any] = Depends(auth_guard),
    db: AsyncSession = Depends(get_db),
):
    """Get recent test execution history."""
    enforce_rate_limit(request, claims)
    ensure_project_access(project_id, claims)

    from tracertm.models.test_run import TestRun

    cutoff_date = datetime.now(UTC) - timedelta(days=days)

    result = await db.execute(
        select(TestRun)
        .where(
            and_(
                TestRun.project_id == project_id,
                TestRun.created_at >= cutoff_date,
            ),
        )
        .order_by(TestRun.created_at.desc())
        .limit(50),
    )

    runs = result.scalars().all()

    return {
        "project_id": project_id,
        "days": days,
        "runs": [
            {
                "id": run.id,
                "run_number": run.run_number,
                "name": run.name,
                "status": run.status.value if hasattr(run.status, "value") else run.status,
                "run_type": run.run_type.value if hasattr(run.run_type, "value") else run.run_type,
                "environment": run.environment,
                "build_number": run.build_number,
                "branch": run.branch,
                "started_at": run.started_at.isoformat() if run.started_at else None,
                "completed_at": run.completed_at.isoformat() if run.completed_at else None,
                "duration_seconds": run.duration_seconds,
                "total_tests": run.total_tests,
                "passed_count": run.passed_count,
                "failed_count": run.failed_count,
                "pass_rate": run.pass_rate,
            }
            for run in runs
        ],
    }
