"""Process repository for TraceRTM."""

from datetime import UTC, datetime
from typing import Any
from uuid import uuid4

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from tracertm.core.concurrency import ConcurrencyError
from tracertm.models.process import Process, ProcessExecution


class ProcessRepository:
    """Repository for Process CRUD operations with optimistic locking."""

    def __init__(self, session: AsyncSession) -> None:
        """Initialize repository.

        Args:
            session: SQLAlchemy async session for database operations.
        """
        self.session = session

    def _generate_process_number(self) -> str:
        """Generate a unique process number."""
        timestamp = datetime.now(UTC).strftime("%Y%m%d")
        unique_part = str(uuid4())[:8].upper()
        return f"PROC-{timestamp}-{unique_part}"

    def _generate_execution_number(self) -> str:
        """Generate a unique execution number."""
        timestamp = datetime.now(UTC).strftime("%Y%m%d%H%M%S")
        unique_part = str(uuid4())[:6].upper()
        return f"EXE-{timestamp}-{unique_part}"

    async def create(
        self,
        project_id: str,
        name: str,
        description: str | None = None,
        purpose: str | None = None,
        category: str | None = None,
        tags: list[str] | None = None,
        stages: list[dict[str, Any]] | None = None,
        swimlanes: list[dict[str, Any]] | None = None,
        inputs: list[dict[str, Any]] | None = None,
        outputs: list[dict[str, Any]] | None = None,
        triggers: list[dict[str, Any]] | None = None,
        exit_criteria: list[str] | None = None,
        bpmn_xml: str | None = None,
        owner: str | None = None,
        responsible_team: str | None = None,
        expected_duration_hours: int | None = None,
        sla_hours: int | None = None,
        related_process_ids: list[str] | None = None,
        metadata: dict[str, Any] | None = None,
        _created_by: str = "system",
    ) -> Process:
        """Create new process."""
        process = Process(
            id=str(uuid4()),
            process_number=self._generate_process_number(),
            project_id=project_id,
            name=name,
            description=description,
            purpose=purpose,
            category=category,
            tags=tags,
            stages=stages,
            swimlanes=swimlanes,
            inputs=inputs,
            outputs=outputs,
            triggers=triggers,
            exit_criteria=exit_criteria,
            bpmn_xml=bpmn_xml,
            owner=owner,
            responsible_team=responsible_team,
            expected_duration_hours=expected_duration_hours,
            sla_hours=sla_hours,
            related_process_ids=related_process_ids,
            process_metadata=metadata or {},
            version_number=1,
            is_active_version=True,
            status="draft",
            version=1,
        )
        self.session.add(process)
        await self.session.flush()
        await self.session.refresh(process)
        return process

    async def get_by_id(self, process_id: str, project_id: str | None = None) -> Process | None:
        """Get process by ID, optionally scoped to project."""
        query = select(Process).where(Process.id == process_id, Process.deleted_at.is_(None))

        if project_id:
            query = query.where(Process.project_id == project_id)

        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_by_number(self, process_number: str, project_id: str | None = None) -> Process | None:
        """Get process by process number."""
        query = select(Process).where(Process.process_number == process_number, Process.deleted_at.is_(None))

        if project_id:
            query = query.where(Process.project_id == project_id)

        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def list_all(
        self,
        project_id: str,
        include_deleted: bool = False,
        status: str | None = None,
        category: str | None = None,
        owner: str | None = None,
        active_only: bool = False,
        limit: int = 100,
        offset: int = 0,
    ) -> list[Process]:
        """List processes with optional filters."""
        query = select(Process).where(Process.project_id == project_id)

        if not include_deleted:
            query = query.where(Process.deleted_at.is_(None))

        if status:
            query = query.where(Process.status == status)
        if category:
            query = query.where(Process.category == category)
        if owner:
            query = query.where(Process.owner == owner)
        if active_only:
            query = query.where(Process.is_active_version)

        query = query.order_by(Process.created_at.desc()).limit(limit).offset(offset)
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def update(
        self,
        process_id: str,
        expected_version: int,
        **updates: Any,
    ) -> Process:
        """Update process with optimistic locking."""
        query = select(Process).where(Process.id == process_id)
        result = await self.session.execute(query)
        process = result.scalar_one_or_none()

        if not process:
            msg = f"Process {process_id} not found"
            raise ValueError(msg)

        if process.version != expected_version:
            msg = (
                f"Process {process_id} was modified by another process "
                f"(expected version {expected_version}, current version {process.version})"
            )
            raise ConcurrencyError(
                msg,
            )

        for key, value in updates.items():
            if hasattr(process, key):
                setattr(process, key, value)

        process.version += 1

        await self.session.flush()
        await self.session.refresh(process)
        return process

    async def create_version(
        self,
        process_id: str,
        version_notes: str | None = None,
        _created_by: str = "system",
    ) -> Process:
        """Create a new version of a process."""
        query = select(Process).where(Process.id == process_id)
        result = await self.session.execute(query)
        original = result.scalar_one_or_none()

        if not original:
            msg = f"Process {process_id} not found"
            raise ValueError(msg)

        # Create new version as copy
        new_process = Process(
            id=str(uuid4()),
            process_number=self._generate_process_number(),
            project_id=original.project_id,
            name=original.name,
            description=original.description,
            purpose=original.purpose,
            category=original.category,
            tags=original.tags,
            stages=original.stages,
            swimlanes=original.swimlanes,
            inputs=original.inputs,
            outputs=original.outputs,
            triggers=original.triggers,
            exit_criteria=original.exit_criteria,
            bpmn_xml=original.bpmn_xml,
            owner=original.owner,
            responsible_team=original.responsible_team,
            expected_duration_hours=original.expected_duration_hours,
            sla_hours=original.sla_hours,
            related_process_ids=original.related_process_ids,
            process_metadata=original.process_metadata,
            version_number=original.version_number + 1,
            is_active_version=False,  # New versions start inactive
            parent_version_id=original.id,
            version_notes=version_notes,
            status="draft",
            version=1,
        )
        self.session.add(new_process)
        await self.session.flush()
        await self.session.refresh(new_process)
        return new_process

    async def activate_version(
        self,
        process_id: str,
        activated_by: str = "system",
    ) -> Process:
        """Activate a process version, deactivating others with same name."""
        query = select(Process).where(Process.id == process_id)
        result = await self.session.execute(query)
        process = result.scalar_one_or_none()

        if not process:
            msg = f"Process {process_id} not found"
            raise ValueError(msg)

        # Deactivate other versions
        deactivate_query = select(Process).where(
            Process.project_id == process.project_id,
            Process.name == process.name,
            Process.id != process_id,
            Process.is_active_version,
        )
        result = await self.session.execute(deactivate_query)
        for other in result.scalars().all():
            other.is_active_version = False

        # Activate this version
        process.is_active_version = True
        process.status = "active"
        process.activated_at = datetime.now(UTC)
        process.activated_by = activated_by
        process.version += 1

        await self.session.flush()
        await self.session.refresh(process)
        return process

    async def deprecate(
        self,
        process_id: str,
        deprecation_reason: str | None = None,
        deprecated_by: str = "system",
    ) -> Process:
        """Deprecate a process."""
        query = select(Process).where(Process.id == process_id)
        result = await self.session.execute(query)
        process = result.scalar_one_or_none()

        if not process:
            msg = f"Process {process_id} not found"
            raise ValueError(msg)

        process.status = "deprecated"
        process.deprecated_at = datetime.now(UTC)
        process.deprecated_by = deprecated_by
        process.deprecation_reason = deprecation_reason
        process.version += 1

        await self.session.flush()
        await self.session.refresh(process)
        return process

    async def delete(self, process_id: str, soft: bool = True) -> bool:
        """Delete process (soft delete by default)."""
        if soft:
            query = select(Process).where(Process.id == process_id)
            result = await self.session.execute(query)
            process = result.scalar_one_or_none()

            if not process:
                return False

            process.deleted_at = datetime.now(UTC)
            await self.session.flush()
            return True
        from sqlalchemy import delete

        result = await self.session.execute(delete(Process).where(Process.id == process_id))
        return getattr(result, "rowcount", 0) > 0

    async def count_by_status(self, project_id: str) -> dict[str, int]:
        """Count processes by status for a project."""
        query = (
            select(Process.status, func.count(Process.id))
            .where(
                Process.project_id == project_id,
                Process.deleted_at.is_(None),
            )
            .group_by(Process.status)
        )

        result = await self.session.execute(query)
        return {r[0]: r[1] for r in result.all()}

    async def count_by_category(self, project_id: str) -> dict[str, int]:
        """Count processes by category for a project."""
        query = (
            select(Process.category, func.count(Process.id))
            .where(
                Process.project_id == project_id,
                Process.deleted_at.is_(None),
            )
            .group_by(Process.category)
        )

        result = await self.session.execute(query)
        return {r[0]: r[1] for r in result.all()}

    # Process Execution methods

    async def create_execution(
        self,
        process_id: str,
        initiated_by: str | None = None,
        trigger_item_id: str | None = None,
        context_data: dict[str, Any] | None = None,
    ) -> ProcessExecution:
        """Create a new process execution."""
        # Verify process exists
        process = await self.get_by_id(process_id)
        if not process:
            msg = f"Process {process_id} not found"
            raise ValueError(msg)

        execution = ProcessExecution(
            id=str(uuid4()),
            process_id=process_id,
            execution_number=self._generate_execution_number(),
            status="pending",
            initiated_by=initiated_by,
            trigger_item_id=trigger_item_id,
            context_data=context_data or {},
        )
        self.session.add(execution)
        await self.session.flush()
        await self.session.refresh(execution)
        return execution

    async def get_execution_by_id(self, execution_id: str) -> ProcessExecution | None:
        """Get process execution by ID."""
        query = select(ProcessExecution).where(ProcessExecution.id == execution_id)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def list_executions(
        self,
        process_id: str,
        status: str | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> list[ProcessExecution]:
        """List executions for a process."""
        query = select(ProcessExecution).where(ProcessExecution.process_id == process_id)

        if status:
            query = query.where(ProcessExecution.status == status)

        query = query.order_by(ProcessExecution.created_at.desc()).limit(limit).offset(offset)
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def start_execution(self, execution_id: str) -> ProcessExecution:
        """Start a process execution."""
        query = select(ProcessExecution).where(ProcessExecution.id == execution_id)
        result = await self.session.execute(query)
        execution = result.scalar_one_or_none()

        if not execution:
            msg = f"Execution {execution_id} not found"
            raise ValueError(msg)

        execution.status = "in_progress"
        execution.started_at = datetime.now(UTC)

        await self.session.flush()
        await self.session.refresh(execution)
        return execution

    async def advance_execution(
        self,
        execution_id: str,
        stage_id: str,
    ) -> ProcessExecution:
        """Advance execution to next stage."""
        query = select(ProcessExecution).where(ProcessExecution.id == execution_id)
        result = await self.session.execute(query)
        execution = result.scalar_one_or_none()

        if not execution:
            msg = f"Execution {execution_id} not found"
            raise ValueError(msg)

        # Mark current stage as completed
        completed = execution.completed_stages or []
        if execution.current_stage_id and execution.current_stage_id not in completed:
            completed.append(execution.current_stage_id)

        execution.completed_stages = completed
        execution.current_stage_id = stage_id

        await self.session.flush()
        await self.session.refresh(execution)
        return execution

    async def complete_execution(
        self,
        execution_id: str,
        completed_by: str | None = None,
        result_summary: str | None = None,
        output_item_ids: list[str] | None = None,
    ) -> ProcessExecution:
        """Complete a process execution."""
        query = select(ProcessExecution).where(ProcessExecution.id == execution_id)
        result = await self.session.execute(query)
        execution = result.scalar_one_or_none()

        if not execution:
            msg = f"Execution {execution_id} not found"
            raise ValueError(msg)

        execution.status = "completed"
        execution.completed_at = datetime.now(UTC)
        execution.completed_by = completed_by
        execution.result_summary = result_summary
        execution.output_item_ids = output_item_ids

        await self.session.flush()
        await self.session.refresh(execution)
        return execution

    async def fail_execution(
        self,
        execution_id: str,
        result_summary: str | None = None,
    ) -> ProcessExecution:
        """Mark execution as failed."""
        query = select(ProcessExecution).where(ProcessExecution.id == execution_id)
        result = await self.session.execute(query)
        execution = result.scalar_one_or_none()

        if not execution:
            msg = f"Execution {execution_id} not found"
            raise ValueError(msg)

        execution.status = "failed"
        execution.completed_at = datetime.now(UTC)
        execution.result_summary = result_summary

        await self.session.flush()
        await self.session.refresh(execution)
        return execution

    async def cancel_execution(
        self,
        execution_id: str,
        result_summary: str | None = None,
    ) -> ProcessExecution:
        """Cancel a process execution."""
        query = select(ProcessExecution).where(ProcessExecution.id == execution_id)
        result = await self.session.execute(query)
        execution = result.scalar_one_or_none()

        if not execution:
            msg = f"Execution {execution_id} not found"
            raise ValueError(msg)

        execution.status = "cancelled"
        execution.completed_at = datetime.now(UTC)
        execution.result_summary = result_summary

        await self.session.flush()
        await self.session.refresh(execution)
        return execution
