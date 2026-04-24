"""Repository for Test Run operations."""

import uuid
from datetime import UTC, datetime
from typing import Any

from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from tracertm.models.test_case import TestCase
from tracertm.models.test_run import (
    TestResult,
    TestResultStatus,
    TestRun,
    TestRunActivity,
    TestRunStatus,
    TestRunType,
)


class TestRunRepository:
    """Repository for test run CRUD and business operations."""

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
        suite_id: str | None = None,
        run_type: str = "manual",
        environment: str | None = None,
        build_number: str | None = None,
        build_url: str | None = None,
        branch: str | None = None,
        commit_sha: str | None = None,
        scheduled_at: datetime | None = None,
        initiated_by: str | None = None,
        tags: list[str] | None = None,
        external_run_id: str | None = None,
        webhook_id: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> TestRun:
        """Create a new test run."""
        run_number = f"TR-{str(uuid.uuid4())[:8].upper()}"

        run = TestRun(
            id=str(uuid.uuid4()),
            run_number=run_number,
            project_id=project_id,
            suite_id=suite_id,
            name=name,
            description=description,
            status=TestRunStatus.PENDING,
            run_type=TestRunType(run_type),
            environment=environment,
            build_number=build_number,
            build_url=build_url,
            branch=branch,
            commit_sha=commit_sha,
            scheduled_at=scheduled_at,
            initiated_by=initiated_by,
            tags=tags,
            external_run_id=external_run_id,
            webhook_id=webhook_id,
            run_metadata=metadata or {},
        )
        self.session.add(run)

        # Log creation activity
        activity = TestRunActivity(
            id=str(uuid.uuid4()),
            run_id=run.id,
            activity_type="created",
            to_value=TestRunStatus.PENDING.value,
            description=f"Test run '{name}' created",
            performed_by=initiated_by,
        )
        self.session.add(activity)

        await self.session.flush()
        return run

    async def get_by_id(self, run_id: str) -> TestRun | None:
        """Get a test run by ID."""
        result = await self.session.execute(
            select(TestRun).options(selectinload(TestRun.results)).where(TestRun.id == run_id),
        )
        return result.scalar_one_or_none()

    async def get_by_number(self, run_number: str) -> TestRun | None:
        """Get a test run by run number."""
        result = await self.session.execute(select(TestRun).where(TestRun.run_number == run_number))
        return result.scalar_one_or_none()

    async def list_by_project(
        self,
        project_id: str,
        status: str | None = None,
        run_type: str | None = None,
        suite_id: str | None = None,
        environment: str | None = None,
        initiated_by: str | None = None,
        from_date: datetime | None = None,
        to_date: datetime | None = None,
        skip: int = 0,
        limit: int = 50,
    ) -> tuple[list[TestRun], int]:
        """List test runs for a project with filtering."""
        query = select(TestRun).where(TestRun.project_id == project_id)

        if status:
            query = query.where(TestRun.status == status)
        if run_type:
            query = query.where(TestRun.run_type == run_type)
        if suite_id:
            query = query.where(TestRun.suite_id == suite_id)
        if environment:
            query = query.where(TestRun.environment == environment)
        if initiated_by:
            query = query.where(TestRun.initiated_by == initiated_by)
        if from_date:
            query = query.where(TestRun.created_at >= from_date)
        if to_date:
            query = query.where(TestRun.created_at <= to_date)

        # Count total
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await self.session.execute(count_query)
        total = total_result.scalar() or 0

        # Apply pagination
        query = query.order_by(TestRun.created_at.desc())
        query = query.offset(skip).limit(limit)

        result = await self.session.execute(query)
        runs = list(result.scalars().all())

        return runs, total

    async def update(
        self,
        run_id: str,
        _updated_by: str | None = None,
        **updates: Any,
    ) -> TestRun | None:
        """Update a test run."""
        run = await self.get_by_id(run_id)
        if not run:
            return None

        for key, value in updates.items():
            if hasattr(run, key) and value is not None:
                setattr(run, key, value)

        run.version += 1
        await self.session.flush()
        return run

    async def start(
        self,
        run_id: str,
        executed_by: str | None = None,
    ) -> TestRun | None:
        """Start a test run."""
        run = await self.get_by_id(run_id)
        if not run:
            return None

        if run.status != TestRunStatus.PENDING:
            msg = f"Cannot start run in status {run.status.value}"
            raise ValueError(msg)

        old_status = run.status
        run.status = TestRunStatus.RUNNING
        run.started_at = datetime.now(UTC)
        run.executed_by = executed_by
        run.version += 1

        # Log activity
        activity = TestRunActivity(
            id=str(uuid.uuid4()),
            run_id=run_id,
            activity_type="started",
            from_value=old_status.value,
            to_value=TestRunStatus.RUNNING.value,
            performed_by=executed_by,
        )
        self.session.add(activity)

        await self.session.flush()
        return run

    async def complete(
        self,
        run_id: str,
        status: str | None = None,
        notes: str | None = None,
        failure_summary: str | None = None,
        completed_by: str | None = None,
    ) -> TestRun | None:
        """Complete a test run."""
        run = await self.get_by_id(run_id)
        if not run:
            return None

        if run.status != TestRunStatus.RUNNING:
            msg = f"Cannot complete run in status {run.status.value}"
            raise ValueError(msg)

        old_status = run.status
        completed_at = datetime.now(UTC)
        run.completed_at = completed_at
        if run.started_at:
            run.duration_seconds = int((completed_at - run.started_at).total_seconds())

        # Determine final status based on results if not provided
        if status:
            run.status = TestRunStatus(status)
        elif run.failed_count > 0 or run.error_count > 0:
            run.status = TestRunStatus.FAILED
        elif run.blocked_count > 0:
            run.status = TestRunStatus.BLOCKED
        else:
            run.status = TestRunStatus.PASSED

        if notes:
            run.notes = notes
        if failure_summary:
            run.failure_summary = failure_summary

        # Calculate pass rate
        if run.total_tests > 0:
            run.pass_rate = (run.passed_count / run.total_tests) * 100

        run.version += 1

        # Log activity
        activity = TestRunActivity(
            id=str(uuid.uuid4()),
            run_id=run_id,
            activity_type="completed",
            from_value=old_status.value,
            to_value=run.status.value,
            description=notes,
            performed_by=completed_by,
        )
        self.session.add(activity)

        await self.session.flush()
        return run

    async def cancel(
        self,
        run_id: str,
        reason: str | None = None,
        cancelled_by: str | None = None,
    ) -> TestRun | None:
        """Cancel a test run."""
        run = await self.get_by_id(run_id)
        if not run:
            return None

        if run.status not in {TestRunStatus.PENDING, TestRunStatus.RUNNING}:
            msg = f"Cannot cancel run in status {run.status.value}"
            raise ValueError(msg)

        old_status = run.status
        run.status = TestRunStatus.CANCELLED
        completed_at = datetime.now(UTC)
        run.completed_at = completed_at
        if run.started_at:
            run.duration_seconds = int((completed_at - run.started_at).total_seconds())
        if reason:
            run.notes = reason

        run.version += 1

        # Log activity
        activity = TestRunActivity(
            id=str(uuid.uuid4()),
            run_id=run_id,
            activity_type="cancelled",
            from_value=old_status.value,
            to_value=TestRunStatus.CANCELLED.value,
            description=reason,
            performed_by=cancelled_by,
        )
        self.session.add(activity)

        await self.session.flush()
        return run

    async def add_result(
        self,
        run_id: str,
        test_case_id: str,
        status: str,
        started_at: datetime | None = None,
        completed_at: datetime | None = None,
        duration_seconds: int | None = None,
        executed_by: str | None = None,
        actual_result: str | None = None,
        failure_reason: str | None = None,
        error_message: str | None = None,
        stack_trace: str | None = None,
        screenshots: list[str] | None = None,
        logs_url: str | None = None,
        attachments: list[dict[str, Any]] | None = None,
        step_results: list[dict[str, Any]] | None = None,
        linked_defect_ids: list[str] | None = None,
        created_defect_id: str | None = None,
        retry_count: int = 0,
        is_flaky: bool = False,
        notes: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> TestResult:
        """Add a test result to a run."""
        result = TestResult(
            id=str(uuid.uuid4()),
            run_id=run_id,
            test_case_id=test_case_id,
            status=TestResultStatus(status),
            started_at=started_at,
            completed_at=completed_at,
            duration_seconds=duration_seconds,
            executed_by=executed_by,
            actual_result=actual_result,
            failure_reason=failure_reason,
            error_message=error_message,
            stack_trace=stack_trace,
            screenshots=screenshots,
            logs_url=logs_url,
            attachments=attachments,
            step_results=step_results,
            linked_defect_ids=linked_defect_ids,
            created_defect_id=created_defect_id,
            retry_count=retry_count,
            is_flaky=is_flaky,
            notes=notes,
            run_metadata=metadata or {},
        )
        self.session.add(result)

        # Update run metrics
        run = await self.get_by_id(run_id)
        if run:
            run.total_tests += 1
            status_enum = TestResultStatus(status)
            if status_enum == TestResultStatus.PASSED:
                run.passed_count += 1
            elif status_enum == TestResultStatus.FAILED:
                run.failed_count += 1
            elif status_enum == TestResultStatus.SKIPPED:
                run.skipped_count += 1
            elif status_enum == TestResultStatus.BLOCKED:
                run.blocked_count += 1
            elif status_enum == TestResultStatus.ERROR:
                run.error_count += 1

            # Update test case execution stats
            tc_result = await self.session.execute(select(TestCase).where(TestCase.id == test_case_id))
            test_case = tc_result.scalar_one_or_none()
            if test_case:
                test_case.total_executions += 1
                test_case.last_executed_at = completed_at or datetime.now(UTC)
                test_case.last_execution_result = status
                if status_enum == TestResultStatus.PASSED:
                    test_case.pass_count += 1
                elif status_enum == TestResultStatus.FAILED:
                    test_case.fail_count += 1

        await self.session.flush()
        return result

    async def add_bulk_results(
        self,
        run_id: str,
        results: list[dict[str, Any]],
    ) -> list[TestResult]:
        """Add multiple test results at once."""
        created_results = []
        for result_data in results:
            result = await self.add_result(
                run_id=run_id,
                test_case_id=result_data["test_case_id"],
                status=result_data["status"],
                started_at=result_data.get("started_at"),
                completed_at=result_data.get("completed_at"),
                duration_seconds=result_data.get("duration_seconds"),
                executed_by=result_data.get("executed_by"),
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
            created_results.append(result)
        return created_results

    async def get_results(
        self,
        run_id: str,
        status: str | None = None,
    ) -> list[TestResult]:
        """Get all results for a run."""
        query = select(TestResult).where(TestResult.run_id == run_id)
        if status:
            query = query.where(TestResult.status == status)
        query = query.order_by(TestResult.created_at)

        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def get_activities(
        self,
        run_id: str,
        limit: int = 50,
    ) -> list[TestRunActivity]:
        """Get activity log for a run."""
        result = await self.session.execute(
            select(TestRunActivity)
            .where(TestRunActivity.run_id == run_id)
            .order_by(TestRunActivity.created_at.desc())
            .limit(limit),
        )
        return list(result.scalars().all())

    async def delete(self, run_id: str) -> bool:
        """Delete a test run."""
        run = await self.get_by_id(run_id)
        if not run:
            return False
        await self.session.delete(run)
        await self.session.flush()
        return True

    async def get_stats(self, project_id: str) -> dict[str, Any]:
        """Get statistics for test runs in a project."""
        # Total count
        total_result = await self.session.execute(select(func.count()).where(TestRun.project_id == project_id))
        total = total_result.scalar() or 0

        # By status
        status_result = await self.session.execute(
            select(TestRun.status, func.count()).where(TestRun.project_id == project_id).group_by(TestRun.status),
        )
        by_status = {str(row[0].value): row[1] for row in status_result}

        # By type
        type_result = await self.session.execute(
            select(TestRun.run_type, func.count()).where(TestRun.project_id == project_id).group_by(TestRun.run_type),
        )
        by_type = {str(row[0].value): row[1] for row in type_result}

        # By environment
        env_result = await self.session.execute(
            select(TestRun.environment, func.count())
            .where(
                and_(
                    TestRun.project_id == project_id,
                    TestRun.environment.isnot(None),
                ),
            )
            .group_by(TestRun.environment),
        )
        by_environment = {row[0]: row[1] for row in env_result}

        # Average duration
        dur_result = await self.session.execute(
            select(func.avg(TestRun.duration_seconds)).where(
                and_(
                    TestRun.project_id == project_id,
                    TestRun.duration_seconds.isnot(None),
                ),
            ),
        )
        avg_duration = dur_result.scalar()

        # Average pass rate
        rate_result = await self.session.execute(
            select(func.avg(TestRun.pass_rate)).where(
                and_(
                    TestRun.project_id == project_id,
                    TestRun.pass_rate.isnot(None),
                ),
            ),
        )
        avg_pass_rate = rate_result.scalar()

        # Recent runs
        recent_result = await self.session.execute(
            select(TestRun).where(TestRun.project_id == project_id).order_by(TestRun.created_at.desc()).limit(5),
        )
        recent_runs = list(recent_result.scalars().all())

        return {
            "project_id": project_id,
            "total_runs": total,
            "by_status": by_status,
            "by_type": by_type,
            "by_environment": by_environment,
            "average_duration_seconds": float(avg_duration) if avg_duration else None,
            "average_pass_rate": float(avg_pass_rate) if avg_pass_rate else None,
            "recent_runs": recent_runs,
        }
