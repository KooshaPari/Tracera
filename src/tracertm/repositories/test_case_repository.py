"""Test Case repository for TraceRTM Quality Engineering."""

from datetime import UTC, datetime
from typing import Any
from uuid import uuid4

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from tracertm.core.concurrency import ConcurrencyError
from tracertm.models.test_case import TestCase, TestCaseActivity


class TestCaseRepository:
    """Repository for TestCase CRUD operations with optimistic locking."""

    def __init__(self, session: AsyncSession) -> None:
        """Initialize repository.

        Args:
            session: SQLAlchemy async session for database operations.
        """
        self.session = session

    def _generate_test_case_number(self) -> str:
        """Generate a unique test case number."""
        timestamp = datetime.now(UTC).strftime("%Y%m%d")
        unique_part = str(uuid4())[:8].upper()
        return f"TC-{timestamp}-{unique_part}"

    async def create(
        self,
        project_id: str,
        title: str,
        description: str | None = None,
        objective: str | None = None,
        test_type: str = "functional",
        priority: str = "medium",
        category: str | None = None,
        tags: list[str] | None = None,
        preconditions: str | None = None,
        test_steps: list[dict[str, Any]] | None = None,
        expected_result: str | None = None,
        postconditions: str | None = None,
        test_data: dict[str, Any] | None = None,
        automation_status: str = "not_automated",
        automation_script_path: str | None = None,
        automation_framework: str | None = None,
        automation_notes: str | None = None,
        estimated_duration_minutes: int | None = None,
        assigned_to: str | None = None,
        metadata: dict[str, Any] | None = None,
        created_by: str = "system",
    ) -> TestCase:
        """Create new test case."""
        test_case = TestCase(
            id=str(uuid4()),
            test_case_number=self._generate_test_case_number(),
            project_id=project_id,
            title=title,
            description=description,
            objective=objective,
            status="draft",
            test_type=test_type,
            priority=priority,
            category=category,
            tags=tags,
            preconditions=preconditions,
            test_steps=test_steps,
            expected_result=expected_result,
            postconditions=postconditions,
            test_data=test_data,
            automation_status=automation_status,
            automation_script_path=automation_script_path,
            automation_framework=automation_framework,
            automation_notes=automation_notes,
            estimated_duration_minutes=estimated_duration_minutes,
            created_by=created_by,
            assigned_to=assigned_to,
            test_case_metadata=metadata or {},
            version=1,
        )
        self.session.add(test_case)
        await self.session.flush()
        await self.session.refresh(test_case)

        # Log creation activity
        await self._log_activity(
            test_case_id=test_case.id,
            activity_type="created",
            to_value="draft",
            description=f"Test case created: {title}",
            performed_by=created_by,
        )

        return test_case

    async def get_by_id(self, test_case_id: str, project_id: str | None = None) -> TestCase | None:
        """Get test case by ID, optionally scoped to project."""
        query = select(TestCase).where(TestCase.id == test_case_id, TestCase.deleted_at.is_(None))

        if project_id:
            query = query.where(TestCase.project_id == project_id)

        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_by_number(self, test_case_number: str, project_id: str | None = None) -> TestCase | None:
        """Get test case by test case number."""
        query = select(TestCase).where(TestCase.test_case_number == test_case_number, TestCase.deleted_at.is_(None))

        if project_id:
            query = query.where(TestCase.project_id == project_id)

        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def list_all(
        self,
        project_id: str,
        include_deleted: bool = False,
        status: str | None = None,
        test_type: str | None = None,
        priority: str | None = None,
        automation_status: str | None = None,
        category: str | None = None,
        assigned_to: str | None = None,
        search: str | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> list[TestCase]:
        """List test cases with optional filters."""
        query = select(TestCase).where(TestCase.project_id == project_id)

        if not include_deleted:
            query = query.where(TestCase.deleted_at.is_(None))

        if status:
            query = query.where(TestCase.status == status)
        if test_type:
            query = query.where(TestCase.test_type == test_type)
        if priority:
            query = query.where(TestCase.priority == priority)
        if automation_status:
            query = query.where(TestCase.automation_status == automation_status)
        if category:
            query = query.where(TestCase.category == category)
        if assigned_to:
            query = query.where(TestCase.assigned_to == assigned_to)
        if search:
            search_term = f"%{search}%"
            query = query.where(
                (TestCase.title.ilike(search_term))
                | (TestCase.description.ilike(search_term))
                | (TestCase.test_case_number.ilike(search_term)),
            )

        query = query.order_by(TestCase.created_at.desc()).limit(limit).offset(offset)
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def count(
        self,
        project_id: str,
        include_deleted: bool = False,
        status: str | None = None,
        test_type: str | None = None,
        priority: str | None = None,
        automation_status: str | None = None,
    ) -> int:
        """Count test cases with optional filters."""
        query = select(func.count(TestCase.id)).where(TestCase.project_id == project_id)

        if not include_deleted:
            query = query.where(TestCase.deleted_at.is_(None))

        if status:
            query = query.where(TestCase.status == status)
        if test_type:
            query = query.where(TestCase.test_type == test_type)
        if priority:
            query = query.where(TestCase.priority == priority)
        if automation_status:
            query = query.where(TestCase.automation_status == automation_status)

        result = await self.session.execute(query)
        return result.scalar() or 0

    async def get_stats(self, project_id: str) -> dict[str, Any]:
        """Get statistics for test cases in a project."""
        from sqlalchemy import and_

        # Total count (excluding soft-deleted)
        total_result = await self.session.execute(
            select(func.count(TestCase.id)).where(
                and_(
                    TestCase.project_id == project_id,
                    TestCase.deleted_at.is_(None),
                ),
            ),
        )
        total = total_result.scalar() or 0

        # By status
        status_result = await self.session.execute(
            select(TestCase.status, func.count())
            .where(
                and_(
                    TestCase.project_id == project_id,
                    TestCase.deleted_at.is_(None),
                ),
            )
            .group_by(TestCase.status),
        )
        by_status = {str(row[0]): row[1] for row in status_result}

        # By priority
        priority_result = await self.session.execute(
            select(TestCase.priority, func.count())
            .where(
                and_(
                    TestCase.project_id == project_id,
                    TestCase.deleted_at.is_(None),
                ),
            )
            .group_by(TestCase.priority),
        )
        by_priority = {str(row[0]): row[1] for row in priority_result}

        # Automated vs manual
        auto_result = await self.session.execute(
            select(func.count()).where(
                and_(
                    TestCase.project_id == project_id,
                    TestCase.deleted_at.is_(None),
                    TestCase.automation_status == "automated",
                ),
            ),
        )
        automated_count = auto_result.scalar() or 0
        manual_count = max(0, total - automated_count)

        return {
            "project_id": project_id,
            "total": total,
            "by_status": by_status,
            "by_priority": by_priority,
            "automated_count": automated_count,
            "manual_count": manual_count,
        }

    async def update(
        self,
        test_case_id: str,
        expected_version: int,
        performed_by: str = "system",
        **updates: Any,
    ) -> TestCase:
        """Update test case with optimistic locking."""
        query = select(TestCase).where(TestCase.id == test_case_id)
        result = await self.session.execute(query)
        test_case = result.scalar_one_or_none()

        if not test_case:
            msg = f"Test case {test_case_id} not found"
            raise ValueError(msg)

        if test_case.version != expected_version:
            msg = (
                f"Test case {test_case_id} was modified by another process "
                f"(expected version {expected_version}, current version {test_case.version})"
            )
            raise ConcurrencyError(
                msg,
            )

        # Track changes for activity log
        changes = []
        for key, value in updates.items():
            if hasattr(test_case, key):
                old_value = getattr(test_case, key)
                if old_value != value:
                    changes.append((key, old_value, value))
                    setattr(test_case, key, value)

        test_case.version += 1

        await self.session.flush()
        await self.session.refresh(test_case)

        # Log significant changes
        for key, old_value, new_value in changes:
            if key in {"status", "priority", "test_type", "automation_status", "assigned_to"}:
                await self._log_activity(
                    test_case_id=test_case.id,
                    activity_type=f"{key}_changed",
                    from_value=str(old_value) if old_value else None,
                    to_value=str(new_value) if new_value else None,
                    performed_by=performed_by,
                )

        return test_case

    async def transition_status(
        self,
        test_case_id: str,
        to_status: str,
        reason: str | None = None,
        performed_by: str = "system",
    ) -> TestCase:
        """Transition test case status with validation."""
        query = select(TestCase).where(TestCase.id == test_case_id)
        result = await self.session.execute(query)
        test_case = result.scalar_one_or_none()

        if not test_case:
            msg = f"Test case {test_case_id} not found"
            raise ValueError(msg)

        from_status = test_case.status

        # Validate transition
        valid_transitions = {
            "draft": ["review", "deprecated"],
            "review": ["draft", "approved", "deprecated"],
            "approved": ["review", "deprecated", "archived"],
            "deprecated": ["archived", "draft"],  # Allow reactivation
            "archived": [],  # Terminal state
        }

        if to_status not in valid_transitions.get(from_status, []):
            msg = f"Invalid status transition from {from_status} to {to_status}"
            raise ValueError(msg)

        test_case.status = to_status
        test_case.version += 1

        # Set review/approval metadata
        now = datetime.now(UTC)
        if to_status == "review":
            test_case.reviewed_at = None  # Reset if going back to review
        elif to_status == "approved":
            test_case.approved_at = now
            test_case.approved_by = performed_by
        elif to_status == "deprecated":
            test_case.deprecated_at = now
            test_case.deprecation_reason = reason

        await self.session.flush()
        await self.session.refresh(test_case)

        await self._log_activity(
            test_case_id=test_case.id,
            activity_type="status_transition",
            from_value=from_status,
            to_value=to_status,
            description=reason,
            performed_by=performed_by,
        )

        return test_case

    async def submit_for_review(
        self,
        test_case_id: str,
        reviewer: str | None = None,
        performed_by: str = "system",
    ) -> TestCase:
        """Submit a test case for review."""
        test_case = await self.transition_status(
            test_case_id=test_case_id,
            to_status="review",
            performed_by=performed_by,
        )

        if reviewer:
            test_case.reviewed_by = reviewer
            await self.session.flush()
            await self.session.refresh(test_case)

        return test_case

    async def approve(
        self,
        test_case_id: str,
        reviewer_notes: str | None = None,
        performed_by: str = "system",
    ) -> TestCase:
        """Approve a test case after review."""
        test_case = await self.transition_status(
            test_case_id=test_case_id,
            to_status="approved",
            reason=reviewer_notes,
            performed_by=performed_by,
        )

        test_case.reviewed_by = performed_by
        test_case.reviewed_at = datetime.now(UTC)
        await self.session.flush()
        await self.session.refresh(test_case)

        return test_case

    async def deprecate(
        self,
        test_case_id: str,
        reason: str,
        replacement_test_case_id: str | None = None,
        performed_by: str = "system",
    ) -> TestCase:
        """Deprecate a test case."""
        test_case = await self.transition_status(
            test_case_id=test_case_id,
            to_status="deprecated",
            reason=reason,
            performed_by=performed_by,
        )

        # Store replacement info in metadata
        if replacement_test_case_id:
            metadata = test_case.test_case_metadata or {}
            metadata["replacement_test_case_id"] = replacement_test_case_id
            test_case.test_case_metadata = metadata
            await self.session.flush()
            await self.session.refresh(test_case)

        return test_case

    async def record_execution(
        self,
        test_case_id: str,
        result: str,
        executed_by: str = "system",
    ) -> TestCase:
        """Record a test execution result (called from test run)."""
        query = select(TestCase).where(TestCase.id == test_case_id)
        db_result = await self.session.execute(query)
        test_case = db_result.scalar_one_or_none()

        if not test_case:
            msg = f"Test case {test_case_id} not found"
            raise ValueError(msg)

        test_case.last_executed_at = datetime.now(UTC)
        test_case.last_execution_result = result
        test_case.total_executions += 1

        if result == "passed":
            test_case.pass_count += 1
        elif result == "failed":
            test_case.fail_count += 1

        test_case.version += 1

        await self.session.flush()
        await self.session.refresh(test_case)

        await self._log_activity(
            test_case_id=test_case.id,
            activity_type="executed",
            to_value=result,
            description=f"Test executed with result: {result}",
            performed_by=executed_by,
        )

        return test_case

    async def delete(self, test_case_id: str, soft: bool = True) -> bool:
        """Delete test case (soft delete by default)."""
        if soft:
            query = select(TestCase).where(TestCase.id == test_case_id)
            result = await self.session.execute(query)
            test_case = result.scalar_one_or_none()

            if not test_case:
                return False

            test_case.deleted_at = datetime.now(UTC)
            await self.session.flush()
            return True
        from sqlalchemy import delete

        result = await self.session.execute(delete(TestCase).where(TestCase.id == test_case_id))
        return getattr(result, "rowcount", 0) > 0

    async def count_by_status(self, project_id: str) -> dict[str, int]:
        """Count test cases by status for a project."""
        query = (
            select(TestCase.status, func.count(TestCase.id))
            .where(
                TestCase.project_id == project_id,
                TestCase.deleted_at.is_(None),
            )
            .group_by(TestCase.status)
        )

        result = await self.session.execute(query)
        return {r[0]: r[1] for r in result.all()}

    async def count_by_type(self, project_id: str) -> dict[str, int]:
        """Count test cases by type for a project."""
        query = (
            select(TestCase.test_type, func.count(TestCase.id))
            .where(
                TestCase.project_id == project_id,
                TestCase.deleted_at.is_(None),
            )
            .group_by(TestCase.test_type)
        )

        result = await self.session.execute(query)
        return {row[0]: row[1] for row in result.all()}

    async def count_by_priority(self, project_id: str) -> dict[str, int]:
        """Count test cases by priority for a project."""
        query = (
            select(TestCase.priority, func.count(TestCase.id))
            .where(
                TestCase.project_id == project_id,
                TestCase.deleted_at.is_(None),
            )
            .group_by(TestCase.priority)
        )

        result = await self.session.execute(query)
        return {row[0]: row[1] for row in result.all()}

    async def count_by_automation_status(self, project_id: str) -> dict[str, int]:
        """Count test cases by automation status for a project."""
        query = (
            select(TestCase.automation_status, func.count(TestCase.id))
            .where(
                TestCase.project_id == project_id,
                TestCase.deleted_at.is_(None),
            )
            .group_by(TestCase.automation_status)
        )

        result = await self.session.execute(query)
        return {row[0]: row[1] for row in result.all()}

    async def get_execution_summary(self, project_id: str) -> dict[str, int]:
        """Get execution statistics summary for a project."""
        query = select(
            func.sum(TestCase.total_executions),
            func.sum(TestCase.pass_count),
            func.sum(TestCase.fail_count),
        ).where(
            TestCase.project_id == project_id,
            TestCase.deleted_at.is_(None),
        )

        result = await self.session.execute(query)
        row = result.one()
        return {
            "total_runs": row[0] or 0,
            "total_passed": row[1] or 0,
            "total_failed": row[2] or 0,
        }

    async def get_activities(self, test_case_id: str, limit: int = 50) -> list[TestCaseActivity]:
        """Get activity log for a test case."""
        query = (
            select(TestCaseActivity)
            .where(TestCaseActivity.test_case_id == test_case_id)
            .order_by(TestCaseActivity.created_at.desc())
            .limit(limit)
        )

        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def _log_activity(
        self,
        test_case_id: str,
        activity_type: str,
        from_value: str | None = None,
        to_value: str | None = None,
        description: str | None = None,
        performed_by: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> TestCaseActivity:
        """Log an activity for a test case."""
        activity = TestCaseActivity(
            id=str(uuid4()),
            test_case_id=test_case_id,
            activity_type=activity_type,
            from_value=from_value,
            to_value=to_value,
            description=description,
            performed_by=performed_by,
            activity_metadata=metadata or {},
        )
        self.session.add(activity)
        await self.session.flush()
        return activity
