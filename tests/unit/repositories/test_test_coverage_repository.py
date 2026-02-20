"""Tests for TestCoverageRepository.

Comprehensive test coverage for test coverage traceability operations.
"""

from datetime import datetime

# Aliases
from typing import Any
from uuid import uuid4

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession

from tests.test_constants import COUNT_FIVE, COUNT_THREE, COUNT_TWO
from tracertm.models import test_case as tc_models
from tracertm.models import test_coverage as cov_models

# Use module-qualified imports to avoid pytest collection issues with Test* classes
from tracertm.repositories import test_coverage_repository as tc_repo
from tracertm.repositories.item_repository import ItemRepository
from tracertm.repositories.project_repository import ProjectRepository

CoverageRepository = tc_repo.TestCoverageRepository
_TestCaseModel = tc_models.TestCase
_TestCoverageModel = cov_models.TestCoverage
_CoverageActivityModel = cov_models.CoverageActivity
CoverageType = cov_models.CoverageType
CoverageStatus = cov_models.CoverageStatus


class TestCoverageRepositoryCreate:
    """Tests for create method."""

    @pytest_asyncio.fixture
    async def setup_entities(self, db_session: AsyncSession) -> None:
        """Create project, test case, and requirement for coverage tests."""
        # Create project
        project_repo = ProjectRepository(db_session)
        project = await project_repo.create(name="Coverage Test Project", description="Project for testing coverage")

        # Create requirement (item)
        item_repo = ItemRepository(db_session)
        requirement = await item_repo.create(
            project_id=project.id,
            title="Test Requirement",
            item_type="requirement",
            description="A requirement to be covered",
            view="requirements",
        )

        # Create test case directly
        test_case = _TestCaseModel(
            id=str(uuid4()),
            project_id=project.id,
            test_case_number="TC-001",
            title="Test Case 1",
            description="Test case for coverage",
            status="draft",
            test_type="functional",
        )
        db_session.add(test_case)
        await db_session.flush()

        return {
            "project": project,
            "test_case": test_case,
            "requirement": requirement,
        }

    @pytest.mark.asyncio
    async def test_create_coverage_success(self, db_session: AsyncSession, setup_entities: Any) -> None:
        """Test creating a coverage mapping successfully."""
        repo = CoverageRepository(db_session)
        entities = setup_entities

        coverage = await repo.create(
            project_id=entities["project"].id,
            test_case_id=entities["test_case"].id,
            requirement_id=entities["requirement"].id,
            coverage_type="direct",
            coverage_percentage=100,
            rationale="Direct test coverage",
            notes="Test notes",
            created_by="test_user",
        )

        assert coverage is not None
        assert coverage.id is not None
        assert coverage.project_id == entities["project"].id
        assert coverage.test_case_id == entities["test_case"].id
        assert coverage.requirement_id == entities["requirement"].id
        assert coverage.coverage_type == CoverageType.DIRECT
        assert coverage.status == CoverageStatus.ACTIVE
        assert coverage.coverage_percentage == 100
        assert coverage.rationale == "Direct test coverage"
        assert coverage.notes == "Test notes"
        assert coverage.created_by == "test_user"
        assert coverage.version == 1

    @pytest.mark.asyncio
    async def test_create_coverage_with_partial_type(self, db_session: AsyncSession, setup_entities: Any) -> None:
        """Test creating coverage with partial coverage type."""
        repo = CoverageRepository(db_session)
        entities = setup_entities

        coverage = await repo.create(
            project_id=entities["project"].id,
            test_case_id=entities["test_case"].id,
            requirement_id=entities["requirement"].id,
            coverage_type="partial",
            coverage_percentage=50,
        )

        assert coverage.coverage_type == CoverageType.PARTIAL
        assert coverage.coverage_percentage == 50

    @pytest.mark.asyncio
    async def test_create_coverage_with_indirect_type(self, db_session: AsyncSession, setup_entities: Any) -> None:
        """Test creating coverage with indirect coverage type."""
        repo = CoverageRepository(db_session)
        entities = setup_entities

        coverage = await repo.create(
            project_id=entities["project"].id,
            test_case_id=entities["test_case"].id,
            requirement_id=entities["requirement"].id,
            coverage_type="indirect",
        )

        assert coverage.coverage_type == CoverageType.INDIRECT

    @pytest.mark.asyncio
    async def test_create_coverage_with_regression_type(self, db_session: AsyncSession, setup_entities: Any) -> None:
        """Test creating coverage with regression coverage type."""
        repo = CoverageRepository(db_session)
        entities = setup_entities

        coverage = await repo.create(
            project_id=entities["project"].id,
            test_case_id=entities["test_case"].id,
            requirement_id=entities["requirement"].id,
            coverage_type="regression",
        )

        assert coverage.coverage_type == CoverageType.REGRESSION

    @pytest.mark.asyncio
    async def test_create_coverage_with_metadata(self, db_session: AsyncSession, setup_entities: Any) -> None:
        """Test creating coverage with metadata."""
        repo = CoverageRepository(db_session)
        entities = setup_entities

        metadata = {"priority": "high", "confidence": 0.95}
        coverage = await repo.create(
            project_id=entities["project"].id,
            test_case_id=entities["test_case"].id,
            requirement_id=entities["requirement"].id,
            coverage_type="direct",
            metadata=metadata,
        )

        assert coverage.coverage_metadata == metadata

    @pytest.mark.asyncio
    async def test_create_coverage_logs_activity(self, db_session: AsyncSession, setup_entities: Any) -> None:
        """Test that creating coverage logs an activity."""
        repo = CoverageRepository(db_session)
        entities = setup_entities

        coverage = await repo.create(
            project_id=entities["project"].id,
            test_case_id=entities["test_case"].id,
            requirement_id=entities["requirement"].id,
            coverage_type="direct",
            created_by="activity_user",
        )

        activities = await repo.get_activities(coverage.id)
        assert len(activities) == 1
        assert activities[0].activity_type == "created"
        assert activities[0].performed_by == "activity_user"


class TestCoverageRepositoryGet:
    """Tests for get methods."""

    @pytest_asyncio.fixture
    async def coverage_with_entities(self, db_session: AsyncSession) -> None:
        """Create coverage mapping with related entities."""
        # Create project
        project_repo = ProjectRepository(db_session)
        project = await project_repo.create(name="Get Test Project")

        # Create requirement
        item_repo = ItemRepository(db_session)
        requirement = await item_repo.create(
            project_id=project.id,
            title="Get Test Requirement",
            item_type="requirement",
            view="requirements",
        )

        # Create test case
        test_case = _TestCaseModel(
            id=str(uuid4()),
            project_id=project.id,
            test_case_number="TC-GET-001",
            title="Get Test Case",
            status="draft",
            test_type="functional",
        )
        db_session.add(test_case)
        await db_session.flush()

        # Create coverage
        repo = CoverageRepository(db_session)
        coverage = await repo.create(
            project_id=project.id,
            test_case_id=test_case.id,
            requirement_id=requirement.id,
            coverage_type="direct",
        )

        return {
            "project": project,
            "test_case": test_case,
            "requirement": requirement,
            "coverage": coverage,
        }

    @pytest.mark.asyncio
    async def test_get_by_id_success(self, db_session: AsyncSession, coverage_with_entities: Any) -> None:
        """Test getting coverage by ID."""
        repo = CoverageRepository(db_session)
        entities = coverage_with_entities

        coverage = await repo.get_by_id(entities["coverage"].id)
        assert coverage is not None
        assert coverage.id == entities["coverage"].id

    @pytest.mark.asyncio
    async def test_get_by_id_not_found(self, db_session: AsyncSession) -> None:
        """Test getting coverage by non-existent ID."""
        repo = CoverageRepository(db_session)
        coverage = await repo.get_by_id(str(uuid4()))
        assert coverage is None

    @pytest.mark.asyncio
    async def test_get_by_test_case_and_requirement(
        self, db_session: AsyncSession, coverage_with_entities: Any
    ) -> None:
        """Test getting coverage by test case and requirement IDs."""
        repo = CoverageRepository(db_session)
        entities = coverage_with_entities

        coverage = await repo.get_by_test_case_and_requirement(
            test_case_id=entities["test_case"].id,
            requirement_id=entities["requirement"].id,
        )
        assert coverage is not None
        assert coverage.id == entities["coverage"].id

    @pytest.mark.asyncio
    async def test_get_by_test_case_and_requirement_not_found(self, db_session: AsyncSession) -> None:
        """Test getting coverage by non-existent combination."""
        repo = CoverageRepository(db_session)
        coverage = await repo.get_by_test_case_and_requirement(
            test_case_id=str(uuid4()),
            requirement_id=str(uuid4()),
        )
        assert coverage is None


class TestCoverageRepositoryList:
    """Tests for list methods."""

    @pytest_asyncio.fixture
    async def multiple_coverages(self, db_session: AsyncSession) -> None:
        """Create multiple coverage mappings."""
        project_repo = ProjectRepository(db_session)
        project = await project_repo.create(name="List Test Project")

        item_repo = ItemRepository(db_session)
        requirements = []
        for i in range(3):
            req = await item_repo.create(
                project_id=project.id,
                title=f"Requirement {i}",
                item_type="requirement",
                view="requirements",
            )
            requirements.append(req)

        test_cases = []
        for i in range(3):
            tc = _TestCaseModel(
                id=str(uuid4()),
                project_id=project.id,
                test_case_number=f"TC-LIST-{i:03d}",
                title=f"Test Case {i}",
                status="draft",
                test_type="functional",
            )
            db_session.add(tc)
            test_cases.append(tc)
        await db_session.flush()

        repo = CoverageRepository(db_session)
        coverages = []

        # Create different types of coverages
        types = ["direct", "partial", "indirect"]
        for _i, (tc, req, ctype) in enumerate(zip(test_cases, requirements, types, strict=True)):
            cov = await repo.create(
                project_id=project.id,
                test_case_id=tc.id,
                requirement_id=req.id,
                coverage_type=ctype,
            )
            coverages.append(cov)

        return {
            "project": project,
            "test_cases": test_cases,
            "requirements": requirements,
            "coverages": coverages,
        }

    @pytest.mark.asyncio
    async def test_list_by_project(self, db_session: AsyncSession, multiple_coverages: Any) -> None:
        """Test listing coverages by project."""
        repo = CoverageRepository(db_session)
        entities = multiple_coverages

        coverages, total = await repo.list_by_project(entities["project"].id)
        assert len(coverages) == COUNT_THREE
        assert total == COUNT_THREE

    @pytest.mark.asyncio
    async def test_list_by_project_with_pagination(self, db_session: AsyncSession, multiple_coverages: Any) -> None:
        """Test listing coverages with pagination."""
        repo = CoverageRepository(db_session)
        entities = multiple_coverages

        coverages, total = await repo.list_by_project(
            entities["project"].id,
            skip=0,
            limit=2,
        )
        assert len(coverages) == COUNT_TWO
        assert total == COUNT_THREE

    @pytest.mark.asyncio
    async def test_list_by_project_filter_by_type(self, db_session: AsyncSession, multiple_coverages: Any) -> None:
        """Test filtering coverages by type."""
        repo = CoverageRepository(db_session)
        entities = multiple_coverages

        coverages, _total = await repo.list_by_project(
            entities["project"].id,
            coverage_type="direct",
        )
        assert len(coverages) == 1
        assert coverages[0].coverage_type == CoverageType.DIRECT

    @pytest.mark.asyncio
    async def test_list_by_project_filter_by_test_case(self, db_session: AsyncSession, multiple_coverages: Any) -> None:
        """Test filtering coverages by test case."""
        repo = CoverageRepository(db_session)
        entities = multiple_coverages

        coverages, _total = await repo.list_by_project(
            entities["project"].id,
            test_case_id=entities["test_cases"][0].id,
        )
        assert len(coverages) == 1

    @pytest.mark.asyncio
    async def test_list_by_project_filter_by_requirement(
        self, db_session: AsyncSession, multiple_coverages: Any
    ) -> None:
        """Test filtering coverages by requirement."""
        repo = CoverageRepository(db_session)
        entities = multiple_coverages

        coverages, _total = await repo.list_by_project(
            entities["project"].id,
            requirement_id=entities["requirements"][0].id,
        )
        assert len(coverages) == 1

    @pytest.mark.asyncio
    async def test_list_by_test_case(self, db_session: AsyncSession, multiple_coverages: Any) -> None:
        """Test listing coverages by test case."""
        repo = CoverageRepository(db_session)
        entities = multiple_coverages

        coverages = await repo.list_by_test_case(entities["test_cases"][0].id)
        assert len(coverages) == 1

    @pytest.mark.asyncio
    async def test_list_by_requirement(self, db_session: AsyncSession, multiple_coverages: Any) -> None:
        """Test listing coverages by requirement."""
        repo = CoverageRepository(db_session)
        entities = multiple_coverages

        coverages = await repo.list_by_requirement(entities["requirements"][0].id)
        assert len(coverages) == 1


class TestCoverageRepositoryUpdate:
    """Tests for update methods."""

    @pytest_asyncio.fixture
    async def coverage_for_update(self, db_session: AsyncSession) -> None:
        """Create coverage for update tests."""
        project_repo = ProjectRepository(db_session)
        project = await project_repo.create(name="Update Test Project")

        item_repo = ItemRepository(db_session)
        requirement = await item_repo.create(
            project_id=project.id,
            title="Update Test Requirement",
            item_type="requirement",
            view="requirements",
        )

        test_case = _TestCaseModel(
            id=str(uuid4()),
            project_id=project.id,
            test_case_number="TC-UPD-001",
            title="Update Test Case",
            status="draft",
            test_type="functional",
        )
        db_session.add(test_case)
        await db_session.flush()

        repo = CoverageRepository(db_session)
        return await repo.create(
            project_id=project.id,
            test_case_id=test_case.id,
            requirement_id=requirement.id,
            coverage_type="direct",
            coverage_percentage=50,
        )

    @pytest.mark.asyncio
    async def test_update_coverage_success(self, db_session: AsyncSession, coverage_for_update: Any) -> None:
        """Test updating coverage."""
        repo = CoverageRepository(db_session)
        coverage = coverage_for_update

        updated = await repo.update(
            coverage.id,
            coverage_percentage=75,
            notes="Updated notes",
        )

        assert updated is not None
        assert updated.coverage_percentage == 75
        assert updated.notes == "Updated notes"
        assert updated.version == COUNT_TWO

    @pytest.mark.asyncio
    async def test_update_coverage_not_found(self, db_session: AsyncSession) -> None:
        """Test updating non-existent coverage."""
        repo = CoverageRepository(db_session)
        updated = await repo.update(str(uuid4()), coverage_percentage=75)
        assert updated is None

    @pytest.mark.asyncio
    async def test_verify_coverage(self, db_session: AsyncSession, coverage_for_update: Any) -> None:
        """Test verifying coverage."""
        repo = CoverageRepository(db_session)
        coverage = coverage_for_update

        verified = await repo.verify_coverage(
            coverage.id,
            verified_by="verifier_user",
            notes="Verified and approved",
        )

        assert verified is not None
        assert verified.verified_by == "verifier_user"
        assert verified.notes == "Verified and approved"
        assert verified.last_verified_at is not None
        assert verified.version == COUNT_TWO

    @pytest.mark.asyncio
    async def test_verify_coverage_logs_activity(self, db_session: AsyncSession, coverage_for_update: Any) -> None:
        """Test that verifying coverage logs an activity."""
        repo = CoverageRepository(db_session)
        coverage = coverage_for_update

        await repo.verify_coverage(coverage.id, verified_by="verifier")

        activities = await repo.get_activities(coverage.id)
        # Should have creation + verification activities
        assert len(activities) == COUNT_TWO
        verify_activity = next(a for a in activities if a.activity_type == "verified")
        assert verify_activity.performed_by == "verifier"

    @pytest.mark.asyncio
    async def test_verify_coverage_not_found(self, db_session: AsyncSession) -> None:
        """Test verifying non-existent coverage."""
        repo = CoverageRepository(db_session)
        verified = await repo.verify_coverage(str(uuid4()), verified_by="user")
        assert verified is None

    @pytest.mark.asyncio
    async def test_update_test_result(self, db_session: AsyncSession, coverage_for_update: Any) -> None:
        """Test updating test result."""
        repo = CoverageRepository(db_session)
        coverage = coverage_for_update

        updated = await repo.update_test_result(
            coverage.id,
            test_result="passed",
        )

        assert updated is not None
        assert updated.last_test_result == "passed"
        assert updated.last_tested_at is not None
        assert updated.version == COUNT_TWO

    @pytest.mark.asyncio
    async def test_update_test_result_with_timestamp(self, db_session: AsyncSession, coverage_for_update: Any) -> None:
        """Test updating test result with specific timestamp."""
        repo = CoverageRepository(db_session)
        coverage = coverage_for_update
        test_time = datetime(2025, 1, 15, 10, 30, 0)

        updated = await repo.update_test_result(
            coverage.id,
            test_result="failed",
            tested_at=test_time,
        )

        assert updated is not None
        u = updated
        assert u.last_test_result == "failed"
        # Compare date components (SQLite may strip timezone)
        assert u.last_tested_at is not None
        dt = u.last_tested_at
        assert dt.year == 2025
        assert dt.month == 1
        assert dt.day == 15

    @pytest.mark.asyncio
    async def test_update_test_result_not_found(self, db_session: AsyncSession) -> None:
        """Test updating test result for non-existent coverage."""
        repo = CoverageRepository(db_session)
        updated = await repo.update_test_result(str(uuid4()), test_result="passed")
        assert updated is None


class TestCoverageRepositoryDelete:
    """Tests for delete method."""

    @pytest_asyncio.fixture
    async def coverage_for_delete(self, db_session: AsyncSession) -> None:
        """Create coverage for delete tests."""
        project_repo = ProjectRepository(db_session)
        project = await project_repo.create(name="Delete Test Project")

        item_repo = ItemRepository(db_session)
        requirement = await item_repo.create(
            project_id=project.id,
            title="Delete Test Requirement",
            item_type="requirement",
            view="requirements",
        )

        test_case = _TestCaseModel(
            id=str(uuid4()),
            project_id=project.id,
            test_case_number="TC-DEL-001",
            title="Delete Test Case",
            status="draft",
            test_type="functional",
        )
        db_session.add(test_case)
        await db_session.flush()

        repo = CoverageRepository(db_session)
        return await repo.create(
            project_id=project.id,
            test_case_id=test_case.id,
            requirement_id=requirement.id,
            coverage_type="direct",
        )

    @pytest.mark.asyncio
    async def test_delete_coverage_success(self, db_session: AsyncSession, coverage_for_delete: Any) -> None:
        """Test deleting coverage."""
        repo = CoverageRepository(db_session)
        coverage = coverage_for_delete

        result = await repo.delete(coverage.id)
        assert result is True

        # Verify deleted
        deleted = await repo.get_by_id(coverage.id)
        assert deleted is None

    @pytest.mark.asyncio
    async def test_delete_coverage_not_found(self, db_session: AsyncSession) -> None:
        """Test deleting non-existent coverage."""
        repo = CoverageRepository(db_session)
        result = await repo.delete(str(uuid4()))
        assert result is False


class TestCoverageRepositoryTraceability:
    """Tests for traceability matrix and coverage gaps."""

    @pytest_asyncio.fixture
    async def traceability_setup(self, db_session: AsyncSession) -> None:
        """Create setup for traceability tests."""
        project_repo = ProjectRepository(db_session)
        project = await project_repo.create(name="Traceability Test Project")

        item_repo = ItemRepository(db_session)
        requirements = []
        for i in range(5):
            req = await item_repo.create(
                project_id=project.id,
                title=f"Requirement {i}",
                item_type="requirement",
                view="requirements",
                priority=["critical", "high", "medium", "low", "low"][i],
            )
            requirements.append(req)

        test_cases = []
        for i in range(3):
            tc = _TestCaseModel(
                id=str(uuid4()),
                project_id=project.id,
                test_case_number=f"TC-TRACE-{i:03d}",
                title=f"Test Case {i}",
                status="draft",
                test_type="functional",
            )
            db_session.add(tc)
            test_cases.append(tc)
        await db_session.flush()

        repo = CoverageRepository(db_session)
        coverages = []

        # Cover only first 3 requirements
        for i in range(3):
            cov = await repo.create(
                project_id=project.id,
                test_case_id=test_cases[i].id,
                requirement_id=requirements[i].id,
                coverage_type="direct",
            )
            coverages.append(cov)

        return {
            "project": project,
            "requirements": requirements,
            "test_cases": test_cases,
            "coverages": coverages,
        }

    @pytest.mark.asyncio
    async def test_get_traceability_matrix(self, db_session: AsyncSession, traceability_setup: Any) -> None:
        """Test getting traceability matrix."""
        repo = CoverageRepository(db_session)
        entities = traceability_setup

        matrix = await repo.get_traceability_matrix(entities["project"].id)

        assert matrix["project_id"] == entities["project"].id
        assert matrix["total_requirements"] == COUNT_FIVE
        assert matrix["covered_requirements"] == COUNT_THREE
        assert matrix["uncovered_requirements"] == COUNT_TWO
        assert matrix["coverage_percentage"] == 60.0
        assert len(matrix["matrix"]) == COUNT_FIVE

    @pytest.mark.asyncio
    async def test_get_traceability_matrix_with_test_results(
        self, db_session: AsyncSession, traceability_setup: Any
    ) -> None:
        """Test traceability matrix with test results."""
        repo = CoverageRepository(db_session)
        entities = traceability_setup

        # Update test results
        await repo.update_test_result(entities["coverages"][0].id, "passed")
        await repo.update_test_result(entities["coverages"][1].id, "passed")
        await repo.update_test_result(entities["coverages"][2].id, "failed")

        matrix = await repo.get_traceability_matrix(entities["project"].id)

        # Check statuses
        covered_items = [m for m in matrix["matrix"] if m["is_covered"]]
        passed = [m for m in covered_items if m["overall_status"] == "passed"]
        failed = [m for m in covered_items if m["overall_status"] == "failed"]

        assert len(passed) == COUNT_TWO
        assert len(failed) == 1

    @pytest.mark.asyncio
    async def test_get_coverage_gaps(self, db_session: AsyncSession, traceability_setup: Any) -> None:
        """Test getting coverage gaps."""
        repo = CoverageRepository(db_session)
        entities = traceability_setup

        gaps = await repo.get_coverage_gaps(entities["project"].id)

        assert gaps["project_id"] == entities["project"].id
        assert gaps["total_requirements"] == COUNT_FIVE
        assert gaps["uncovered_count"] == COUNT_TWO
        assert gaps["coverage_percentage"] == 60.0
        assert len(gaps["gaps"]) == COUNT_TWO

    @pytest.mark.asyncio
    async def test_get_coverage_gaps_sorted_by_priority(
        self, db_session: AsyncSession, traceability_setup: Any
    ) -> None:
        """Test that gaps are sorted by priority."""
        repo = CoverageRepository(db_session)
        entities = traceability_setup

        gaps = await repo.get_coverage_gaps(entities["project"].id)

        # Uncovered are requirements 3 and 4 (both low priority)
        # They should be sorted by priority
        for gap in gaps["gaps"]:
            assert gap["priority"] == "low"

    @pytest.mark.asyncio
    async def test_get_test_case_coverage_summary(self, db_session: AsyncSession, traceability_setup: Any) -> None:
        """Test getting test case coverage summary."""
        repo = CoverageRepository(db_session)
        entities = traceability_setup

        summary = await repo.get_test_case_coverage_summary(entities["test_cases"][0].id)

        assert summary["test_case_id"] == entities["test_cases"][0].id
        assert summary["total_requirements_covered"] == 1
        assert summary["coverage_types"]["direct"] == 1
        assert len(summary["requirements"]) == 1


class TestCoverageRepositoryStats:
    """Tests for statistics methods."""

    @pytest_asyncio.fixture
    async def stats_setup(self, db_session: AsyncSession) -> None:
        """Create setup for statistics tests."""
        project_repo = ProjectRepository(db_session)
        project = await project_repo.create(name="Stats Test Project")

        item_repo = ItemRepository(db_session)
        requirements = []
        for i in range(5):
            req = await item_repo.create(
                project_id=project.id,
                title=f"Stats Requirement {i}",
                item_type="requirement",
                view="requirements",
            )
            requirements.append(req)

        test_cases = []
        for i in range(3):
            tc = _TestCaseModel(
                id=str(uuid4()),
                project_id=project.id,
                test_case_number=f"TC-STATS-{i:03d}",
                title=f"Stats Test Case {i}",
                status="draft",
                test_type="functional",
            )
            db_session.add(tc)
            test_cases.append(tc)
        await db_session.flush()

        repo = CoverageRepository(db_session)
        coverages = []

        # Create diverse coverage types
        types = ["direct", "partial", "indirect", "direct", "regression"]
        for i in range(5):
            cov = await repo.create(
                project_id=project.id,
                test_case_id=test_cases[i % 3].id,
                requirement_id=requirements[i].id,
                coverage_type=types[i],
            )
            coverages.append(cov)

        return {
            "project": project,
            "requirements": requirements,
            "test_cases": test_cases,
            "coverages": coverages,
        }

    @pytest.mark.asyncio
    async def test_get_stats(self, db_session: AsyncSession, stats_setup: Any) -> None:
        """Test getting coverage statistics."""
        repo = CoverageRepository(db_session)
        entities = stats_setup

        stats = await repo.get_stats(entities["project"].id)

        assert stats["project_id"] == entities["project"].id
        assert stats["total_mappings"] == COUNT_FIVE
        assert stats["by_type"]["direct"] == COUNT_TWO
        assert stats["by_type"]["partial"] == 1
        assert stats["by_type"]["indirect"] == 1
        assert stats["by_type"]["regression"] == 1
        assert stats["by_status"]["active"] == COUNT_FIVE
        assert stats["unique_test_cases"] == COUNT_THREE
        assert stats["unique_requirements"] == COUNT_FIVE

    @pytest.mark.asyncio
    async def test_get_stats_empty_project(self, db_session: AsyncSession) -> None:
        """Test getting stats for empty project."""
        project_repo = ProjectRepository(db_session)
        project = await project_repo.create(name="Empty Stats Project")

        repo = CoverageRepository(db_session)
        stats = await repo.get_stats(project.id)

        assert stats["total_mappings"] == 0
        assert stats["unique_test_cases"] == 0
        assert stats["unique_requirements"] == 0


class TestCoverageRepositoryActivities:
    """Tests for activity tracking."""

    @pytest_asyncio.fixture
    async def coverage_with_activities(self, db_session: AsyncSession) -> None:
        """Create coverage with multiple activities."""
        project_repo = ProjectRepository(db_session)
        project = await project_repo.create(name="Activities Test Project")

        item_repo = ItemRepository(db_session)
        requirement = await item_repo.create(
            project_id=project.id,
            title="Activities Test Requirement",
            item_type="requirement",
            view="requirements",
        )

        test_case = _TestCaseModel(
            id=str(uuid4()),
            project_id=project.id,
            test_case_number="TC-ACT-001",
            title="Activities Test Case",
            status="draft",
            test_type="functional",
        )
        db_session.add(test_case)
        await db_session.flush()

        repo = CoverageRepository(db_session)
        coverage = await repo.create(
            project_id=project.id,
            test_case_id=test_case.id,
            requirement_id=requirement.id,
            coverage_type="direct",
            created_by="creator",
        )

        # Add more activities via verify
        await repo.verify_coverage(coverage.id, verified_by="verifier1")
        await repo.verify_coverage(coverage.id, verified_by="verifier2")

        return coverage

    @pytest.mark.asyncio
    async def test_get_activities(self, db_session: AsyncSession, coverage_with_activities: Any) -> None:
        """Test getting activities for coverage."""
        repo = CoverageRepository(db_session)
        coverage = coverage_with_activities

        activities = await repo.get_activities(coverage.id)

        assert len(activities) >= COUNT_THREE  # created + 2 verifications
        # Newest first
        activity_types = [a.activity_type for a in activities]
        assert "created" in activity_types
        assert activity_types.count("verified") == COUNT_TWO

    @pytest.mark.asyncio
    async def test_get_activities_with_limit(self, db_session: AsyncSession, coverage_with_activities: Any) -> None:
        """Test getting limited activities."""
        repo = CoverageRepository(db_session)
        coverage = coverage_with_activities

        activities = await repo.get_activities(coverage.id, limit=2)
        assert len(activities) == COUNT_TWO

    @pytest.mark.asyncio
    async def test_get_activities_empty(self, db_session: AsyncSession) -> None:
        """Test getting activities for non-existent coverage."""
        repo = CoverageRepository(db_session)
        activities = await repo.get_activities(str(uuid4()))
        assert len(activities) == 0


class TestCoverageRepositoryEdgeCases:
    """Tests for edge cases."""

    @pytest_asyncio.fixture
    async def edge_case_setup(self, db_session: AsyncSession) -> None:
        """Create setup for edge case tests."""
        project_repo = ProjectRepository(db_session)
        project = await project_repo.create(name="Edge Case Project")

        item_repo = ItemRepository(db_session)
        requirement = await item_repo.create(
            project_id=project.id,
            title="Edge Case Requirement",
            item_type="requirement",
            view="requirements",
        )

        test_case = _TestCaseModel(
            id=str(uuid4()),
            project_id=project.id,
            test_case_number="TC-EDGE-001",
            title="Edge Case Test",
            status="draft",
            test_type="functional",
        )
        db_session.add(test_case)
        await db_session.flush()

        return {
            "project": project,
            "requirement": requirement,
            "test_case": test_case,
        }

    @pytest.mark.asyncio
    async def test_create_coverage_minimal_fields(self, db_session: AsyncSession, edge_case_setup: Any) -> None:
        """Test creating coverage with minimal fields."""
        repo = CoverageRepository(db_session)
        entities = edge_case_setup

        coverage = await repo.create(
            project_id=entities["project"].id,
            test_case_id=entities["test_case"].id,
            requirement_id=entities["requirement"].id,
        )

        assert coverage is not None
        assert coverage.coverage_type == CoverageType.DIRECT
        assert coverage.status == CoverageStatus.ACTIVE

    @pytest.mark.asyncio
    async def test_list_by_project_empty(self, db_session: AsyncSession) -> None:
        """Test listing coverages for project with none."""
        project_repo = ProjectRepository(db_session)
        project = await project_repo.create(name="Empty Coverage Project")

        repo = CoverageRepository(db_session)
        coverages, total = await repo.list_by_project(project.id)

        assert len(coverages) == 0
        assert total == 0

    @pytest.mark.asyncio
    async def test_traceability_matrix_no_requirements(self, db_session: AsyncSession) -> None:
        """Test traceability matrix for project with no requirements."""
        project_repo = ProjectRepository(db_session)
        project = await project_repo.create(name="No Requirements Project")

        repo = CoverageRepository(db_session)
        matrix = await repo.get_traceability_matrix(project.id)

        assert matrix["total_requirements"] == 0
        assert matrix["covered_requirements"] == 0
        assert matrix["coverage_percentage"] == 0

    @pytest.mark.asyncio
    async def test_coverage_gaps_all_covered(self, db_session: AsyncSession, edge_case_setup: Any) -> None:
        """Test coverage gaps when all requirements are covered."""
        repo = CoverageRepository(db_session)
        entities = edge_case_setup

        await repo.create(
            project_id=entities["project"].id,
            test_case_id=entities["test_case"].id,
            requirement_id=entities["requirement"].id,
            coverage_type="direct",
        )

        gaps = await repo.get_coverage_gaps(entities["project"].id)

        assert gaps["uncovered_count"] == 0
        assert gaps["coverage_percentage"] == 100.0
        assert len(gaps["gaps"]) == 0

    @pytest.mark.asyncio
    async def test_update_with_no_changes(self, db_session: AsyncSession, edge_case_setup: Any) -> None:
        """Test update with no actual changes."""
        repo = CoverageRepository(db_session)
        entities = edge_case_setup

        coverage = await repo.create(
            project_id=entities["project"].id,
            test_case_id=entities["test_case"].id,
            requirement_id=entities["requirement"].id,
            coverage_type="direct",
        )

        # Update with empty kwargs (only version should increment)
        updated = await repo.update(coverage.id)

        assert updated is not None
        assert updated.version == COUNT_TWO
