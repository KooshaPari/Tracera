"""
Bulkhead pattern implementation for resource isolation.
"""

from __future__ import annotations

import asyncio
from contextlib import asynccontextmanager, contextmanager, suppress
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

from pheno.logging.core.logger import get_logger

if TYPE_CHECKING:
    from collections.abc import Awaitable, Callable

logger = get_logger("pheno.resilience.bulkhead")


@dataclass(slots=True)
class BulkheadConfig:
    """
    Configuration for bulkhead pattern.
    """

    max_concurrent_calls: int = 10
    max_wait_time: float = 5.0  # seconds
    timeout: float | None = None  # seconds
    enable_monitoring: bool = True


class BulkheadFullError(Exception):
    """
    Raised when bulkhead is full and cannot accept more calls.
    """

    def __init__(self, bulkhead_name: str, max_concurrent: int, current_calls: int):
        self.bulkhead_name = bulkhead_name
        self.max_concurrent = max_concurrent
        self.current_calls = current_calls
        super().__init__(f"Bulkhead '{bulkhead_name}' is full ({current_calls}/{max_concurrent})")


class ResourcePool:
    """
    Manages a pool of resources with concurrency limits.
    """

    def __init__(self, name: str, config: BulkheadConfig):
        self.name = name
        self.config = config
        self._semaphore = asyncio.Semaphore(config.max_concurrent_calls)
        self._active_calls = 0
        self._total_calls = 0
        self._rejected_calls = 0
        self._lock = asyncio.Lock()

    async def acquire(self, timeout: float | None = None) -> bool:
        """
        Acquire a resource from the pool.
        """
        try:
            await asyncio.wait_for(
                self._semaphore.acquire(), timeout=timeout or self.config.max_wait_time,
            )

            async with self._lock:
                self._active_calls += 1
                self._total_calls += 1

            logger.debug(
                f"Acquired resource from pool '{self.name}' ({self._active_calls}/{self.config.max_concurrent_calls})",
            )
            return True

        except TimeoutError:
            async with self._lock:
                self._rejected_calls += 1

            logger.warning(f"Failed to acquire resource from pool '{self.name}' (timeout)")
            raise BulkheadFullError(self.name, self.config.max_concurrent_calls, self._active_calls)

    async def release(self) -> None:
        """
        Release a resource back to the pool.
        """
        self._semaphore.release()

        async with self._lock:
            self._active_calls = max(0, self._active_calls - 1)

        logger.debug(
            f"Released resource to pool '{self.name}' ({self._active_calls}/{self.config.max_concurrent_calls})",
        )

    @property
    def active_calls(self) -> int:
        """
        Get number of active calls.
        """
        return self._active_calls

    @property
    def available_calls(self) -> int:
        """
        Get number of available calls.
        """
        return self.config.max_concurrent_calls - self._active_calls

    def get_stats(self) -> dict[str, Any]:
        """
        Get pool statistics.
        """
        return {
            "name": self.name,
            "max_concurrent_calls": self.config.max_concurrent_calls,
            "active_calls": self._active_calls,
            "available_calls": self.available_calls,
            "total_calls": self._total_calls,
            "rejected_calls": self._rejected_calls,
            "utilization": (
                self._active_calls / self.config.max_concurrent_calls
                if self.config.max_concurrent_calls > 0
                else 0.0
            ),
        }


class Bulkhead:
    """
    Bulkhead pattern implementation for resource isolation.
    """

    def __init__(self, name: str, config: BulkheadConfig | None = None):
        self.name = name
        self.config = config or BulkheadConfig()
        self._pool = ResourcePool(name, self.config)
        self._monitoring_task: asyncio.Task | None = None
        self._shutdown_event = asyncio.Event()

    async def execute(self, func: Callable[..., Any], *args, **kwargs) -> Any:
        """
        Execute function through bulkhead.
        """
        return await self._execute_call(func, args, kwargs, is_async=False)

    async def execute_async(self, func: Callable[..., Awaitable[Any]], *args, **kwargs) -> Any:
        """
        Execute async function through bulkhead.
        """
        return await self._execute_call(func, args, kwargs, is_async=True)

    async def _execute_call(
        self, func: Callable[..., Any], args: tuple, kwargs: dict, is_async: bool,
    ) -> Any:
        """
        Execute a call through the bulkhead.
        """
        # Acquire resource
        await self._pool.acquire(timeout=self.config.timeout)

        try:
            # Execute function
            if is_async:
                result = await func(*args, **kwargs)
            else:
                result = func(*args, **kwargs)

            return result

        finally:
            # Always release resource
            await self._pool.release()

    @asynccontextmanager
    async def acquire_resource(self):
        """
        Context manager for acquiring bulkhead resources.
        """
        await self._pool.acquire(timeout=self.config.timeout)
        try:
            yield
        finally:
            await self._pool.release()

    @contextmanager
    def acquire_resource_sync(self):
        """
        Synchronous context manager for acquiring bulkhead resources.
        """
        # This is a simplified sync version - in practice, you'd need to handle
        # the async nature properly in a sync context
        raise NotImplementedError("Use acquire_resource() for async context")

    def get_stats(self) -> dict[str, Any]:
        """
        Get bulkhead statistics.
        """
        return self._pool.get_stats()

    async def start_monitoring(self) -> None:
        """
        Start monitoring task.
        """
        if not self.config.enable_monitoring or self._monitoring_task is not None:
            return

        self._monitoring_task = asyncio.create_task(self._monitoring_loop())
        logger.info(f"Started monitoring for bulkhead '{self.name}'")

    async def stop_monitoring(self) -> None:
        """
        Stop monitoring task.
        """
        if self._monitoring_task is None:
            return

        self._shutdown_event.set()
        self._monitoring_task.cancel()

        with suppress(asyncio.CancelledError):
            await self._monitoring_task

        self._monitoring_task = None
        logger.info(f"Stopped monitoring for bulkhead '{self.name}'")

    async def _monitoring_loop(self) -> None:
        """
        Monitoring loop.
        """
        while not self._shutdown_event.is_set():
            try:
                stats = self.get_stats()
                logger.debug(f"Bulkhead '{self.name}' stats: {stats}")

                # Check for high utilization
                if stats["utilization"] > 0.8:
                    logger.warning(
                        f"Bulkhead '{self.name}' high utilization: {stats['utilization']:.2%}",
                    )

                await asyncio.sleep(10.0)  # Check every 10 seconds

            except Exception as e:
                logger.exception(f"Error in bulkhead monitoring: {e}")
                await asyncio.sleep(5.0)


class BulkheadManager:
    """
    Manages multiple bulkheads.
    """

    def __init__(self):
        self._bulkheads: dict[str, Bulkhead] = {}
        self._monitoring_task: asyncio.Task | None = None
        self._shutdown_event = asyncio.Event()

    def create_bulkhead(self, name: str, config: BulkheadConfig | None = None) -> Bulkhead:
        """
        Create a new bulkhead.
        """
        if name in self._bulkheads:
            raise ValueError(f"Bulkhead '{name}' already exists")

        bulkhead = Bulkhead(name, config)
        self._bulkheads[name] = bulkhead

        logger.info(f"Created bulkhead '{name}'")
        return bulkhead

    def get_bulkhead(self, name: str) -> Bulkhead | None:
        """
        Get bulkhead by name.
        """
        return self._bulkheads.get(name)

    def remove_bulkhead(self, name: str) -> bool:
        """
        Remove bulkhead.
        """
        if name in self._bulkheads:
            asyncio.create_task(self._bulkheads[name].stop_monitoring())
            del self._bulkheads[name]
            logger.info(f"Removed bulkhead '{name}'")
            return True
        return False

    def list_bulkheads(self) -> list[str]:
        """
        List all bulkhead names.
        """
        return list(self._bulkheads.keys())

    def get_all_stats(self) -> dict[str, dict[str, Any]]:
        """
        Get statistics for all bulkheads.
        """
        return {name: bulkhead.get_stats() for name, bulkhead in self._bulkheads.items()}

    async def start_monitoring(self) -> None:
        """
        Start monitoring all bulkheads.
        """
        if self._monitoring_task is not None:
            return

        # Start monitoring for all bulkheads
        for bulkhead in self._bulkheads.values():
            await bulkhead.start_monitoring()

        self._monitoring_task = asyncio.create_task(self._manager_monitoring_loop())
        logger.info("Started bulkhead manager monitoring")

    async def stop_monitoring(self) -> None:
        """
        Stop monitoring all bulkheads.
        """
        if self._monitoring_task is None:
            return

        self._shutdown_event.set()
        self._monitoring_task.cancel()

        with suppress(asyncio.CancelledError):
            await self._monitoring_task

        # Stop monitoring for all bulkheads
        for bulkhead in self._bulkheads.values():
            await bulkhead.stop_monitoring()

        self._monitoring_task = None
        logger.info("Stopped bulkhead manager monitoring")

    async def _manager_monitoring_loop(self) -> None:
        """
        Manager-level monitoring loop.
        """
        while not self._shutdown_event.is_set():
            try:
                # Log overall stats
                stats = self.get_all_stats()
                logger.debug(f"Bulkhead manager stats: {stats}")

                await asyncio.sleep(30.0)  # Check every 30 seconds

            except Exception as e:
                logger.exception(f"Error in bulkhead manager monitoring: {e}")
                await asyncio.sleep(10.0)
