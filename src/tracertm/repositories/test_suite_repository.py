"""Repository for Test Suite operations."""

import uuid
from typing import Any

from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from tracertm.models.test_case import TestCase
from tracertm.models.test_suite import (
    TestSuite,
    TestSuiteActivity,
    TestSuiteStatus,
    TestSuiteTestCase,
)


class TestSuiteRepository:
    """Repository for test suite CRUD and business operations."""

    def __init__(self, session: AsyncSession) -> None:
        """Initialize repository.

        Args:
            session: SQLAlchemy async session for database operations.
        """
        self.session = session

    async def create(
        self,
        project_id: str,
        name: str,
        description: str | None = None,
        objective: str | None = None,
        parent_id: str | None = None,
        order_index: int = 0,
        category: str | None = None,
        tags: list[str] | None = None,
        is_parallel_execution: bool = False,
        estimated_duration_minutes: int | None = None,
        required_environment: str | None = None,
        environment_variables: dict[str, str] | None = None,
        setup_instructions: str | None = None,
        teardown_instructions: str | None = None,
        owner: str | None = None,
        responsible_team: str | None = None,
        metadata: dict[str, Any] | None = None,
        created_by: str | None = None,
    ) -> TestSuite:
        """Create a new test suite."""
        suite_number = f"TS-{str(uuid.uuid4())[:8].upper()}"

        suite = TestSuite(
            id=str(uuid.uuid4()),
            suite_number=suite_number,
            project_id=project_id,
            name=name,
            description=description,
            objective=objective,
            status=TestSuiteStatus.DRAFT,
            parent_id=parent_id,
            order_index=order_index,
            category=category,
            tags=tags,
            is_parallel_execution=is_parallel_execution,
            estimated_duration_minutes=estimated_duration_minutes,
            required_environment=required_environment,
            environment_variables=environment_variables,
            setup_instructions=setup_instructions,
            teardown_instructions=teardown_instructions,
            owner=owner,
            responsible_team=responsible_team,
            suite_metadata=metadata or {},
        )
        self.session.add(suite)

        # Log creation activity
        activity = TestSuiteActivity(
            id=str(uuid.uuid4()),
            suite_id=suite.id,
            activity_type="created",
            to_value=TestSuiteStatus.DRAFT.value,
            description=f"Test suite '{name}' created",
            performed_by=created_by,
        )
        self.session.add(activity)

        await self.session.flush()
        return suite

    async def get_by_id(self, suite_id: str) -> TestSuite | None:
        """Get a test suite by ID."""
        result = await self.session.execute(
            select(TestSuite).options(selectinload(TestSuite.test_case_associations)).where(TestSuite.id == suite_id),
        )
        return result.scalar_one_or_none()

    async def get_by_number(self, suite_number: str) -> TestSuite | None:
        """Get a test suite by suite number."""
        result = await self.session.execute(select(TestSuite).where(TestSuite.suite_number == suite_number))
        return result.scalar_one_or_none()

    async def list_by_project(
        self,
        project_id: str,
        status: str | None = None,
        category: str | None = None,
        parent_id: str | None = None,
        owner: str | None = None,
        search: str | None = None,
        skip: int = 0,
        limit: int = 50,
    ) -> tuple[list[TestSuite], int]:
        """List test suites for a project with filtering."""
        query = select(TestSuite).where(TestSuite.project_id == project_id)

        if status:
            query = query.where(TestSuite.status == status)
        if category:
            query = query.where(TestSuite.category == category)
        if parent_id is not None:
            if not parent_id:
                query = query.where(TestSuite.parent_id.is_(None))
            else:
                query = query.where(TestSuite.parent_id == parent_id)
        if owner:
            query = query.where(TestSuite.owner == owner)
        if search:
            search_pattern = f"%{search}%"
            query = query.where(TestSuite.name.ilike(search_pattern) | TestSuite.description.ilike(search_pattern))

        # Count total
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await self.session.execute(count_query)
        total = total_result.scalar() or 0

        # Apply pagination
        query = query.order_by(TestSuite.order_index, TestSuite.created_at.desc())
        query = query.offset(skip).limit(limit)

        result = await self.session.execute(query)
        suites = list(result.scalars().all())

        return suites, total

    async def update(
        self,
        suite_id: str,
        _updated_by: str | None = None,
        **updates: Any,
    ) -> TestSuite | None:
        """Update a test suite."""
        suite = await self.get_by_id(suite_id)
        if not suite:
            return None

        for key, value in updates.items():
            if hasattr(suite, key) and value is not None:
                setattr(suite, key, value)

        suite.version += 1
        await self.session.flush()
        return suite

    async def transition_status(
        self,
        suite_id: str,
        new_status: str,
        reason: str | None = None,
        performed_by: str | None = None,
    ) -> TestSuite | None:
        """Transition suite status with validation."""
        suite = await self.get_by_id(suite_id)
        if not suite:
            return None

        old_status = suite.status
        valid_transitions = {
            TestSuiteStatus.DRAFT: [TestSuiteStatus.ACTIVE, TestSuiteStatus.ARCHIVED],
            TestSuiteStatus.ACTIVE: [TestSuiteStatus.DEPRECATED, TestSuiteStatus.ARCHIVED],
            TestSuiteStatus.DEPRECATED: [TestSuiteStatus.ARCHIVED, TestSuiteStatus.ACTIVE],
            TestSuiteStatus.ARCHIVED: [TestSuiteStatus.DRAFT],
        }

        new_status_enum = TestSuiteStatus(new_status)
        if new_status_enum not in valid_transitions.get(old_status, []):
            msg = f"Invalid transition from {old_status.value} to {new_status}"
            raise ValueError(msg)

        suite.status = new_status_enum
        suite.version += 1

        # Log activity
        activity = TestSuiteActivity(
            id=str(uuid.uuid4()),
            suite_id=suite_id,
            activity_type="status_changed",
            from_value=old_status.value,
            to_value=new_status,
            description=reason,
            performed_by=performed_by,
        )
        self.session.add(activity)

        await self.session.flush()
        return suite

    async def add_test_case(
        self,
        suite_id: str,
        test_case_id: str,
        order_index: int = 0,
        is_mandatory: bool = True,
        skip_reason: str | None = None,
        custom_parameters: dict[str, Any] | None = None,
        added_by: str | None = None,
    ) -> TestSuiteTestCase:
        """Add a test case to a suite."""
        association = TestSuiteTestCase(
            id=str(uuid.uuid4()),
            suite_id=suite_id,
            test_case_id=test_case_id,
            order_index=order_index,
            is_mandatory=is_mandatory,
            skip_reason=skip_reason,
            custom_parameters=custom_parameters,
        )
        self.session.add(association)

        # Update suite metrics
        suite = await self.get_by_id(suite_id)
        if suite:
            suite.total_test_cases += 1

            # Check if test case is automated
            tc_result = await self.session.execute(
                select(TestCase.automation_status).where(TestCase.id == test_case_id),
            )
            tc = tc_result.scalar_one_or_none()
            if tc == "automated":
                suite.automated_count += 1

        # Log activity
        activity = TestSuiteActivity(
            id=str(uuid.uuid4()),
            suite_id=suite_id,
            activity_type="test_case_added",
            to_value=test_case_id,
            performed_by=added_by,
        )
        self.session.add(activity)

        await self.session.flush()
        return association

    async def remove_test_case(
        self,
        suite_id: str,
        test_case_id: str,
        removed_by: str | None = None,
    ) -> bool:
        """Remove a test case from a suite."""
        result = await self.session.execute(
            select(TestSuiteTestCase).where(
                and_(
                    TestSuiteTestCase.suite_id == suite_id,
                    TestSuiteTestCase.test_case_id == test_case_id,
                ),
            ),
        )
        association = result.scalar_one_or_none()
        if not association:
            return False

        await self.session.delete(association)

        # Update suite metrics
        suite = await self.get_by_id(suite_id)
        if suite and suite.total_test_cases > 0:
            suite.total_test_cases -= 1

        # Log activity
        activity = TestSuiteActivity(
            id=str(uuid.uuid4()),
            suite_id=suite_id,
            activity_type="test_case_removed",
            from_value=test_case_id,
            performed_by=removed_by,
        )
        self.session.add(activity)

        await self.session.flush()
        return True

    async def get_test_cases(
        self,
        suite_id: str,
    ) -> list[TestSuiteTestCase]:
        """Get all test case associations for a suite."""
        result = await self.session.execute(
            select(TestSuiteTestCase)
            .where(TestSuiteTestCase.suite_id == suite_id)
            .order_by(TestSuiteTestCase.order_index),
        )
        return list(result.scalars().all())

    async def reorder_test_cases(
        self,
        suite_id: str,
        ordered_test_case_ids: list[str],
        _reordered_by: str | None = None,
    ) -> bool:
        """Reorder test cases within a suite."""
        for index, tc_id in enumerate(ordered_test_case_ids):
            result = await self.session.execute(
                select(TestSuiteTestCase).where(
                    and_(
                        TestSuiteTestCase.suite_id == suite_id,
                        TestSuiteTestCase.test_case_id == tc_id,
                    ),
                ),
            )
            assoc = result.scalar_one_or_none()
            if assoc:
                assoc.order_index = index

        await self.session.flush()
        return True

    async def get_activities(
        self,
        suite_id: str,
        limit: int = 50,
    ) -> list[TestSuiteActivity]:
        """Get activity log for a suite."""
        result = await self.session.execute(
            select(TestSuiteActivity)
            .where(TestSuiteActivity.suite_id == suite_id)
            .order_by(TestSuiteActivity.created_at.desc())
            .limit(limit),
        )
        return list(result.scalars().all())

    async def delete(self, suite_id: str) -> bool:
        """Delete a test suite."""
        suite = await self.get_by_id(suite_id)
        if not suite:
            return False
        await self.session.delete(suite)
        await self.session.flush()
        return True

    async def get_stats(self, project_id: str) -> dict[str, Any]:
        """Get statistics for test suites in a project."""
        # Total count
        total_result = await self.session.execute(select(func.count()).where(TestSuite.project_id == project_id))
        total = total_result.scalar() or 0

        # By status
        status_result = await self.session.execute(
            select(TestSuite.status, func.count()).where(TestSuite.project_id == project_id).group_by(TestSuite.status),
        )
        by_status = {str(row[0].value): row[1] for row in status_result}

        # By category
        category_result = await self.session.execute(
            select(TestSuite.category, func.count())
            .where(
                and_(
                    TestSuite.project_id == project_id,
                    TestSuite.category.isnot(None),
                ),
            )
            .group_by(TestSuite.category),
        )
        by_category = {row[0]: row[1] for row in category_result}

        # Total test cases in all suites
        tc_result = await self.session.execute(
            select(func.sum(TestSuite.total_test_cases)).where(TestSuite.project_id == project_id),
        )
        total_test_cases = tc_result.scalar() or 0

        # Total automated
        auto_result = await self.session.execute(
            select(func.sum(TestSuite.automated_count)).where(TestSuite.project_id == project_id),
        )
        automated_test_cases = auto_result.scalar() or 0

        return {
            "project_id": project_id,
            "total": total,
            "by_status": by_status,
            "by_category": by_category,
            "total_test_cases": total_test_cases,
            "automated_test_cases": automated_test_cases,
        }
