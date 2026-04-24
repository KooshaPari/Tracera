"""Native process orchestration for QA Integration.

Executes commands directly via subprocess without Docker dependency.
Provides workspace isolation and resource management.
"""

from __future__ import annotations

import asyncio
import contextlib
import logging
import os
import shutil
import subprocess
import tempfile
import uuid
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


class NativeOrchestratorError(Exception):
    """Raised when native execution fails."""


@dataclass
class ProcessHandle:
    """Tracks a running process and its workspace."""

    process_id: str
    workspace: Path
    pid: int | None = None
    proc: asyncio.subprocess.Process | None = None
    env: dict[str, str] = field(default_factory=dict)
    created_at: float = field(default_factory=lambda: __import__("time").time())
    _wait_task: asyncio.Task[None] | None = field(default=None, repr=False)

    def is_running(self) -> bool:
        """Check if the process is still running."""
        if self.proc is None:
            return False
        return self.proc.returncode is None


class NativeOrchestrator:
    """Orchestrates native subprocess execution with workspace isolation.

    Provides:
    - Isolated workspace directories using tempfiles
    - Process lifecycle management (start, stop, cleanup)
    - File copying to/from workspaces
    - Resource limits via environment variables
    - Graceful shutdown with timeouts
    """

    def __init__(self, base_workspace: Path | str | None = None) -> None:
        """Initialize the orchestrator.

        Args:
            base_workspace: Base directory for workspaces. Defaults to system temp.
        """
        if base_workspace:
            self._base = Path(base_workspace)
        else:
            self._base = Path(tempfile.gettempdir()) / "tracertm-exec"

        self._base.mkdir(parents=True, exist_ok=True)
        self._handles: dict[str, ProcessHandle] = {}
        logger.info("NativeOrchestrator initialized with base: %s", self._base)

    async def is_available(self) -> bool:
        """Check if native execution is available.

        Always returns True since we use system subprocess.
        """
        return True

    async def create_workspace(self, handle_id: str | None = None, env: dict[str, str] | None = None) -> str:
        """Create an isolated workspace directory.

        Args:
            handle_id: Optional custom handle ID. Generated if not provided.
            env: Optional environment variables to set for processes in this workspace.

        Returns:
            The handle ID for this workspace.

        Raises:
            NativeOrchestratorError: If workspace creation fails.
        """
        if handle_id is None:
            handle_id = str(uuid.uuid4())

        if handle_id in self._handles:
            msg = f"Workspace {handle_id} already exists. Use unique handle IDs."
            raise NativeOrchestratorError(msg)

        try:
            workspace = self._base / handle_id
            workspace.mkdir(parents=True, exist_ok=True)

            handle = ProcessHandle(
                process_id=handle_id,
                workspace=workspace,
                env=env or {},
            )
            self._handles[handle_id] = handle

            logger.debug("Created workspace %s at %s", handle_id, workspace)

        except Exception as e:
            msg = f"Failed to create workspace: {e}"
            raise NativeOrchestratorError(msg) from e
        else:
            return handle_id

    async def run_command(
        self,
        handle_id: str,
        command: str | list[str],
        timeout: int = 300,
        input_data: bytes | None = None,
        check: bool = False,
    ) -> tuple[int, str, str]:
        """Run a command in the workspace.

        Args:
            handle_id: The workspace handle ID.
            command: Command to run (string or list).
            timeout: Command timeout in seconds.
            input_data: Optional stdin data.
            check: If True, raise on non-zero return code.

        Returns:
            Tuple of (return_code, stdout, stderr).

        Raises:
            NativeOrchestratorError: If handle doesn't exist or command fails.
        """
        handle = self._get_handle(handle_id)

        # Convert string command to list
        command_list = command.split() if isinstance(command, str) else command

        # Build process environment
        proc_env = os.environ.copy()
        proc_env.update(handle.env)

        try:
            logger.debug("Running command in %s: %s", handle_id, " ".join(command_list))

            proc = await asyncio.create_subprocess_exec(
                *command_list,
                cwd=str(handle.workspace),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                stdin=subprocess.PIPE if input_data else None,
                env=proc_env,
            )

            try:
                stdout_data, stderr_data = await asyncio.wait_for(
                    proc.communicate(input=input_data),
                    timeout=timeout,
                )
            except TimeoutError:
                proc.kill()
                with contextlib.suppress(TimeoutError):
                    await asyncio.wait_for(proc.wait(), timeout=5)
                msg = f"Command timed out after {timeout}s: {' '.join(command_list)}"
                raise NativeOrchestratorError(msg) from None

            stdout = stdout_data.decode("utf-8", errors="replace")
            stderr = stderr_data.decode("utf-8", errors="replace")
            return_code = proc.returncode or 0

            if check and return_code != 0:
                msg = f"Command failed with code {return_code}: {stderr}"
                raise NativeOrchestratorError(msg)

            logger.debug("Command completed with return code %s", return_code)

        except TimeoutError as e:
            msg = f"Command execution timed out: {e}"
            raise NativeOrchestratorError(msg) from e
        except Exception as e:
            msg = f"Failed to execute command: {e}"
            raise NativeOrchestratorError(msg) from e
        else:
            return return_code, stdout, stderr

    async def start_background(
        self,
        handle_id: str,
        command: str | list[str],
        timeout: int = 3600,
    ) -> str:
        """Start a background process in the workspace.

        Args:
            handle_id: The workspace handle ID.
            command: Command to run (string or list).
            timeout: Process timeout in seconds.

        Returns:
            The handle ID (for consistency with other methods).

        Raises:
            NativeOrchestratorError: If handle doesn't exist or process fails to start.
        """
        handle = self._get_handle(handle_id)

        if handle.is_running():
            msg = f"Process already running in {handle_id}. Stop it first."
            raise NativeOrchestratorError(msg)

        # Convert string command to list
        command_list = command.split() if isinstance(command, str) else command

        # Build process environment
        proc_env = os.environ.copy()
        proc_env.update(handle.env)

        try:
            logger.debug("Starting background process in %s: %s", handle_id, " ".join(command_list))

            proc = await asyncio.create_subprocess_exec(
                *command_list,
                cwd=str(handle.workspace),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                env=proc_env,
            )

            handle.proc = proc
            handle.pid = proc.pid

            # Create a task to wait for process completion (keep reference to avoid GC)
            handle._wait_task = asyncio.create_task(self._wait_process(handle_id, timeout))

            logger.debug("Background process started with PID %s", proc.pid)

        except Exception as e:
            msg = f"Failed to start background process: {e}"
            raise NativeOrchestratorError(msg) from e
        else:
            return handle_id

    async def _wait_process(self, handle_id: str, timeout: int) -> None:
        """Wait for a background process to complete or timeout.

        Args:
            handle_id: The handle ID.
            timeout: Process timeout in seconds.
        """
        handle = self._handles.get(handle_id)
        if not handle or not handle.proc:
            return

        try:
            await asyncio.wait_for(handle.proc.wait(), timeout=timeout)
        except TimeoutError:
            logger.warning("Process %s timed out after %ss, killing...", handle_id, timeout)
            await self.stop(handle_id)
        except Exception:
            logger.exception("Error waiting for process %s", handle_id)

    async def stop(self, handle_id: str, timeout: int = 30) -> None:
        """Stop a running process gracefully.

        Sends SIGTERM, waits, then SIGKILL if necessary.

        Args:
            handle_id: The workspace handle ID.
            timeout: Timeout in seconds before SIGKILL.

        Raises:
            NativeOrchestratorError: If handle doesn't exist.
        """
        handle = self._get_handle(handle_id)

        if not handle.proc or not handle.is_running():
            logger.debug("No running process in %s", handle_id)
            return

        try:
            logger.info("Stopping process %s (SIGTERM)...", handle.pid)
            handle.proc.terminate()

            try:
                await asyncio.wait_for(handle.proc.wait(), timeout=timeout)
            except TimeoutError:
                logger.warning("Process %s didn't stop, sending SIGKILL...", handle.pid)
                handle.proc.kill()
                try:
                    await asyncio.wait_for(handle.proc.wait(), timeout=5)
                except TimeoutError:
                    logger.exception("Failed to kill process %s", handle.pid)

            logger.info("Process %s stopped", handle.pid)

        except Exception:
            logger.exception("Error stopping process %s", handle_id)

    async def copy_to(self, handle_id: str, source: Path | str, dest_name: str = "") -> Path:
        """Copy a file into the workspace.

        Args:
            handle_id: The workspace handle ID.
            source: Source file path on host.
            dest_name: Destination filename in workspace. Uses source name if not provided.

        Returns:
            Path to the copied file in the workspace.

        Raises:
            NativeOrchestratorError: If copy fails.
        """
        handle = self._get_handle(handle_id)
        source_path = Path(source)

        if not source_path.exists():
            msg = f"Source file does not exist: {source_path}"
            raise NativeOrchestratorError(msg)

        dest_filename = dest_name or source_path.name
        dest_path = handle.workspace / dest_filename

        try:
            logger.debug("Copying %s to %s", source_path, dest_path)

            if source_path.is_dir():
                if dest_path.exists():
                    shutil.rmtree(dest_path)
                shutil.copytree(source_path, dest_path)
            else:
                dest_path.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(source_path, dest_path)

        except Exception as e:
            msg = f"Failed to copy file: {e}"
            raise NativeOrchestratorError(msg) from e
        else:
            return dest_path

    async def copy_from(self, handle_id: str, source_name: str, dest: Path | str) -> None:
        """Copy a file from workspace to host.

        Args:
            handle_id: The workspace handle ID.
            source_name: Source filename in workspace.
            dest: Destination path on host.

        Raises:
            NativeOrchestratorError: If copy fails.
        """
        handle = self._get_handle(handle_id)
        source_path = handle.workspace / source_name
        dest_path = Path(dest)

        if not source_path.exists():
            msg = f"Source file does not exist in workspace: {source_path}"
            raise NativeOrchestratorError(msg)

        try:
            logger.debug("Copying %s to %s", source_path, dest_path)

            dest_path.parent.mkdir(parents=True, exist_ok=True)

            if source_path.is_dir():
                if dest_path.exists():
                    shutil.rmtree(dest_path)
                shutil.copytree(source_path, dest_path)
            else:
                shutil.copy2(source_path, dest_path)

        except Exception as e:
            msg = f"Failed to copy file from workspace: {e}"
            raise NativeOrchestratorError(msg) from e

    async def cleanup(self, handle_id: str) -> None:
        """Remove workspace and stop any running process.

        Args:
            handle_id: The workspace handle ID.

        Raises:
            NativeOrchestratorError: If handle doesn't exist.
        """
        handle = self._get_handle(handle_id)

        # Stop process if running
        if handle.is_running():
            await self.stop(handle_id, timeout=10)

        # Remove workspace directory
        try:
            if handle.workspace.exists():
                logger.debug("Removing workspace %s", handle.workspace)
                shutil.rmtree(handle.workspace)
        except (OSError, subprocess.SubprocessError) as e:
            logger.warning("Failed to remove workspace %s: %s", handle.workspace, e)

        # Remove from tracking
        del self._handles[handle_id]
        logger.info("Cleaned up workspace %s", handle_id)

    async def cleanup_all(self) -> None:
        """Cleanup all workspaces (for shutdown).

        Called during graceful shutdown to clean up all resources.
        """
        logger.info("Cleaning up %s workspaces...", len(self._handles))

        # Copy handle IDs to avoid modification during iteration
        handle_ids = list(self._handles.keys())

        for handle_id in handle_ids:
            try:
                await self.cleanup(handle_id)
            except Exception:
                logger.exception("Error cleaning up %s", handle_id)

        logger.info("All workspaces cleaned up")

    def _get_handle(self, handle_id: str) -> ProcessHandle:
        """Get a handle by ID.

        Args:
            handle_id: The workspace handle ID.

        Returns:
            The ProcessHandle object.

        Raises:
            NativeOrchestratorError: If handle doesn't exist.
        """
        if handle_id not in self._handles:
            msg = f"Workspace not found: {handle_id}"
            raise NativeOrchestratorError(msg)
        return self._handles[handle_id]

    def get_workspace_path(self, handle_id: str) -> Path:
        """Get the workspace directory path.

        Args:
            handle_id: The workspace handle ID.

        Returns:
            Path to the workspace directory.

        Raises:
            NativeOrchestratorError: If handle doesn't exist.
        """
        return self._get_handle(handle_id).workspace

    def list_handles(self) -> dict[str, dict[str, Any]]:
        """List all active handles and their status.

        Returns:
            Dictionary mapping handle IDs to status info.
        """
        result = {}
        for handle_id, handle in self._handles.items():
            result[handle_id] = {
                "workspace": str(handle.workspace),
                "pid": handle.pid,
                "running": handle.is_running(),
                "created_at": handle.created_at,
            }
        return result

    async def set_workspace_env(self, handle_id: str, env: dict[str, str]) -> None:
        """Set environment variables for a workspace.

        Args:
            handle_id: The workspace handle ID.
            env: Environment variables to set.

        Raises:
            NativeOrchestratorError: If handle doesn't exist or process is running.
        """
        handle = self._get_handle(handle_id)

        if handle.is_running():
            msg = "Cannot modify environment while process is running"
            raise NativeOrchestratorError(msg)

        handle.env.update(env)
        logger.debug("Updated environment for %s: %s", handle_id, list(env.keys()))

    async def apply_resource_limits(
        self,
        handle_id: str,
        cpu_seconds: int | None = None,
        memory_mb: int | None = None,
    ) -> None:
        """Apply resource limits to a workspace via environment variables.

        Note: Actual enforcement depends on system capabilities. This sets
        environment variables that tools can respect (e.g., via ulimit).

        Args:
            handle_id: The workspace handle ID.
            cpu_seconds: CPU time limit in seconds.
            memory_mb: Memory limit in megabytes.

        Raises:
            NativeOrchestratorError: If handle doesn't exist.
        """
        self._get_handle(handle_id)

        env_updates = {}
        if cpu_seconds is not None:
            env_updates["CPU_SECONDS"] = str(cpu_seconds)
        if memory_mb is not None:
            env_updates["MEMORY_MB"] = str(memory_mb)

        if env_updates:
            await self.set_workspace_env(handle_id, env_updates)
            logger.info("Applied resource limits to %s: %s", handle_id, env_updates)
