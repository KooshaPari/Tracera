"""Execution orchestration service for QA Integration (STORY-002).

Coordinates execution lifecycle: create, start workspace, complete, store artifacts.
Supports both native subprocess execution (default) and Docker containers (optional).
"""

from __future__ import annotations

from datetime import UTC, datetime
from typing import TYPE_CHECKING, Any, cast

from tracertm.repositories.execution_repository import (
    ExecutionArtifactRepository,
    ExecutionEnvironmentConfigRepository,
    ExecutionRepository,
)
from tracertm.services.execution.artifact_storage import ArtifactStorageService
from tracertm.services.execution.docker_orchestrator import (
    DockerOrchestrator,
    DockerOrchestratorError,
)
from tracertm.services.execution.native_orchestrator import (
    NativeOrchestrator,
    NativeOrchestratorError,
)

if TYPE_CHECKING:
    from pathlib import Path

    from sqlalchemy.ext.asyncio import AsyncSession

    from tracertm.models.execution import Execution, ExecutionArtifact
    from tracertm.models.execution_config import ExecutionEnvironmentConfig


class ExecutionService:
    """Orchestrates test/recording executions with native subprocess or Docker and artifact storage."""

    def __init__(
        self,
        session: AsyncSession,
        *,
        artifact_storage: ArtifactStorageService | None = None,
        orchestrator: NativeOrchestrator | None = None,
        docker_orchestrator: DockerOrchestrator | None = None,
    ) -> None:
        """Initialize."""
        self.session = session
        self._exec_repo = ExecutionRepository(session)
        self._artifact_repo = ExecutionArtifactRepository(session)
        self._config_repo = ExecutionEnvironmentConfigRepository(session)
        self._storage = artifact_storage or ArtifactStorageService()
        self._orchestrator = orchestrator or NativeOrchestrator()
        self._docker = docker_orchestrator

    async def create(
        self,
        project_id: str,
        execution_type: str,
        trigger_source: str,
        *,
        test_run_id: str | None = None,
        item_id: str | None = None,
        trigger_ref: str | None = None,
        config: dict[str, Any] | None = None,
    ) -> Execution:
        """Create a new execution record (status=pending)."""
        return await self._exec_repo.create(
            project_id=project_id,
            execution_type=execution_type,
            trigger_source=trigger_source,
            test_run_id=test_run_id,
            item_id=item_id,
            trigger_ref=trigger_ref,
            config=config,
        )

    async def get(self, execution_id: str) -> Execution | None:
        """Get execution by ID."""
        return await self._exec_repo.get_by_id(execution_id)

    async def list_by_project(
        self,
        project_id: str,
        *,
        status: str | None = None,
        execution_type: str | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> list[Execution]:
        """List executions for a project."""
        return await self._exec_repo.list_by_project(
            project_id,
            status=status,
            execution_type=execution_type,
            limit=limit,
            offset=offset,
        )

    async def start(
        self,
        execution_id: str,
        *,
        mount_source: Path | str | None = None,
        command: list[str] | None = None,
        use_docker: bool = False,
    ) -> bool:
        """Start execution: create workspace/container, update status to running.

        Uses native subprocess execution by default. Pass use_docker=True to use
        Docker containers (requires docker_orchestrator to be configured).

        Returns True if started; False if execution not found or orchestrator unavailable.
        """
        execution = await self._exec_repo.get_by_id(execution_id)
        if not execution or execution.status != "pending":
            return False
        config = await self._config_repo.get_by_project(execution.project_id)

        try:
            if use_docker:
                return await self._start_with_docker(execution, execution_id, config, mount_source, command)
            return await self._start_with_native(execution, execution_id, config, mount_source, command)
        except (NativeOrchestratorError, DockerOrchestratorError) as e:
            await self._exec_repo.update_status(
                execution_id,
                "failed",
                error_message=str(e),
            )
            return False

    async def _start_with_native(
        self,
        _execution: Execution,
        execution_id: str,
        config: ExecutionEnvironmentConfig | None,
        mount_source: Path | str | None,
        _command: list[str] | None,
    ) -> bool:
        """Start execution using native subprocess orchestrator."""
        if not await self._orchestrator.is_available():
            await self._exec_repo.update_status(
                execution_id,
                "failed",
                error_message="Native execution not available",
            )
            return False

        # Create workspace
        workspace_id = await self._orchestrator.create_workspace(
            handle_id=execution_id,
            env=cast("dict[str, str]", config.environment_vars) if config and config.environment_vars else {},
        )

        # Apply resource limits if configured
        if config and config.resource_limits:
            resource_limits = config.resource_limits
            await self._orchestrator.apply_resource_limits(
                workspace_id,
                cpu_seconds=cast("int | None", resource_limits.get("cpu_seconds")),
                memory_mb=cast("int | None", resource_limits.get("memory_mb")),
            )

        # Copy mount_source to workspace if provided
        if mount_source:
            await self._orchestrator.copy_to(workspace_id, mount_source)

        now = datetime.now(UTC)
        await self._exec_repo.update_status(
            execution_id,
            "running",
            container_id=workspace_id,
            container_image="native-subprocess",
            started_at=now,
        )
        return True

    async def _start_with_docker(
        self,
        execution: Execution,
        execution_id: str,
        config: ExecutionEnvironmentConfig | None,
        mount_source: Path | str | None,
        command: list[str] | None,
    ) -> bool:
        """Start execution using Docker container orchestrator."""
        if not self._docker:
            msg = "Docker orchestrator not configured. Pass docker_orchestrator to ExecutionService."
            raise DockerOrchestratorError(
                msg,
            )

        if not await self._docker.is_available():
            await self._exec_repo.update_status(
                execution_id,
                "failed",
                error_message="Docker daemon not available",
            )
            return False

        image = config.docker_image if config else "node:20-alpine"
        container_id = await self._docker.create_and_start(
            image,
            project_id=execution.project_id,
            execution_id=execution_id,
            mount_source=mount_source,
            env_vars=cast("dict[str, str] | None", config.environment_vars) if config and config.environment_vars else None,
            working_dir=config.working_directory if config else None,
            network_mode=config.network_mode if config else "bridge",
            resource_limits=config.resource_limits if config else None,
            command=command,
            timeout=config.execution_timeout if config else 600,
        )

        now = datetime.now(UTC)
        await self._exec_repo.update_status(
            execution_id,
            "running",
            container_id=container_id,
            container_image=image,
            started_at=now,
        )
        return True

    async def complete(
        self,
        execution_id: str,
        *,
        exit_code: int = 0,
        error_message: str | None = None,
        output_summary: str | None = None,
        use_docker: bool = False,
    ) -> Execution | None:
        """Complete execution: stop process/container, compute duration, update status.

        Automatically detects whether to use native or Docker cleanup based on use_docker flag.
        """
        execution = await self._exec_repo.get_by_id(execution_id)
        if not execution:
            return None

        now = datetime.now(UTC)
        status = "passed" if exit_code == 0 else "failed"
        if error_message:
            status = "failed"
        duration_ms = None
        if execution.started_at:
            delta = now - execution.started_at
            duration_ms = int(delta.total_seconds() * 1000)

        # Clean up execution environment
        if execution.container_id:
            try:
                if use_docker:
                    if self._docker:
                        await self._docker.stop(execution.container_id, timeout=15)
                else:
                    await self._orchestrator.cleanup(execution.container_id)
            except (NativeOrchestratorError, DockerOrchestratorError):
                pass

        return await self._exec_repo.update_status(
            execution_id,
            status,
            completed_at=now,
            duration_ms=duration_ms,
            exit_code=exit_code,
            error_message=error_message,
            output_summary=output_summary,
        )

    async def store_artifact(
        self,
        execution_id: str,
        source_path: str | Path,
        artifact_type: str,
        *,
        project_id: str | None = None,
        item_id: str | None = None,
        filename: str | None = None,
    ) -> ExecutionArtifact | None:
        """Copy file into artifact storage and create ExecutionArtifact record."""
        execution = await self._exec_repo.get_by_id(execution_id)
        if not execution:
            return None
        project_id = project_id or execution.project_id
        dest_path, size = self._storage.store_file(
            project_id,
            execution_id,
            source_path,
            artifact_type,
            filename=filename,
        )
        return await self._artifact_repo.create(
            execution_id=execution_id,
            artifact_type=artifact_type,
            file_path=str(dest_path),
            captured_at=datetime.now(UTC),
            item_id=item_id,
            file_size=size,
            artifact_metadata={"stored_from": str(source_path)},
        )

    async def list_artifacts(
        self,
        execution_id: str,
        artifact_type: str | None = None,
    ) -> list[ExecutionArtifact]:
        """List artifacts for an execution."""
        return await self._artifact_repo.list_by_execution(execution_id, artifact_type=artifact_type)

    async def get_config(self, project_id: str) -> ExecutionEnvironmentConfig | None:
        """Get execution environment config for project (create default if missing)."""
        return await self._config_repo.get_by_project(project_id)

    async def upsert_config(
        self,
        project_id: str,
        *,
        docker_image: str | None = None,
        artifact_retention_days: int | None = None,
        **kwargs: object,
    ) -> ExecutionEnvironmentConfig:
        """Get or create execution config; update with provided fields."""
        return await self._config_repo.create_or_update(
            project_id,
            docker_image=docker_image,
            artifact_retention_days=artifact_retention_days,
            **kwargs,
        )

    def artifact_storage(self) -> ArtifactStorageService:
        """Return the artifact storage service (e.g. for VHS/Playwright to use)."""
        return self._storage

    def orchestrator(self) -> NativeOrchestrator:
        """Return the native orchestrator for direct workspace interaction.

        Use this to directly run commands or copy files in the workspace.
        """
        return self._orchestrator

    def docker(self) -> DockerOrchestrator | None:
        """Return the Docker orchestrator if configured (e.g. for exec/copy).

        Returns None if Docker orchestrator was not provided during initialization.
        """
        return self._docker
