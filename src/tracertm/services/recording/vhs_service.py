"""VHS CLI execution service for QA Integration (STORY-005).

Executes VHS recordings using TapeFileGenerator and stores output artifacts.
"""

from __future__ import annotations

import asyncio
import logging
import os
import subprocess
import tempfile
from pathlib import Path
from typing import TYPE_CHECKING, Any

from tracertm.services.recording.tape_generator import TapeFileGenerator

if TYPE_CHECKING:
    from tracertm.models.execution_config import ExecutionEnvironmentConfig
    from tracertm.services.execution import ExecutionService

logger = logging.getLogger(__name__)


class VHSExecutionError(Exception):
    """Raised when VHS execution fails."""


class VHSExecutionService:
    """Service for executing VHS recordings."""

    def __init__(
        self,
        execution_service: ExecutionService,
        *,
        vhs_command: str | None = None,
    ) -> None:
        """Initialize VHS execution service.

        Args:
            execution_service: ExecutionService instance for artifact storage.
            vhs_command: Override VHS command (default: "vhs").
        """
        self._exec_service = execution_service
        self._vhs_cmd: str = vhs_command or os.getenv("VHS_COMMAND", "vhs") or "vhs"

    async def execute(
        self,
        execution_id: str,
        commands: list[str] | None = None,
        *,
        tape_generator: TapeFileGenerator | None = None,
        output_filename: str | None = None,
        use_docker: bool = False,
    ) -> dict[str, Any]:
        """Execute VHS recording and store artifacts.

        Args:
            execution_id: Execution ID (must exist and be in 'pending' status).
            commands: List of shell commands to record (optional if tape_generator provided).
            tape_generator: Pre-built TapeFileGenerator (optional).
            output_filename: Override output filename (default: execution_id.gif).
            use_docker: Use Docker container if True (falls back to native execution).

        Returns:
            Dict with keys: success, artifact_id, file_path, error_message.

        Raises:
            VHSExecutionError: If execution not found or VHS command fails.
        """
        execution = await self._exec_service.get(execution_id)
        if not execution:
            msg = f"Execution {execution_id} not found"
            raise VHSExecutionError(msg)
        if execution.status != "pending":
            msg = f"Execution {execution_id} is {execution.status}, expected pending"
            raise VHSExecutionError(msg)

        config = await self._exec_service.get_config(execution.project_id)
        if config and not config.vhs_enabled:
            msg = "VHS is disabled for this project"
            raise VHSExecutionError(msg)

        # Build tape file
        if tape_generator is None:
            tape_generator = self._build_tape_generator(execution_id, commands or [], config)
        if not output_filename:
            output_filename = f"{execution_id}.gif"

        # Write tape file to temp location
        with tempfile.TemporaryDirectory() as tmpdir:
            tape_path = Path(tmpdir) / f"{execution_id}.tape"
            tape_generator.output(output_filename).write(str(tape_path))

            # Execute VHS - default to native subprocess, fall back to Docker if requested
            workdir = Path(tmpdir)
            if use_docker and execution.container_id:
                result = await self._execute_in_container(execution_id, tape_path, output_filename, workdir)
                # Fall back to native execution if container fails
                if not result["success"]:
                    result = await self._execute_subprocess(tape_path, output_filename, workdir)
            else:
                result = await self._execute_subprocess(tape_path, output_filename, workdir)

            if not result["success"]:
                await self._exec_service.complete(
                    execution_id,
                    exit_code=1,
                    error_message=result.get("error_message"),
                )
                return result

            # Store output artifact
            output_path = workdir / output_filename
            if not output_path.exists():
                # Try common VHS output locations
                for ext in [".gif", ".mp4", ".webm"]:
                    alt_path = workdir / f"{execution_id}{ext}"
                    if alt_path.exists():
                        output_path = alt_path
                        break
                else:
                    msg = f"VHS output not found: {output_filename} in {tmpdir}"
                    raise VHSExecutionError(msg)

            artifact = await self._exec_service.store_artifact(
                execution_id,
                output_path,
                "gif" if output_path.suffix == ".gif" else "video",
                filename=output_path.name,
            )

            # Store tape file as artifact too
            await self._exec_service.store_artifact(
                execution_id,
                tape_path,
                "tape",
                filename=f"{execution_id}.tape",
            )

            return {
                "success": True,
                "artifact_id": artifact.id if artifact else None,
                "file_path": str(output_path),
                "tape_path": str(tape_path),
            }

    def _build_tape_generator(
        self,
        _execution_id: str,
        commands: list[str],
        config: ExecutionEnvironmentConfig | None,
    ) -> TapeFileGenerator:
        """Build TapeFileGenerator from config and commands."""
        tape = TapeFileGenerator()
        if config:
            tape = (
                tape
                .set_shell("bash")
                .set_font_size(config.vhs_font_size)
                .set_width(config.vhs_width)
                .set_height(config.vhs_height)
                .set_theme(config.vhs_theme)
                .set_framerate(config.vhs_framerate)
            )
        else:
            tape = tape.preset_demo()

        # Add commands
        for cmd in commands:
            tape = tape.type(cmd).enter().sleep(0.5)

        return tape

    async def _execute_subprocess(self, tape_path: Path, _output_filename: str, workdir: Path) -> dict[str, Any]:
        """Execute VHS via subprocess."""
        cmd = [self._vhs_cmd, str(tape_path)]
        try:
            proc = await asyncio.create_subprocess_exec(
                *cmd,
                cwd=str(workdir),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            _stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=300)
            if proc.returncode != 0:
                return {
                    "success": False,
                    "error_message": f"VHS failed: {stderr.decode()[:500]}",
                }
        except TimeoutError:
            return {
                "success": False,
                "error_message": "VHS execution timed out after 300s",
            }
        except FileNotFoundError:
            return {
                "success": False,
                "error_message": f"VHS command not found: {self._vhs_cmd}. Install with: brew install vhs",
            }
        else:
            return {"success": True}

    async def _execute_in_container(
        self,
        execution_id: str,
        tape_path: Path,
        output_filename: str,
        workdir: Path,
    ) -> dict[str, Any]:
        """Execute VHS inside Docker container."""
        docker = self._exec_service.docker()
        execution = await self._exec_service.get(execution_id)
        if not execution or not execution.container_id or docker is None:
            return await self._execute_subprocess(tape_path, output_filename, workdir)

        # Copy tape file into container (docker cp host_path container_id:container_path)
        container_tape = f"/tmp/{tape_path.name}"  # nosec B108 -- path inside Docker container, not host
        try:
            # Docker cp: docker cp host_path container_id:container_path
            code, _, stderr = await docker._run(
                "cp",
                str(tape_path),
                f"{execution.container_id}:{container_tape}",
                timeout=30,
            )
            if code != 0:
                return {
                    "success": False,
                    "error_message": f"Failed to copy tape to container: {stderr[:200]}",
                }
        except (OSError, subprocess.SubprocessError) as e:
            return {
                "success": False,
                "error_message": f"Failed to copy tape to container: {e}",
            }

        # Run vhs inside container
        code, _stdout, stderr = await docker.exec(
            execution.container_id,
            [self._vhs_cmd, container_tape],
            timeout=300,
        )
        if code != 0:
            return {
                "success": False,
                "error_message": f"VHS failed in container: {stderr[:500]}",
            }

        # Copy output back from container (docker cp container_id:container_path host_path)
        container_output = f"/tmp/{output_filename}"  # nosec B108 -- path inside Docker container, not host
        try:
            code, _, stderr = await docker._run(
                "cp",
                f"{execution.container_id}:{container_output}",
                str(workdir / output_filename),
                timeout=30,
            )
            if code != 0:
                # Output might be in different location or format - try common container paths
                for alt in ["/tmp/output.gif", "/tmp/output.mp4", f"/tmp/{execution_id}.gif"]:  # nosec B108
                    code2, _, _ = await docker._run(
                        "cp",
                        f"{execution.container_id}:{alt}",
                        str(workdir / output_filename),
                        timeout=30,
                    )
                    if code2 == 0:
                        break
        except (OSError, subprocess.SubprocessError) as e:
            # Output might be in different location or format
            logger.debug("Copy from container failed (trying next path): %s", e)

        return {"success": True}

    async def generate_tape_from_commands(
        self,
        project_id: str,
        commands: list[str],
        *,
        output_filename: str = "demo.gif",
        config: ExecutionEnvironmentConfig | None = None,
    ) -> str:
        """Generate .tape file content from commands (without executing).

        Useful for preview or manual execution.

        Args:
            project_id: Project ID (for config lookup).
            commands: Shell commands to record.
            output_filename: Output filename.
            config: Optional config override.

        Returns:
            .tape file content as string.
        """
        if config is None:
            config = await self._exec_service.get_config(project_id)
        tape = self._build_tape_generator("preview", commands, config)
        tape.output(output_filename)
        return tape.build()
