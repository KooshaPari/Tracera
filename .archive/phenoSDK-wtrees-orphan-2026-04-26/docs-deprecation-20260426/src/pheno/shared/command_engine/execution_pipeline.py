"""Command execution pipeline and workflow management.

Manages command execution workflows, process orchestration, and execution lifecycle
management.
"""

from __future__ import annotations

import asyncio
import json
import logging
import os
import shutil
import tempfile
from contextlib import asynccontextmanager
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    import subprocess
    from collections.abc import Callable

logger = logging.getLogger(__name__)


class CommandStatus(Enum):
    """
    Status of command execution.
    """

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class OutputFormat(Enum):
    """
    Output format for command results.
    """

    TEXT = "text"
    JSON = "json"
    TABLE = "table"
    YAML = "yaml"
    XML = "xml"


@dataclass
class CommandResult:
    """
    Result of command execution.
    """

    status: CommandStatus
    return_code: int
    stdout: str = ""
    stderr: str = ""
    output: Any = None
    metadata: dict[str, Any] = field(default_factory=dict)
    duration: float = 0.0
    error: Exception | None = None


@dataclass
class CommandConfig:
    """
    Configuration for command execution.
    """

    timeout: float | None = None
    cwd: Path | None = None
    env: dict[str, str] | None = None
    shell: bool = False
    capture_output: bool = True
    text: bool = True
    encoding: str = "utf-8"
    output_format: OutputFormat = OutputFormat.TEXT
    validate_output: bool = True
    retry_count: int = 0
    retry_delay: float = 1.0


class ExecutionPipeline:
    """
    Manages command execution workflows and process orchestration.
    """

    def __init__(self):
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        self._running_processes: dict[str, subprocess.Popen] = {}
        self._process_lock = asyncio.Lock()
        self._execution_hooks: dict[str, list[Callable]] = {
            "pre_execute": [],
            "post_execute": [],
            "on_error": [],
            "on_success": [],
        }

    async def execute_command(
        self,
        command: str | list[str],
        config: CommandConfig,
        process_id: str | None = None,
    ) -> CommandResult:
        """Execute a command with full pipeline orchestration.

        Args:
            command: Command to execute (string or list)
            config: Command configuration
            process_id: Optional process identifier

        Returns:
            CommandResult with execution outcome
        """
        start_time = asyncio.get_event_loop().time()
        process_id = process_id or f"cmd_{id(command)}"

        try:
            # Run pre-execution hooks
            await self._run_hooks("pre_execute", command, config, process_id)

            # Prepare environment and context
            env = self._prepare_environment(config)
            cmd_args = self._prepare_command(command, config)

            self.logger.info(
                f"Executing command: {' '.join(cmd_args) if isinstance(cmd_args, list) else cmd_args}",
            )

            # Execute command process
            result = await self._execute_process(cmd_args, config, env, process_id, start_time)

            # Run post-execution hooks
            await self._run_hooks("post_execute", result, command, config, process_id)

            # Run success hooks if successful
            if result.status == CommandStatus.COMPLETED:
                await self._run_hooks("on_success", result, command, config, process_id)

            return result

        except Exception as e:
            duration = asyncio.get_event_loop().time() - start_time
            self.logger.exception(f"Command execution failed: {e}")

            # Create error result
            error_result = CommandResult(
                status=CommandStatus.FAILED,
                return_code=1,
                error=e,
                duration=duration,
                metadata={
                    "process_id": process_id,
                    "command": command,
                    "error": str(e),
                },
            )

            # Run error hooks
            await self._run_hooks("on_error", error_result, e, command, config, process_id)

            return error_result

        finally:
            # Clean up process tracking
            async with self._process_lock:
                self._running_processes.pop(process_id, None)

    async def _execute_process(
        self,
        cmd_args: str | list[str],
        config: CommandConfig,
        env: dict[str, str],
        process_id: str,
        start_time: float,
    ) -> CommandResult:
        """
        Execute the actual subprocess.
        """
        # Create subprocess
        process = await asyncio.create_subprocess_exec(
            *cmd_args,
            stdout=asyncio.subprocess.PIPE if config.capture_output else None,
            stderr=asyncio.subprocess.PIPE if config.capture_output else None,
            cwd=config.cwd,
            env=env,
            shell=config.shell,
        )

        # Track running process
        async with self._process_lock:
            self._running_processes[process_id] = process

        # Wait for completion with timeout
        try:
            stdout, stderr = await asyncio.wait_for(process.communicate(), timeout=config.timeout)
        except TimeoutError:
            process.kill()
            await process.wait()
            raise TimeoutError(f"Command timed out after {config.timeout} seconds")

        # Calculate duration
        duration = asyncio.get_event_loop().time() - start_time

        # Decode output
        stdout_text = stderr_text = ""
        if config.capture_output:
            stdout_text = stdout.decode(config.encoding) if stdout else ""
            stderr_text = stderr.decode(config.encoding) if stderr else ""

        # Create result
        result = CommandResult(
            status=CommandStatus.COMPLETED if process.returncode == 0 else CommandStatus.FAILED,
            return_code=process.returncode or 0,
            stdout=stdout_text,
            stderr=stderr_text,
            duration=duration,
            metadata={
                "process_id": process_id,
                "command": cmd_args,
                "timeout": config.timeout,
            },
        )

        # Format output
        result.output = self._format_output(result, config)

        return result

    def _prepare_environment(self, config: CommandConfig) -> dict[str, str]:
        """
        Prepare environment for subprocess execution.
        """
        env = os.environ.copy()

        # Add custom environment variables
        if config.env:
            env.update(config.env)

        # Ensure PATH is properly set
        if "PATH" not in env:
            env["PATH"] = os.environ.get("PATH", "")

        return env

    def _prepare_command(
        self, command: str | list[str], config: CommandConfig,
    ) -> str | list[str]:
        """
        Prepare command for execution.
        """
        if isinstance(command, str):
            return command.split() if not config.shell else command
        return command

    def _format_output(self, result: CommandResult, config: CommandConfig) -> Any:
        """
        Format command output according to configuration.
        """
        if not config.capture_output or not result.stdout:
            return result.stdout

        if config.output_format == OutputFormat.JSON:
            try:
                return json.loads(result.stdout)
            except json.JSONDecodeError:
                return {"raw": result.stdout, "error": "Invalid JSON"}

        elif config.output_format == OutputFormat.YAML:
            try:
                import yaml

                return yaml.safe_load(result.stdout)
            except ImportError:
                return {"raw": result.stdout, "error": "YAML not available"}
            except yaml.YAMLError:
                return {"raw": result.stdout, "error": "Invalid YAML"}

        elif config.output_format == OutputFormat.TABLE:
            # Simple table format
            lines = result.stdout.strip().split("\n")
            if lines and lines[0]:
                headers = lines[0].split()
                rows = [line.split() for line in lines[1:] if line.strip()]
                return {"headers": headers, "rows": rows}
            return {"raw": result.stdout}

        else:
            return result.stdout

    async def execute_with_retry(
        self,
        command: str | list[str],
        config: CommandConfig,
        process_id: str | None = None,
    ) -> CommandResult:
        """Execute command with retry logic.

        Args:
            command: Command to execute
            config: Command configuration
            process_id: Optional process identifier

        Returns:
            CommandResult with final execution outcome
        """
        last_result = None

        for attempt in range(config.retry_count + 1):
            if attempt > 0:
                self.logger.info(f"Retry attempt {attempt}/{config.retry_count}")
                await asyncio.sleep(config.retry_delay)

            result = await self.execute_command(command, config, process_id)

            if result.status == CommandStatus.COMPLETED:
                return result

            last_result = result

        return last_result or CommandResult(
            status=CommandStatus.FAILED, return_code=1, error=Exception("All retry attempts failed"),
        )

    async def cancel_process(self, process_id: str) -> bool:
        """Cancel a running process.

        Args:
            process_id: Process identifier to cancel

        Returns:
            True if process was cancelled, False if not found
        """
        async with self._process_lock:
            process = self._running_processes.get(process_id)
            if process:
                process.terminate()
                try:
                    await asyncio.wait_for(process.wait(), timeout=5.0)
                except TimeoutError:
                    process.kill()
                    await process.wait()
                return True
            return False

    async def list_running_processes(self) -> list[str]:
        """List currently running process IDs.

        Returns:
            List of running process IDs
        """
        async with self._process_lock:
            return list(self._running_processes.keys())

    def add_hook(self, event: str, hook: Callable) -> None:
        """Add a hook for execution events.

        Args:
            event: Event name ('pre_execute', 'post_execute', 'on_error', 'on_success')
            hook: Hook function to add
        """
        if event not in self._execution_hooks:
            raise ValueError(f"Invalid hook event: {event}")

        self._execution_hooks[event].append(hook)
        self.logger.debug(f"Added {event} hook: {hook}")

    def remove_hook(self, event: str, hook: Callable) -> bool:
        """Remove a hook.

        Args:
            event: Event name
            hook: Hook function to remove

        Returns:
            True if hook was removed, False if not found
        """
        if event in self._execution_hooks and hook in self._execution_hooks[event]:
            self._execution_hooks[event].remove(hook)
            self.logger.debug(f"Removed {event} hook: {hook}")
            return True
        return False

    async def _run_hooks(self, event: str, *args, **kwargs) -> None:
        """
        Run hooks for an event.
        """
        for hook in self._execution_hooks.get(event, []):
            try:
                if asyncio.iscoroutinefunction(hook):
                    await hook(*args, **kwargs)
                else:
                    hook(*args, **kwargs)
            except Exception as e:
                self.logger.warning(f"Hook {hook} failed for event {event}: {e}")


class ProcessManager:
    """
    Manages system processes and resource allocation.
    """

    def __init__(self):
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        self._managed_processes: dict[str, dict[str, Any]] = {}
        self._resource_limits: dict[str, int] = {}

    def set_resource_limit(self, resource: str, limit: int) -> None:
        """Set resource limit for process management.

        Args:
            resource: Resource name (e.g., 'concurrent_processes', 'memory_mb')
            limit: Maximum limit value
        """
        self._resource_limits[resource] = limit
        self.logger.info(f"Set resource limit: {resource} = {limit}")

    async def execute_batch(
        self, commands: list[str | list[str]], config: CommandConfig, max_concurrent: int = 5,
    ) -> list[CommandResult]:
        """Execute a batch of commands with concurrency control.

        Args:
            commands: List of commands to execute
            config: Configuration for all commands
            max_concurrent: Maximum concurrent executions

        Returns:
            List of command results in order
        """
        semaphore = asyncio.Semaphore(max_concurrent)
        pipeline = ExecutionPipeline()

        async def execute_single_command(
            command: str | list[str], index: int,
        ) -> tuple[int, CommandResult]:
            async with semaphore:
                process_id = f"batch_{index}_{id(command)}"
                result = await pipeline.execute_command(command, config, process_id)
                return index, result

        # Create tasks for all commands
        tasks = [execute_single_command(command, i) for i, command in enumerate(commands)]

        # Execute all tasks
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Process results and maintain order
        ordered_results = [None] * len(commands)
        for item in results:
            if isinstance(item, Exception):
                self.logger.error(f"Batch execution error: {item}")
                continue
            if isinstance(item, tuple) and len(item) == 2:
                index, result = item
                ordered_results[index] = result

        return ordered_results

    @asynccontextmanager
    async def temporary_directory(self) -> Path:
        """Create a temporary directory for command execution.

        Yields:
            Path to temporary directory
        """
        temp_dir = Path(tempfile.mkdtemp())
        try:
            yield temp_dir
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)

    async def monitor_system_resources(self) -> dict[str, Any]:
        """Monitor system resource usage.

        Returns:
            Dictionary with resource usage information
        """
        try:
            # Get basic system info
            import psutil

            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage("/")

            return {
                "cpu_percent": cpu_percent,
                "memory_total_mb": memory.total / (1024 * 1024),
                "memory_available_mb": memory.available / (1024 * 1024),
                "memory_percent": memory.percent,
                "disk_total_gb": disk.total / (1024 * 1024 * 1024),
                "disk_free_gb": disk.free / (1024 * 1024 * 1024),
                "disk_percent": (disk.used / disk.total) * 100,
            }
        except ImportError:
            self.logger.warning("psutil not available for system monitoring")
            return {"error": "psutil not available"}
        except Exception as e:
            self.logger.exception(f"System monitoring failed: {e}")
            return {"error": str(e)}
