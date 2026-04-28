"""Core Command Engine Implementation.

Provides the main CommandEngine class that orchestrates command execution with
subprocess management, progress tracking, and error handling.
"""

import asyncio
import contextlib
import logging
import subprocess
import sys
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


class CommandStatus(Enum):
    """
    Status of a command execution.
    """

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class CommandStage:
    """
    Represents a stage in command execution.
    """

    name: str
    description: str
    status: CommandStatus = CommandStatus.PENDING
    start_time: datetime | None = None
    end_time: datetime | None = None
    logs: list[str] = field(default_factory=list)
    error: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def add_log(self, message: str) -> None:
        """
        Add a log message to this stage.
        """
        self.logs.append(f"[{datetime.now().strftime('%H:%M:%S')}] {message}")

    def set_error(self, error: str) -> None:
        """
        Set an error for this stage.
        """
        self.error = error
        self.status = CommandStatus.FAILED
        self.add_log(f"ERROR: {error}")

    def start(self) -> None:
        """
        Mark stage as started.
        """
        self.status = CommandStatus.RUNNING
        self.start_time = datetime.now()
        self.add_log(f"Starting {self.name}")

    def complete(self) -> None:
        """
        Mark stage as completed.
        """
        self.status = CommandStatus.COMPLETED
        self.end_time = datetime.now()
        self.add_log(f"Completed {self.name}")

    @property
    def duration(self) -> float | None:
        """
        Get stage duration in seconds.
        """
        if self.start_time and self.end_time:
            return (self.end_time - self.start_time).total_seconds()
        return None


@dataclass
class CommandResult:
    """
    Result of command execution.
    """

    success: bool
    exit_code: int
    stdout: str
    stderr: str
    duration: float
    stages: list[CommandStage]
    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def failed_stages(self) -> list[CommandStage]:
        """
        Get stages that failed.
        """
        return [stage for stage in self.stages if stage.status == CommandStatus.FAILED]

    @property
    def all_logs(self) -> list[str]:
        """
        Get all logs from all stages.
        """
        logs = []
        for stage in self.stages:
            logs.extend(stage.logs)
        return logs


class CommandEngine:
    """Unified command execution engine.

    Provides comprehensive command execution with subprocess management, progress
    tracking, error handling, and TUI integration.
    """

    def __init__(self, working_directory: Path | None = None):
        self.working_directory = working_directory or Path.cwd()
        self._callbacks: list[Callable[[CommandStage], None]] = []
        self._running_processes: dict[str, subprocess.Popen] = {}

    def add_callback(self, callback: Callable[[CommandStage], None]) -> None:
        """
        Add a progress callback.
        """
        self._callbacks.append(callback)

    def _trigger_callbacks(self, stage: CommandStage) -> None:
        """
        Trigger all registered callbacks.
        """
        for callback in self._callbacks:
            try:
                callback(stage)
            except Exception as e:
                logger.warning(f"Callback failed: {e}")

    async def run_command(
        self,
        command: str | list[str],
        *,
        working_directory: Path | None = None,
        environment: dict[str, str] | None = None,
        timeout: int | None = None,
        capture_output: bool = True,
        real_time_output: bool = False,
        stages: list[str] | None = None,
        progress_callback: Callable[[CommandStage], None] | None = None,
        **kwargs,
    ) -> CommandResult:
        """Run a command with full orchestration.

        Args:
            command: Command to run (string or list)
            working_directory: Working directory for command
            environment: Environment variables
            timeout: Command timeout in seconds
            capture_output: Whether to capture stdout/stderr
            real_time_output: Whether to show real-time output
            stages: List of stage names for progress tracking
            progress_callback: Callback for progress updates
            **kwargs: Additional arguments

        Returns:
            CommandResult with execution details
        """
        start_time = datetime.now()
        working_dir = working_directory or self.working_directory

        # Prepare command
        cmd_args = command.split() if isinstance(command, str) else command

        # Create stages
        command_stages = []
        if stages:
            for stage_name in stages:
                command_stages.append(
                    CommandStage(name=stage_name, description=f"Executing {stage_name}"),
                )
        else:
            command_stages.append(
                CommandStage(name="execute", description=f"Running: {' '.join(cmd_args)}"),
            )

        # Add progress callback
        if progress_callback:
            self.add_callback(progress_callback)

        try:
            # Execute command
            result = await self._execute_command(
                cmd_args,
                working_dir=working_dir,
                environment=environment,
                timeout=timeout,
                capture_output=capture_output,
                real_time_output=real_time_output,
                stages=command_stages,
            )

            duration = (datetime.now() - start_time).total_seconds()

            return CommandResult(
                success=result.returncode == 0,
                exit_code=result.returncode,
                stdout=result.stdout or "",
                stderr=result.stderr or "",
                duration=duration,
                stages=command_stages,
                metadata={
                    "command": cmd_args,
                    "working_directory": str(working_dir),
                    "environment": environment or {},
                },
            )

        except Exception as e:
            duration = (datetime.now() - start_time).total_seconds()
            error_stage = CommandStage(name="error", description="Command execution failed")
            error_stage.set_error(str(e))
            command_stages.append(error_stage)

            return CommandResult(
                success=False,
                exit_code=-1,
                stdout="",
                stderr=str(e),
                duration=duration,
                stages=command_stages,
                metadata={
                    "command": cmd_args,
                    "working_directory": str(working_dir),
                    "error": str(e),
                },
            )

    async def _execute_command(
        self,
        cmd_args: list[str],
        *,
        working_dir: Path,
        environment: dict[str, str] | None = None,
        timeout: int | None = None,
        capture_output: bool = True,
        real_time_output: bool = False,
        stages: list[CommandStage],
    ) -> subprocess.CompletedProcess:
        """
        Execute the actual command.
        """

        # Prepare environment
        env = environment or {}
        full_env = {**sys.environ, **env}

        # Start first stage
        if stages:
            stages[0].start()
            self._trigger_callbacks(stages[0])

        try:
            # Configure subprocess
            kwargs = {
                "cwd": str(working_dir),
                "env": full_env,
            }

            if capture_output and not real_time_output:
                kwargs["stdout"] = subprocess.PIPE
                kwargs["stderr"] = subprocess.PIPE
                kwargs["text"] = True

            # Execute command
            process = await asyncio.create_subprocess_exec(*cmd_args, **kwargs)

            # Handle real-time output
            if real_time_output:
                stdout, stderr = await self._handle_real_time_output(process, stages)
            else:
                stdout, stderr = await process.communicate()

            # Complete stages
            if stages:
                stages[0].complete()
                self._trigger_callbacks(stages[0])

            return subprocess.CompletedProcess(
                args=cmd_args, returncode=process.returncode, stdout=stdout, stderr=stderr,
            )

        except TimeoutError:
            if stages:
                stages[0].set_error(f"Command timed out after {timeout} seconds")
                self._trigger_callbacks(stages[0])
            raise
        except Exception as e:
            if stages:
                stages[0].set_error(str(e))
                self._trigger_callbacks(stages[0])
            raise

    async def _handle_real_time_output(
        self, process: asyncio.subprocess.Process, stages: list[CommandStage],
    ) -> tuple[str, str]:
        """
        Handle real-time output from subprocess.
        """
        stdout_lines = []
        stderr_lines = []

        async def read_stream(stream, lines, prefix=""):
            """
            Read from a stream and collect lines.
            """
            while True:
                line = await stream.readline()
                if not line:
                    break
                line_str = line.decode().rstrip()
                lines.append(line_str)
                if stages:
                    stages[0].add_log(f"{prefix}{line_str}")

        # Read stdout and stderr concurrently
        await asyncio.gather(
            read_stream(process.stdout, stdout_lines, "[STDOUT] "),
            read_stream(process.stderr, stderr_lines, "[STDERR] "),
        )

        return "\n".join(stdout_lines), "\n".join(stderr_lines)

    async def run_parallel_commands(
        self,
        commands: list[dict[str, Any]],
        *,
        max_concurrent: int = 3,
        progress_callback: Callable[[CommandStage], None] | None = None,
    ) -> list[CommandResult]:
        """Run multiple commands in parallel.

        Args:
            commands: List of command dictionaries
            max_concurrent: Maximum concurrent commands
            progress_callback: Callback for progress updates

        Returns:
            List of CommandResult objects
        """
        semaphore = asyncio.Semaphore(max_concurrent)

        async def run_single_command(cmd_dict: dict[str, Any]) -> CommandResult:
            async with semaphore:
                return await self.run_command(**cmd_dict, progress_callback=progress_callback)

        tasks = [run_single_command(cmd) for cmd in commands]
        return await asyncio.gather(*tasks)

    def cancel_command(self, command_id: str) -> bool:
        """
        Cancel a running command.
        """
        if command_id in self._running_processes:
            process = self._running_processes[command_id]
            process.terminate()
            del self._running_processes[command_id]
            return True
        return False

    def get_running_commands(self) -> list[str]:
        """
        Get list of running command IDs.
        """
        return list(self._running_processes.keys())

    def cleanup(self) -> None:
        """
        Clean up any running processes.
        """
        for process in self._running_processes.values():
            with contextlib.suppress(Exception):
                process.terminate()
        self._running_processes.clear()
