"""Repository for Test Coverage operations."""

import uuid
from datetime import UTC, datetime
from typing import Any

from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from tracertm.models.item import Item
from tracertm.models.test_coverage import (
    CoverageActivity,
    CoverageStatus,
    CoverageType,
    TestCoverage,
)


class TestCoverageRepository:
    """Repository for test coverage CRUD and traceability operations."""

    def __init__(self, session: AsyncSession) -> None:
        """Initialize repository.

        Args:
            session: SQLAlchemy async session for database operations.
        """
        self.session = session

    async def create(
        self,
        project_id: str,
        test_case_id: str,
        requirement_id: str,
        coverage_type: str = "direct",
        coverage_percentage: int | None = None,
        rationale: str | None = None,
        notes: str | None = None,
        metadata: dict[str, Any] | None = None,
        created_by: str | None = None,
    ) -> TestCoverage:
        """Create a new test coverage mapping."""
        coverage = TestCoverage(
            id=str(uuid.uuid4()),
            project_id=project_id,
            test_case_id=test_case_id,
            requirement_id=requirement_id,
            coverage_type=CoverageType(coverage_type),
            status=CoverageStatus.ACTIVE,
            coverage_percentage=coverage_percentage,
            rationale=rationale,
            notes=notes,
            coverage_metadata=metadata or {},
            created_by=created_by,
        )
        self.session.add(coverage)

        # Log creation activity
        activity = CoverageActivity(
            id=str(uuid.uuid4()),
            coverage_id=coverage.id,
            activity_type="created",
            to_value=coverage_type,
            description="Coverage mapping created",
            performed_by=created_by,
        )
        self.session.add(activity)

        await self.session.flush()
        return coverage

    async def get_by_id(self, coverage_id: str) -> TestCoverage | None:
        """Get a coverage mapping by ID."""
        result = await self.session.execute(
            select(TestCoverage)
            .options(
                selectinload(TestCoverage.test_case),
                selectinload(TestCoverage.requirement),
            )
            .where(TestCoverage.id == coverage_id),
        )
        return result.scalar_one_or_none()

    async def get_by_test_case_and_requirement(
        self,
        test_case_id: str,
        requirement_id: str,
    ) -> TestCoverage | None:
        """Get a coverage mapping by test case and requirement."""
        result = await self.session.execute(
            select(TestCoverage).where(
                and_(
                    TestCoverage.test_case_id == test_case_id,
                    TestCoverage.requirement_id == requirement_id,
                ),
            ),
        )
        return result.scalar_one_or_none()

    async def list_by_project(
        self,
        project_id: str,
        coverage_type: str | None = None,
        status: str | None = None,
        test_case_id: str | None = None,
        requirement_id: str | None = None,
        skip: int = 0,
        limit: int = 100,
    ) -> tuple[list[TestCoverage], int]:
        """List coverage mappings for a project with filtering."""
        query = select(TestCoverage).where(TestCoverage.project_id == project_id)

        if coverage_type:
            try:
                coverage_enum = CoverageType(coverage_type)
            except ValueError:
                return [], 0
            query = query.where(TestCoverage.coverage_type == coverage_enum)
        if status:
            try:
                status_enum = CoverageStatus(status)
            except ValueError:
                return [], 0
            query = query.where(TestCoverage.status == status_enum)
        if test_case_id:
            query = query.where(TestCoverage.test_case_id == test_case_id)
        if requirement_id:
            query = query.where(TestCoverage.requirement_id == requirement_id)

        # Count total
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await self.session.execute(count_query)
        total = total_result.scalar() or 0

        # Apply pagination
        query = query.order_by(TestCoverage.created_at.desc())
        query = query.offset(skip).limit(limit)

        result = await self.session.execute(query)
        coverages = list(result.scalars().all())

        return coverages, total

    async def list_by_test_case(
        self,
        test_case_id: str,
    ) -> list[TestCoverage]:
        """Get all requirements covered by a test case."""
        result = await self.session.execute(
            select(TestCoverage)
            .options(selectinload(TestCoverage.requirement))
            .where(
                and_(
                    TestCoverage.test_case_id == test_case_id,
                    TestCoverage.status == CoverageStatus.ACTIVE,
                ),
            ),
        )
        return list(result.scalars().all())

    async def list_by_requirement(
        self,
        requirement_id: str,
    ) -> list[TestCoverage]:
        """Get all test cases covering a requirement."""
        result = await self.session.execute(
            select(TestCoverage)
            .options(selectinload(TestCoverage.test_case))
            .where(
                and_(
                    TestCoverage.requirement_id == requirement_id,
                    TestCoverage.status == CoverageStatus.ACTIVE,
                ),
            ),
        )
        return list(result.scalars().all())

    async def update(
        self,
        coverage_id: str,
        _updated_by: str | None = None,
        **updates: Any,
    ) -> TestCoverage | None:
        """Update a coverage mapping."""
        coverage = await self.get_by_id(coverage_id)
        if not coverage:
            return None

        for key, value in updates.items():
            if hasattr(coverage, key) and value is not None:
                setattr(coverage, key, value)

        coverage.version += 1
        await self.session.flush()
        return coverage

    async def verify_coverage(
        self,
        coverage_id: str,
        verified_by: str,
        notes: str | None = None,
    ) -> TestCoverage | None:
        """Mark a coverage mapping as verified."""
        coverage = await self.get_by_id(coverage_id)
        if not coverage:
            return None

        coverage.last_verified_at = datetime.now(UTC)
        coverage.verified_by = verified_by
        if notes:
            coverage.notes = notes
        coverage.version += 1

        # Log activity
        activity = CoverageActivity(
            id=str(uuid.uuid4()),
            coverage_id=coverage_id,
            activity_type="verified",
            description=f"Coverage verified by {verified_by}",
            performed_by=verified_by,
        )
        self.session.add(activity)

        await self.session.flush()
        return coverage

    async def update_test_result(
        self,
        coverage_id: str,
        test_result: str,
        tested_at: datetime | None = None,
    ) -> TestCoverage | None:
        """Update the last test result for a coverage mapping."""
        coverage = await self.get_by_id(coverage_id)
        if not coverage:
            return None

        coverage.last_test_result = test_result
        coverage.last_tested_at = tested_at or datetime.now(UTC)
        coverage.version += 1

        await self.session.flush()
        return coverage

    async def delete(self, coverage_id: str) -> bool:
        """Delete a coverage mapping."""
        coverage = await self.get_by_id(coverage_id)
        if not coverage:
            return False
        await self.session.delete(coverage)
        await self.session.flush()
        return True

    async def get_traceability_matrix(
        self,
        project_id: str,
        requirement_view: str | None = None,
    ) -> dict[str, Any]:
        """Generate a traceability matrix for a project.

        Returns requirements mapped to their covering test cases.
        """
        # Get all requirements (items) for the project
        req_query = select(Item).where(Item.project_id == project_id)
        if requirement_view:
            req_query = req_query.where(Item.view == requirement_view)
        req_result = await self.session.execute(req_query)
        requirements = list(req_result.scalars().all())

        # Get all active coverage mappings
        cov_query = select(TestCoverage).where(
            and_(
                TestCoverage.project_id == project_id,
                TestCoverage.status == CoverageStatus.ACTIVE,
            ),
        )
        cov_result = await self.session.execute(cov_query)
        coverages = list(cov_result.scalars().all())

        # Build mapping
        coverage_map: dict[str, list[dict[str, Any]]] = {}
        for cov in coverages:
            if cov.requirement_id not in coverage_map:
                coverage_map[cov.requirement_id] = []
            coverage_map[cov.requirement_id].append({
                "test_case_id": cov.test_case_id,
                "coverage_type": cov.coverage_type.value,
                "coverage_percentage": cov.coverage_percentage,
                "last_test_result": cov.last_test_result,
                "last_tested_at": cov.last_tested_at.isoformat() if cov.last_tested_at else None,
            })

        # Build matrix
        matrix = []
        covered_count = 0
        for req in requirements:
            test_cases = coverage_map.get(str(req.id), [])
            is_covered = len(test_cases) > 0
            if is_covered:
                covered_count += 1

            # Determine overall status based on test results
            overall_status = "not_tested"
            if test_cases:
                results = [tc.get("last_test_result") for tc in test_cases if tc.get("last_test_result")]
                if results:
                    if all(r == "passed" for r in results):
                        overall_status = "passed"
                    elif any(r == "failed" for r in results):
                        overall_status = "failed"
                    else:
                        overall_status = "partial"
                else:
                    overall_status = "pending"

            matrix.append({
                "requirement_id": req.id,
                "requirement_title": req.title,
                "requirement_view": req.view,
                "requirement_status": req.status,
                "is_covered": is_covered,
                "test_count": len(test_cases),
                "test_cases": test_cases,
                "overall_status": overall_status,
            })

        total_requirements = len(requirements)
        coverage_percentage = (covered_count / total_requirements * 100) if total_requirements > 0 else 0

        return {
            "project_id": project_id,
            "total_requirements": total_requirements,
            "covered_requirements": covered_count,
            "uncovered_requirements": total_requirements - covered_count,
            "coverage_percentage": round(coverage_percentage, 2),
            "matrix": matrix,
        }

    async def get_coverage_gaps(
        self,
        project_id: str,
        requirement_view: str | None = None,
    ) -> dict[str, Any]:
        """Find requirements that have no test coverage."""
        # Get all requirements
        req_query = select(Item).where(Item.project_id == project_id)
        if requirement_view:
            req_query = req_query.where(Item.view == requirement_view)
        req_result = await self.session.execute(req_query)
        requirements = list(req_result.scalars().all())

        # Get all covered requirement IDs
        cov_query = (
            select(TestCoverage.requirement_id)
            .where(
                and_(
                    TestCoverage.project_id == project_id,
                    TestCoverage.status == CoverageStatus.ACTIVE,
                ),
            )
            .distinct()
        )
        cov_result = await self.session.execute(cov_query)
        covered_ids = {row[0] for row in cov_result}

        # Find uncovered
        gaps = [
            {
                "requirement_id": req.id,
                "requirement_title": req.title,
                "requirement_view": req.view,
                "requirement_status": req.status,
                "priority": req.priority,
            }
            for req in requirements
            if req.id not in covered_ids
        ]

        # Sort by priority
        priority_order = {"critical": 0, "high": 1, "medium": 2, "low": 3}
        gaps.sort(key=lambda x: priority_order.get(str(x.get("priority", "low")), 4))

        return {
            "project_id": project_id,
            "total_requirements": len(requirements),
            "uncovered_count": len(gaps),
            "coverage_percentage": round((1 - len(gaps) / len(requirements)) * 100 if requirements else 0, 2),
            "gaps": gaps,
        }

    async def get_test_case_coverage_summary(
        self,
        test_case_id: str,
    ) -> dict[str, Any]:
        """Get coverage summary for a specific test case."""
        coverages = await self.list_by_test_case(test_case_id)

        return {
            "test_case_id": test_case_id,
            "total_requirements_covered": len(coverages),
            "coverage_types": {
                "direct": len([c for c in coverages if c.coverage_type == CoverageType.DIRECT]),
                "partial": len([c for c in coverages if c.coverage_type == CoverageType.PARTIAL]),
                "indirect": len([c for c in coverages if c.coverage_type == CoverageType.INDIRECT]),
                "regression": len([c for c in coverages if c.coverage_type == CoverageType.REGRESSION]),
            },
            "requirements": [
                {
                    "requirement_id": c.requirement_id,
                    "requirement_title": c.requirement.title if c.requirement else None,
                    "coverage_type": c.coverage_type.value,
                    "coverage_percentage": c.coverage_percentage,
                }
                for c in coverages
            ],
        }

    async def get_stats(self, project_id: str) -> dict[str, Any]:
        """Get coverage statistics for a project."""
        # Total coverage mappings
        total_result = await self.session.execute(select(func.count()).where(TestCoverage.project_id == project_id))
        total = total_result.scalar() or 0

        # By type
        type_result = await self.session.execute(
            select(TestCoverage.coverage_type, func.count())
            .where(TestCoverage.project_id == project_id)
            .group_by(TestCoverage.coverage_type),
        )
        by_type = {str(row[0].value): row[1] for row in type_result}

        # By status
        status_result = await self.session.execute(
            select(TestCoverage.status, func.count())
            .where(TestCoverage.project_id == project_id)
            .group_by(TestCoverage.status),
        )
        by_status = {str(row[0].value): row[1] for row in status_result}

        # Unique test cases and requirements
        unique_tests = await self.session.execute(
            select(func.count(func.distinct(TestCoverage.test_case_id))).where(TestCoverage.project_id == project_id),
        )
        unique_reqs = await self.session.execute(
            select(func.count(func.distinct(TestCoverage.requirement_id))).where(TestCoverage.project_id == project_id),
        )

        return {
            "project_id": project_id,
            "total_mappings": total,
            "by_type": by_type,
            "by_status": by_status,
            "unique_test_cases": unique_tests.scalar() or 0,
            "unique_requirements": unique_reqs.scalar() or 0,
        }

    async def get_activities(
        self,
        coverage_id: str,
        limit: int = 50,
    ) -> list[CoverageActivity]:
        """Get activity log for a coverage mapping."""
        result = await self.session.execute(
            select(CoverageActivity)
            .where(CoverageActivity.coverage_id == coverage_id)
            .order_by(CoverageActivity.created_at.desc())
            .limit(limit),
        )
        return list(result.scalars().all())
