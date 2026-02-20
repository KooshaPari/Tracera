"""Docker SDK for Python - Comprehensive Async Examples.

Complete production-ready patterns for container orchestration.
"""

import asyncio
import contextlib
import logging
import signal
from collections.abc import AsyncGenerator
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
from typing import Any

try:
    import aiodocker
except ImportError:
    aiodocker = None

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


# ============================================================================
# Data Models
# ============================================================================


class ContainerStatus(Enum):
    """Container execution status."""

    CREATED = "created"
    RUNNING = "running"
    STOPPED = "stopped"
    FAILED = "failed"
    UNKNOWN = "unknown"


@dataclass
class ContainerConfig:
    """Container configuration."""

    image: str
    command: str | None = None
    name: str | None = None
    environment: dict[str, str] | None = None
    volumes: dict[str, dict[str, str]] | None = None
    user: str = "1000"
    memory_limit: str = "512m"
    cpu_limit: float = 1.0
    timeout: int = 300
    read_only: bool = False
    cap_drop: list[str] = None
    security_opt: list[str] = None

    def __post_init__(self) -> None:
        """Set defaults."""
        if self.cap_drop is None:
            self.cap_drop = ["ALL"]
        if self.security_opt is None:
            self.security_opt = ["no-new-privileges:true"]


@dataclass
class ExecutionResult:
    """Result of container execution."""

    container_id: str
    exit_code: int
    logs: str
    error: str | None = None
    duration: float = 0.0
    success: bool = False
    timed_out: bool = False


# ============================================================================
# Secure Container Manager
# ============================================================================


class SecureAsyncContainerManager:
    """Secure async container management with hardened defaults.

    Features:
    - Non-root execution (UID 1000)
    - Dropped capabilities
    - Read-only filesystem
    - Resource limits
    - Timeout management
    - Graceful shutdown
    """

    def __init__(self, max_concurrent: int = 5) -> None:
        """Initialize container manager.

        Args:
            max_concurrent: Maximum concurrent operations
        """
        self.docker: aiodocker.Docker | None = None
        self.semaphore = asyncio.Semaphore(max_concurrent)
        self.running_containers: dict[str, aiodocker.containers.DockerContainer] = {}
        self._shutdown = asyncio.Event()
        self._register_signals()

    def _register_signals(self) -> None:
        """Register signal handlers for graceful shutdown."""
        signal.signal(signal.SIGTERM, self._signal_handler)
        signal.signal(signal.SIGINT, self._signal_handler)

    def _signal_handler(self, signum: Any, _frame: Any) -> None:
        """Handle shutdown signal."""
        logger.info("Received signal %s, initiating shutdown...", signum)
        self._shutdown.set()

    async def __aenter__(self) -> None:
        """Context manager entry."""
        self.docker = aiodocker.Docker()
        return self

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Context manager exit."""
        await self.cleanup()

    async def cleanup(self) -> None:
        """Cleanup all resources."""
        logger.info("Cleaning up container manager...")

        # Stop all running containers
        for container_id, container in list(self.running_containers.items()):
            try:
                await self._stop_container(container, timeout=5)
            except Exception as e:
                logger.exception("Error stopping container %s: %s", container_id, e)

        # Close Docker client
        if self.docker:
            await self.docker.close()

    async def create_container(self, config: ContainerConfig) -> aiodocker.containers.DockerContainer:
        """Create container with secure defaults.

        Args:
            config: Container configuration

        Returns:
            Created container

        Raises:
            RuntimeError: If Docker client not initialized
        """
        if not self.docker:
            msg = "Docker client not initialized"
            raise RuntimeError(msg)

        # Build container configuration
        docker_config = {
            "Image": config.image,
            "User": config.user,
            "Cmd": [config.command] if config.command else None,
            "Env": self._format_env(config.environment or {}),
            "Volumes": config.volumes or {},
            "HostConfig": {
                "CapDrop": config.cap_drop,
                "SecurityOpt": config.security_opt,
                "Memory": self._parse_memory(config.memory_limit),
                "NanoCpus": int(config.cpu_limit * 1e9),
                "ReadonlyRootfs": config.read_only,
                "Tmpfs": {"/tmp": "size=100m,mode=1777", "/run": "size=50m,mode=1777"} if config.read_only else None,
            },
        }

        # Remove None values
        docker_config = {k: v for k, v in docker_config.items() if v is not None}
        docker_config["HostConfig"] = {k: v for k, v in docker_config["HostConfig"].items() if v is not None}

        container = await self.docker.containers.create_or_replace(config=docker_config, name=config.name)

        logger.info("Created container: %s (%s)", container.id[:12], config.name)
        return container

    async def run_container(self, config: ContainerConfig) -> ExecutionResult:
        """Create and run container with timeout and cleanup.

        Args:
            config: Container configuration

        Returns:
            ExecutionResult with logs and exit code
        """
        async with self.semaphore:
            container = None
            start_time = datetime.now()

            try:
                # Create container
                container = await self.create_container(config)
                self.running_containers[container.id] = container

                # Start container
                await container.start()
                logger.info("Started container: %s", container.id[:12])

                # Wait for completion with timeout
                exit_code = await asyncio.wait_for(container.wait(), timeout=config.timeout)

                # Get logs
                logs = await self._get_logs(container)

                duration = (datetime.now() - start_time).total_seconds()

                result = ExecutionResult(
                    container_id=container.id,
                    exit_code=exit_code.get("StatusCode", 0),
                    logs=logs,
                    duration=duration,
                    success=exit_code.get("StatusCode", 0) == 0,
                    timed_out=False,
                )

                logger.info(
                    f"Container {container.id[:12]} completed (exit={result.exit_code}, duration={duration:.2f}s)",
                )

                return result

            except TimeoutError:
                logger.warning(
                    f"Container {container.id[:12] if container else 'unknown'} timed out after {config.timeout}s",
                )

                if container:
                    await self._stop_container(container, timeout=5, force=True)
                    logs = await self._get_logs(container)
                else:
                    logs = ""

                duration = (datetime.now() - start_time).total_seconds()

                return ExecutionResult(
                    container_id=container.id if container else "",
                    exit_code=-1,
                    logs=logs,
                    duration=duration,
                    error=f"Container timed out after {config.timeout}s",
                    success=False,
                    timed_out=True,
                )

            except Exception as e:
                logger.exception("Error running container: %s", e)

                if container:
                    with contextlib.suppress(Exception):
                        await self._stop_container(container, timeout=5, force=True)

                duration = (datetime.now() - start_time).total_seconds()

                return ExecutionResult(
                    container_id=container.id if container else "",
                    exit_code=-1,
                    logs="",
                    duration=duration,
                    error=str(e),
                    success=False,
                    timed_out=False,
                )

            finally:
                # Cleanup container
                if container:
                    try:
                        await container.delete(force=True, v=True)
                        if container.id in self.running_containers:
                            del self.running_containers[container.id]
                    except Exception as e:
                        logger.exception("Error cleaning up container: %s", e)

    async def _stop_container(
        self,
        container: aiodocker.containers.DockerContainer,
        timeout: int = 10,
        force: bool = False,
    ) -> None:
        """Stop container gracefully or forcefully.

        Args:
            container: Container to stop
            timeout: Graceful stop timeout
            force: Force kill if graceful fails
        """
        try:
            await container.stop(timeout=timeout)
            logger.debug("Stopped container gracefully")
        except Exception:
            if force:
                try:
                    await container.kill()
                    logger.debug("Force killed container")
                except Exception:
                    pass
            else:
                raise

    async def _get_logs(self, container: aiodocker.containers.DockerContainer) -> str:
        """Get container logs.

        Args:
            container: Target container

        Returns:
            Combined stdout/stderr logs
        """
        try:
            async with container.log(stdout=True, stderr=True) as logs:
                output = [line.decode("utf-8") async for line in logs]
                return "".join(output)
        except Exception as e:
            logger.exception("Error getting logs: %s", e)
            return ""

    async def stream_logs(
        self,
        container: aiodocker.containers.DockerContainer,
        follow: bool = True,
    ) -> AsyncGenerator[str, None]:
        """Stream logs from container in real-time.

        Args:
            container: Target container
            follow: Continue streaming until stop

        Yields:
            Log lines
        """
        try:
            async with container.log(stdout=True, stderr=True, follow=follow) as logs:
                async for line in logs:
                    yield line.decode("utf-8").rstrip()
        except Exception as e:
            logger.exception("Error streaming logs: %s", e)

    @staticmethod
    def _format_env(env: dict[str, str]) -> list[str]:
        """Format environment variables as list."""
        return [f"{k}={v}" for k, v in env.items()]

    @staticmethod
    def _parse_memory(memory_str: str) -> int:
        """Parse memory string to bytes.

        Examples:
            "512m" -> 536870912
            "1g" -> 1073741824
        """
        units = {"b": 1, "k": 1024, "m": 1024**2, "g": 1024**3}
        memory_str = memory_str.lower().strip()

        for unit, multiplier in units.items():
            if memory_str.endswith(unit):
                return int(float(memory_str[:-1]) * multiplier)

        return int(memory_str)  # Assume bytes


# ============================================================================
# Batch Operations Manager
# ============================================================================


class AsyncBatchOperationManager(SecureAsyncContainerManager):
    """Manage multiple containers with concurrent execution and aggregated results."""

    async def run_batch(
        self,
        configs: list[ContainerConfig],
        max_concurrent: int | None = None,
    ) -> list[ExecutionResult]:
        """Run multiple containers concurrently.

        Args:
            configs: List of container configurations
            max_concurrent: Override max concurrent limit

        Returns:
            List of execution results

        Raises:
            Exception: If any container fails and not handled
        """
        if max_concurrent:
            self.semaphore = asyncio.Semaphore(max_concurrent)

        logger.info(f"Starting batch of {len(configs)} containers")
        start_time = datetime.now()

        # Run all containers concurrently
        results = await asyncio.gather(*[self.run_container(config) for config in configs], return_exceptions=False)

        duration = (datetime.now() - start_time).total_seconds()

        # Summary
        successful = sum(1 for r in results if r.success)
        failed = sum(1 for r in results if not r.success)
        timed_out = sum(1 for r in results if r.timed_out)

        logger.info(
            f"Batch completed: {successful} succeeded, {failed} failed, "
            f"{timed_out} timed out (duration={duration:.2f}s)",
        )

        return results

    async def run_with_retry(
        self,
        config: ContainerConfig,
        max_retries: int = 3,
        backoff_factor: float = 2.0,
    ) -> ExecutionResult:
        """Run container with automatic retry on failure.

        Args:
            config: Container configuration
            max_retries: Maximum retry attempts
            backoff_factor: Exponential backoff multiplier

        Returns:
            ExecutionResult from successful run or last attempt
        """
        last_result = None
        wait_time = 1.0

        for attempt in range(max_retries + 1):
            logger.info(f"Container attempt {attempt + 1}/{max_retries + 1}")

            result = await self.run_container(config)
            last_result = result

            if result.success:
                logger.info(f"Container succeeded on attempt {attempt + 1}")
                return result

            if attempt < max_retries:
                logger.warning(f"Container failed on attempt {attempt + 1}, retrying in {wait_time:.1f}s...")
                await asyncio.sleep(wait_time)
                wait_time *= backoff_factor

        logger.error(f"Container failed after {max_retries + 1} attempts")
        return last_result

    async def run_until_success(
        self,
        config: ContainerConfig,
        max_duration: int = 600,
        check_interval: float = 1.0,
    ) -> ExecutionResult:
        """Run container repeatedly until success.

        Args:
            config: Container configuration
            max_duration: Maximum total duration
            check_interval: Interval between checks

        Returns:
            ExecutionResult from successful run

        Raises:
            TimeoutError: If max_duration exceeded
        """
        start_time = datetime.now()
        deadline = start_time + timedelta(seconds=max_duration)
        attempt = 0

        while datetime.now() < deadline:
            attempt += 1
            logger.info("Attempt %s...", attempt)

            result = await self.run_container(config)

            if result.success:
                (datetime.now() - start_time).total_seconds()
                logger.info("Succeeded on attempt %s (duration={duration:.2f}s)", attempt)
                return result

            # Check timeout
            remaining = (deadline - datetime.now()).total_seconds()
            if remaining <= 0:
                msg = f"Max duration {max_duration}s exceeded"
                raise TimeoutError(msg)

            # Wait before retry
            await asyncio.sleep(min(check_interval, remaining))

        msg = f"Max duration {max_duration}s exceeded"
        raise TimeoutError(msg)


# ============================================================================
# Graceful Shutdown Manager
# ============================================================================


class GracefulShutdownManager:
    """Manage graceful shutdown of async operations.

    Handles SIGTERM/SIGINT and ensures proper cleanup.
    """

    def __init__(self, timeout: int = 30) -> None:
        """Initialize shutdown manager.

        Args:
            timeout: Graceful shutdown timeout
        """
        self.timeout = timeout
        self._shutdown_event = asyncio.Event()
        self._tasks: list[asyncio.Task] = []
        self._register_signals()

    def _register_signals(self) -> None:
        """Register signal handlers."""
        signal.signal(signal.SIGTERM, self._signal_handler)
        signal.signal(signal.SIGINT, self._signal_handler)

    def _signal_handler(self, signum: Any, _frame: Any) -> None:
        """Signal handler callback."""
        logger.info("Received signal %s, initiating graceful shutdown...", signum)
        self._shutdown_event.set()

    async def wait_for_shutdown(self) -> None:
        """Wait for shutdown signal."""
        await self._shutdown_event.wait()

    async def run_until_shutdown(self, coroutine: Any) -> Any:
        """Run coroutine until shutdown signal.

        Args:
            coroutine: Async coroutine to run

        Returns:
            Result from coroutine

        Raises:
            Exception: If coroutine fails or times out
        """
        task = asyncio.create_task(coroutine)
        self._tasks.append(task)

        try:
            done, pending = await asyncio.wait(
                [task, asyncio.create_task(self.wait_for_shutdown())],
                return_when=asyncio.FIRST_COMPLETED,
            )

            # Cancel pending
            for t in pending:
                t.cancel()

            # Get result
            return done.pop().result()

        except asyncio.CancelledError:
            logger.info("Operation cancelled")
            raise
        except Exception as e:
            logger.exception("Error in operation: %s", e)
            raise

    async def shutdown(self) -> None:
        """Shutdown all tasks gracefully."""
        logger.info(f"Shutting down {len(self._tasks)} tasks...")

        # Cancel all tasks
        for task in self._tasks:
            task.cancel()

        # Wait for cancellation with timeout
        try:
            await asyncio.wait_for(asyncio.gather(*self._tasks, return_exceptions=True), timeout=self.timeout)
        except TimeoutError:
            logger.warning("Shutdown timeout after %ss, forcing termination", self.timeout)


# ============================================================================
# Example Usage
# ============================================================================


async def example_simple() -> None:
    """Simple example: run single container."""
    logger.info("=== Simple Example ===")

    config = ContainerConfig(
        image="python:3.11-slim",
        command='python -c "print(\\"Hello from Docker\\")"',
        name="simple-example",
    )

    async with SecureAsyncContainerManager() as manager:
        result = await manager.run_container(config)
        logger.info("Exit code: %s", result.exit_code)
        logger.info("Output:\n%s", result.logs)


async def example_batch() -> None:
    """Batch example: run multiple containers."""
    logger.info("=== Batch Example ===")

    configs = [
        ContainerConfig(
            image="python:3.11-slim",
            command=f'python -c "print(\\"Task {i}\\")"',
            name=f"batch-task-{i}",
            timeout=60,
        )
        for i in range(5)
    ]

    async with AsyncBatchOperationManager(max_concurrent=3) as manager:
        results = await manager.run_batch(configs)

        for i, result in enumerate(results):
            logger.info(
                "Task %s: exit=%s, success=%s, duration={result.duration:.2f}s", i, result.exit_code, result.success
            )


async def example_retry() -> None:
    """Retry example: run with automatic retry."""
    logger.info("=== Retry Example ===")

    config = ContainerConfig(
        image="python:3.11-slim",
        command='python -c "import sys; sys.exit(0)"',
        name="retry-example",
        timeout=30,
    )

    async with SecureAsyncContainerManager() as manager:
        result = await manager.run_with_retry(config, max_retries=2)
        logger.info("Final result: exit=%s, success=%s", result.exit_code, result.success)


async def example_streaming() -> None:
    """Streaming example: stream logs in real-time."""
    logger.info("=== Streaming Example ===")

    config = ContainerConfig(
        image="python:3.11-slim",
        command='python -c "for i in range(5): print(f\\"Line {i}\\")"',
        name="streaming-example",
    )

    async with SecureAsyncContainerManager() as manager:
        container = await manager.create_container(config)
        await container.start()

        logger.info("Streaming logs:")
        async for line in manager.stream_logs(container):
            logger.info("  %s", line)

        await container.wait()
        await container.delete(force=True)


async def example_timeout() -> None:
    """Timeout example: handle container timeout."""
    logger.info("=== Timeout Example ===")

    config = ContainerConfig(
        image="python:3.11-slim",
        command='python -c "import time; time.sleep(100)"',
        name="timeout-example",
        timeout=5,  # Very short timeout
    )

    async with SecureAsyncContainerManager() as manager:
        result = await manager.run_container(config)
        logger.info("Timed out: %s", result.timed_out)
        logger.info("Exit code: %s", result.exit_code)
        logger.info("Error: %s", result.error)


async def main() -> None:
    """Run all examples."""
    examples = [example_simple, example_batch, example_retry, example_streaming, example_timeout]

    for example in examples:
        try:
            await example()
        except Exception as e:
            logger.exception("Example failed: %s", e)

        logger.info("")


if __name__ == "__main__":
    asyncio.run(main())
