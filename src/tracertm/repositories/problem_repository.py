"""Problem repository for TraceRTM."""

from datetime import UTC, datetime
from typing import Any
from uuid import uuid4

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from tracertm.core.concurrency import ConcurrencyError
from tracertm.models.problem import Problem, ProblemActivity


class ProblemRepository:
    """Repository for Problem CRUD operations with optimistic locking."""

    def __init__(self, session: AsyncSession) -> None:
        """Initialize repository.

        Args:
            session: SQLAlchemy async session for database operations.
        """
        self.session = session

    def _generate_problem_number(self) -> str:
        """Generate a unique problem number."""
        timestamp = datetime.now(UTC).strftime("%Y%m%d")
        unique_part = str(uuid4())[:8].upper()
        return f"P-{timestamp}-{unique_part}"

    async def create(
        self,
        project_id: str,
        title: str,
        description: str | None = None,
        category: str | None = None,
        sub_category: str | None = None,
        tags: list[str] | None = None,
        impact_level: str = "medium",
        urgency: str = "medium",
        priority: str = "medium",
        affected_systems: list[str] | None = None,
        affected_users_estimated: int | None = None,
        business_impact_description: str | None = None,
        assigned_to: str | None = None,
        assigned_team: str | None = None,
        owner: str | None = None,
        target_resolution_date: datetime | None = None,
        metadata: dict[str, Any] | None = None,
        created_by: str = "system",
    ) -> Problem:
        """Create new problem."""
        problem = Problem(
            id=str(uuid4()),
            problem_number=self._generate_problem_number(),
            project_id=project_id,
            title=title,
            description=description,
            category=category,
            sub_category=sub_category,
            tags=tags,
            impact_level=impact_level,
            urgency=urgency,
            priority=priority,
            affected_systems=affected_systems,
            affected_users_estimated=affected_users_estimated,
            business_impact_description=business_impact_description,
            assigned_to=assigned_to,
            assigned_team=assigned_team,
            owner=owner,
            target_resolution_date=target_resolution_date,
            problem_metadata=metadata or {},
            version=1,
        )
        self.session.add(problem)
        await self.session.flush()
        await self.session.refresh(problem)

        # Log creation activity
        await self._log_activity(
            problem_id=problem.id,
            activity_type="created",
            to_value="open",
            description=f"Problem created: {title}",
            performed_by=created_by,
        )

        return problem

    async def get_by_id(self, problem_id: str, project_id: str | None = None) -> Problem | None:
        """Get problem by ID, optionally scoped to project."""
        query = select(Problem).where(Problem.id == problem_id, Problem.deleted_at.is_(None))

        if project_id:
            query = query.where(Problem.project_id == project_id)

        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_by_number(self, problem_number: str, project_id: str | None = None) -> Problem | None:
        """Get problem by problem number."""
        query = select(Problem).where(Problem.problem_number == problem_number, Problem.deleted_at.is_(None))

        if project_id:
            query = query.where(Problem.project_id == project_id)

        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def list_all(
        self,
        project_id: str,
        include_deleted: bool = False,
        status: str | None = None,
        priority: str | None = None,
        impact_level: str | None = None,
        category: str | None = None,
        assigned_to: str | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> list[Problem]:
        """List problems with optional filters."""
        query = select(Problem).where(Problem.project_id == project_id)

        if not include_deleted:
            query = query.where(Problem.deleted_at.is_(None))

        if status:
            query = query.where(Problem.status == status)
        if priority:
            query = query.where(Problem.priority == priority)
        if impact_level:
            query = query.where(Problem.impact_level == impact_level)
        if category:
            query = query.where(Problem.category == category)
        if assigned_to:
            query = query.where(Problem.assigned_to == assigned_to)

        query = query.order_by(Problem.created_at.desc()).limit(limit).offset(offset)
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def update(
        self,
        problem_id: str,
        expected_version: int,
        performed_by: str = "system",
        **updates: Any,
    ) -> Problem:
        """Update problem with optimistic locking."""
        query = select(Problem).where(Problem.id == problem_id)
        result = await self.session.execute(query)
        problem = result.scalar_one_or_none()

        if not problem:
            msg = f"Problem {problem_id} not found"
            raise ValueError(msg)

        if problem.version != expected_version:
            msg = (
                f"Problem {problem_id} was modified by another process "
                f"(expected version {expected_version}, current version {problem.version})"
            )
            raise ConcurrencyError(
                msg,
            )

        # Track changes for activity log
        changes = []
        for key, value in updates.items():
            if hasattr(problem, key):
                old_value = getattr(problem, key)
                if old_value != value:
                    changes.append((key, old_value, value))
                    setattr(problem, key, value)

        problem.version += 1

        await self.session.flush()
        await self.session.refresh(problem)

        # Log significant changes
        for key, old_value, new_value in changes:
            if key in {"status", "priority", "impact_level", "assigned_to"}:
                await self._log_activity(
                    problem_id=problem.id,
                    activity_type=f"{key}_changed",
                    from_value=str(old_value) if old_value else None,
                    to_value=str(new_value) if new_value else None,
                    performed_by=performed_by,
                )

        return problem

    async def transition_status(
        self,
        problem_id: str,
        to_status: str,
        reason: str | None = None,
        performed_by: str = "system",
    ) -> Problem:
        """Transition problem status with validation."""
        query = select(Problem).where(Problem.id == problem_id)
        result = await self.session.execute(query)
        problem = result.scalar_one_or_none()

        if not problem:
            msg = f"Problem {problem_id} not found"
            raise ValueError(msg)

        from_status = problem.status

        # Validate transition (simplified - full state machine in service layer)
        valid_transitions = {
            "open": ["in_investigation", "closed"],
            "in_investigation": ["pending_workaround", "known_error", "closed"],
            "pending_workaround": ["known_error", "closed"],
            "known_error": ["awaiting_fix", "closed"],
            "awaiting_fix": ["closed"],
            "closed": ["open"],  # Reopen
        }

        if to_status not in valid_transitions.get(from_status, []):
            msg = f"Invalid status transition from {from_status} to {to_status}"
            raise ValueError(msg)

        problem.status = to_status
        problem.version += 1

        await self.session.flush()
        await self.session.refresh(problem)

        await self._log_activity(
            problem_id=problem.id,
            activity_type="status_transition",
            from_value=from_status,
            to_value=to_status,
            description=reason,
            performed_by=performed_by,
        )

        return problem

    async def record_rca(
        self,
        problem_id: str,
        rca_method: str,
        rca_notes: str | None = None,
        rca_data: dict[str, Any] | None = None,
        root_cause_identified: bool = False,
        root_cause_description: str | None = None,
        root_cause_category: str | None = None,
        root_cause_confidence: str | None = None,
        performed_by: str = "system",
    ) -> Problem:
        """Record Root Cause Analysis for a problem."""
        query = select(Problem).where(Problem.id == problem_id)
        result = await self.session.execute(query)
        problem = result.scalar_one_or_none()

        if not problem:
            msg = f"Problem {problem_id} not found"
            raise ValueError(msg)

        problem.rca_performed = True
        problem.rca_method = rca_method
        problem.rca_notes = rca_notes
        problem.rca_data = rca_data
        problem.root_cause_identified = root_cause_identified
        problem.root_cause_description = root_cause_description
        problem.root_cause_category = root_cause_category
        problem.root_cause_confidence = root_cause_confidence
        problem.rca_completed_at = datetime.now(UTC)
        problem.rca_completed_by = performed_by
        problem.version += 1

        await self.session.flush()
        await self.session.refresh(problem)

        await self._log_activity(
            problem_id=problem.id,
            activity_type="rca_completed",
            to_value=rca_method,
            description=f"RCA completed using {rca_method}. Root cause identified: {root_cause_identified}",
            performed_by=performed_by,
            metadata={"rca_method": rca_method, "root_cause_identified": root_cause_identified},
        )

        return problem

    async def update_workaround(
        self,
        problem_id: str,
        workaround_available: bool,
        workaround_description: str | None = None,
        workaround_effectiveness: str | None = None,
        performed_by: str = "system",
    ) -> Problem:
        """Update workaround information."""
        query = select(Problem).where(Problem.id == problem_id)
        result = await self.session.execute(query)
        problem = result.scalar_one_or_none()

        if not problem:
            msg = f"Problem {problem_id} not found"
            raise ValueError(msg)

        problem.workaround_available = workaround_available
        problem.workaround_description = workaround_description
        problem.workaround_effectiveness = workaround_effectiveness
        problem.version += 1

        await self.session.flush()
        await self.session.refresh(problem)

        if workaround_available:
            await self._log_activity(
                problem_id=problem.id,
                activity_type="workaround_added",
                to_value=workaround_effectiveness or "available",
                description=workaround_description,
                performed_by=performed_by,
            )

        return problem

    async def update_permanent_fix(
        self,
        problem_id: str,
        permanent_fix_available: bool,
        permanent_fix_description: str | None = None,
        permanent_fix_change_id: str | None = None,
        performed_by: str = "system",
    ) -> Problem:
        """Update permanent fix information."""
        query = select(Problem).where(Problem.id == problem_id)
        result = await self.session.execute(query)
        problem = result.scalar_one_or_none()

        if not problem:
            msg = f"Problem {problem_id} not found"
            raise ValueError(msg)

        problem.permanent_fix_available = permanent_fix_available
        problem.permanent_fix_description = permanent_fix_description
        problem.permanent_fix_change_id = permanent_fix_change_id
        if permanent_fix_available:
            problem.permanent_fix_implemented_at = datetime.now(UTC)
        problem.version += 1

        await self.session.flush()
        await self.session.refresh(problem)

        if permanent_fix_available:
            await self._log_activity(
                problem_id=problem.id,
                activity_type="permanent_fix_added",
                to_value=permanent_fix_change_id or "available",
                description=permanent_fix_description,
                performed_by=performed_by,
            )

        return problem

    async def close(
        self,
        problem_id: str,
        resolution_type: str,
        closure_notes: str | None = None,
        closed_by: str = "system",
    ) -> Problem:
        """Close a problem."""
        query = select(Problem).where(Problem.id == problem_id)
        result = await self.session.execute(query)
        problem = result.scalar_one_or_none()

        if not problem:
            msg = f"Problem {problem_id} not found"
            raise ValueError(msg)

        problem.status = "closed"
        problem.resolution_type = resolution_type
        problem.closure_notes = closure_notes
        problem.closed_by = closed_by
        problem.closed_at = datetime.now(UTC)
        problem.version += 1

        await self.session.flush()
        await self.session.refresh(problem)

        await self._log_activity(
            problem_id=problem.id,
            activity_type="closed",
            to_value=resolution_type,
            description=closure_notes,
            performed_by=closed_by,
        )

        return problem

    async def delete(self, problem_id: str, soft: bool = True) -> bool:
        """Delete problem (soft delete by default)."""
        if soft:
            query = select(Problem).where(Problem.id == problem_id)
            result = await self.session.execute(query)
            problem = result.scalar_one_or_none()

            if not problem:
                return False

            problem.deleted_at = datetime.now(UTC)
            await self.session.flush()
            return True
        from sqlalchemy import delete

        result = await self.session.execute(delete(Problem).where(Problem.id == problem_id))
        return getattr(result, "rowcount", 0) > 0

    async def count_by_status(self, project_id: str) -> dict[str, int]:
        """Count problems by status for a project."""
        query = (
            select(Problem.status, func.count(Problem.id))
            .where(
                Problem.project_id == project_id,
                Problem.deleted_at.is_(None),
            )
            .group_by(Problem.status)
        )

        result = await self.session.execute(query)
        return {r[0]: r[1] for r in result.all()}

    async def count_by_priority(self, project_id: str) -> dict[str, int]:
        """Count problems by priority for a project."""
        query = (
            select(Problem.priority, func.count(Problem.id))
            .where(
                Problem.project_id == project_id,
                Problem.deleted_at.is_(None),
            )
            .group_by(Problem.priority)
        )

        result = await self.session.execute(query)
        return {r[0]: r[1] for r in result.all()}

    async def get_activities(self, problem_id: str, limit: int = 50) -> list[ProblemActivity]:
        """Get activity log for a problem."""
        query = (
            select(ProblemActivity)
            .where(ProblemActivity.problem_id == problem_id)
            .order_by(ProblemActivity.created_at.desc())
            .limit(limit)
        )

        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def _log_activity(
        self,
        problem_id: str,
        activity_type: str,
        from_value: str | None = None,
        to_value: str | None = None,
        description: str | None = None,
        performed_by: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> ProblemActivity:
        """Log an activity for a problem."""
        activity = ProblemActivity(
            id=str(uuid4()),
            problem_id=problem_id,
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
