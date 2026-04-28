"""
Circuit breaker pattern implementation for fault tolerance.
"""

from __future__ import annotations

import asyncio
import contextlib
import threading
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import TYPE_CHECKING, Any

from pheno.logging.core.logger import get_logger

if TYPE_CHECKING:
    from collections.abc import Awaitable, Callable

logger = get_logger("pheno.resilience.circuit_breaker")


class CircuitBreakerState(Enum):
    """
    States of the circuit breaker.
    """

    CLOSED = "closed"  # Normal operation
    OPEN = "open"  # Circuit is open, calls fail fast
    HALF_OPEN = "half_open"  # Testing if service is back


@dataclass(slots=True)
class CircuitBreakerConfig:
    """
    Configuration for circuit breaker.
    """

    # Failure threshold
    failure_threshold: int = 5
    failure_window: float = 60.0  # seconds

    # Recovery settings
    recovery_timeout: float = 30.0  # seconds
    success_threshold: int = 3  # successes needed to close from half-open

    # Monitoring
    enable_monitoring: bool = True
    monitoring_interval: float = 10.0  # seconds

    # Custom error handling
    exception_types: tuple = (Exception,)
    ignore_exceptions: tuple = ()

    # Callbacks
    on_state_change: Callable[[CircuitBreakerState, CircuitBreakerState], None] | None = None
    on_failure: Callable[[Exception], None] | None = None
    on_success: Callable[[Any], None] | None = None


class CircuitBreakerError(Exception):
    """
    Base exception for circuit breaker errors.
    """



class CircuitBreakerOpenError(CircuitBreakerError):
    """
    Raised when circuit breaker is open.
    """

    def __init__(self, circuit_name: str, state: CircuitBreakerState):
        self.circuit_name = circuit_name
        self.state = state
        super().__init__(f"Circuit breaker '{circuit_name}' is {state.value}")


class CircuitBreaker:
    """
    Circuit breaker implementation for fault tolerance.
    """

    def __init__(self, name: str, config: CircuitBreakerConfig | None = None):
        self.name = name
        self.config = config or CircuitBreakerConfig()

        # State
        self._state = CircuitBreakerState.CLOSED
        self._failure_count = 0
        self._success_count = 0
        self._last_failure_time: datetime | None = None
        self._last_success_time: datetime | None = None
        self._state_change_time = datetime.now()

        # Thread safety
        self._lock = threading.RLock()

        # Monitoring
        self._monitoring_task: asyncio.Task | None = None
        self._shutdown_event = asyncio.Event()

        # Statistics
        self._total_calls = 0
        self._total_failures = 0
        self._total_successes = 0
        self._total_rejections = 0

    @property
    def state(self) -> CircuitBreakerState:
        """
        Get current state.
        """
        with self._lock:
            return self._state

    @property
    def failure_count(self) -> int:
        """
        Get current failure count.
        """
        with self._lock:
            return self._failure_count

    @property
    def success_count(self) -> int:
        """
        Get current success count.
        """
        with self._lock:
            return self._success_count

    @property
    def is_open(self) -> bool:
        """
        Check if circuit is open.
        """
        return self.state == CircuitBreakerState.OPEN

    @property
    def is_closed(self) -> bool:
        """
        Check if circuit is closed.
        """
        return self.state == CircuitBreakerState.CLOSED

    @property
    def is_half_open(self) -> bool:
        """
        Check if circuit is half-open.
        """
        return self.state == CircuitBreakerState.HALF_OPEN

    def call(self, func: Callable[..., Any], *args, **kwargs) -> Any:
        """
        Execute a function through the circuit breaker.
        """
        return self._execute_call(func, args, kwargs, is_async=False)

    async def call_async(self, func: Callable[..., Awaitable[Any]], *args, **kwargs) -> Any:
        """
        Execute an async function through the circuit breaker.
        """
        return await self._execute_call(func, args, kwargs, is_async=True)

    def _execute_call(
        self, func: Callable[..., Any], args: tuple, kwargs: dict, is_async: bool,
    ) -> Any:
        """
        Execute a call through the circuit breaker.
        """
        with self._lock:
            self._total_calls += 1

            # Check if circuit is open
            if self._state == CircuitBreakerState.OPEN:
                if self._should_attempt_reset():
                    self._transition_to_half_open()
                else:
                    self._total_rejections += 1
                    raise CircuitBreakerOpenError(self.name, self._state)

            # Check if circuit is half-open and we've reached success threshold
            elif self._state == CircuitBreakerState.HALF_OPEN:
                if self._success_count >= self.config.success_threshold:
                    self._transition_to_closed()
                elif self._failure_count >= self.config.failure_threshold:
                    self._transition_to_open()
                    self._total_rejections += 1
                    raise CircuitBreakerOpenError(self.name, self._state)

        # Execute the function
        try:
            if is_async:
                result = asyncio.run(func(*args, **kwargs))
            else:
                result = func(*args, **kwargs)

            self._record_success()
            return result

        except Exception as e:
            self._record_failure(e)
            raise

    def _should_attempt_reset(self) -> bool:
        """
        Check if we should attempt to reset the circuit.
        """
        if self._last_failure_time is None:
            return True

        time_since_failure = (datetime.now() - self._last_failure_time).total_seconds()
        return time_since_failure >= self.config.recovery_timeout

    def _record_success(self) -> None:
        """
        Record a successful call.
        """
        with self._lock:
            self._success_count += 1
            self._last_success_time = datetime.now()
            self._total_successes += 1

            logger.debug(
                f"Circuit breaker '{self.name}' recorded success (count: {self._success_count})",
            )

            # Call success callback
            if self.config.on_success:
                try:
                    self.config.on_success(None)
                except Exception as e:
                    logger.warning(f"Success callback failed: {e}")

            # Transition to closed if we're half-open and have enough successes
            if (
                self._state == CircuitBreakerState.HALF_OPEN
                and self._success_count >= self.config.success_threshold
            ):
                self._transition_to_closed()

    def _record_failure(self, exception: Exception) -> None:
        """
        Record a failed call.
        """
        with self._lock:
            # Check if this exception should be ignored
            if isinstance(exception, self.config.ignore_exceptions):
                logger.debug(
                    f"Circuit breaker '{self.name}' ignoring exception: {type(exception).__name__}",
                )
                return

            # Check if this exception should be counted
            if not isinstance(exception, self.config.exception_types):
                logger.debug(
                    f"Circuit breaker '{self.name}' not counting exception: {type(exception).__name__}",
                )
                return

            self._failure_count += 1
            self._last_failure_time = datetime.now()
            self._total_failures += 1

            logger.debug(
                f"Circuit breaker '{self.name}' recorded failure (count: {self._failure_count})",
            )

            # Call failure callback
            if self.config.on_failure:
                try:
                    self.config.on_failure(exception)
                except Exception as e:
                    logger.warning(f"Failure callback failed: {e}")

            # Check if we should open the circuit
            if self._should_open_circuit():
                self._transition_to_open()

    def _should_open_circuit(self) -> bool:
        """
        Check if circuit should be opened.
        """
        # Check failure count threshold
        if self._failure_count >= self.config.failure_threshold:
            return True

        # Check failure rate within window
        if self._last_failure_time:
            time_since_first_failure = (datetime.now() - self._last_failure_time).total_seconds()
            if time_since_first_failure <= self.config.failure_window:
                return self._failure_count >= self.config.failure_threshold

        return False

    def _transition_to_open(self) -> None:
        """
        Transition to open state.
        """
        old_state = self._state
        self._state = CircuitBreakerState.OPEN
        self._state_change_time = datetime.now()
        self._failure_count = 0
        self._success_count = 0

        logger.info(f"Circuit breaker '{self.name}' transitioned to OPEN")
        self._notify_state_change(old_state, self._state)

    def _transition_to_half_open(self) -> None:
        """
        Transition to half-open state.
        """
        old_state = self._state
        self._state = CircuitBreakerState.HALF_OPEN
        self._state_change_time = datetime.now()
        self._failure_count = 0
        self._success_count = 0

        logger.info(f"Circuit breaker '{self.name}' transitioned to HALF_OPEN")
        self._notify_state_change(old_state, self._state)

    def _transition_to_closed(self) -> None:
        """
        Transition to closed state.
        """
        old_state = self._state
        self._state = CircuitBreakerState.CLOSED
        self._state_change_time = datetime.now()
        self._failure_count = 0
        self._success_count = 0

        logger.info(f"Circuit breaker '{self.name}' transitioned to CLOSED")
        self._notify_state_change(old_state, self._state)

    def _notify_state_change(
        self, old_state: CircuitBreakerState, new_state: CircuitBreakerState,
    ) -> None:
        """
        Notify about state change.
        """
        if self.config.on_state_change:
            try:
                self.config.on_state_change(old_state, new_state)
            except Exception as e:
                logger.warning(f"State change callback failed: {e}")

    def reset(self) -> None:
        """
        Manually reset the circuit breaker.
        """
        with self._lock:
            old_state = self._state
            self._state = CircuitBreakerState.CLOSED
            self._failure_count = 0
            self._success_count = 0
            self._last_failure_time = None
            self._last_success_time = None
            self._state_change_time = datetime.now()

            logger.info(f"Circuit breaker '{self.name}' manually reset")
            self._notify_state_change(old_state, self._state)

    def get_stats(self) -> dict[str, Any]:
        """
        Get circuit breaker statistics.
        """
        with self._lock:
            return {
                "name": self.name,
                "state": self._state.value,
                "failure_count": self._failure_count,
                "success_count": self._success_count,
                "total_calls": self._total_calls,
                "total_failures": self._total_failures,
                "total_successes": self._total_successes,
                "total_rejections": self._total_rejections,
                "last_failure_time": (
                    self._last_failure_time.isoformat() if self._last_failure_time else None
                ),
                "last_success_time": (
                    self._last_success_time.isoformat() if self._last_success_time else None
                ),
                "state_change_time": self._state_change_time.isoformat(),
                "failure_rate": self._total_failures / max(1, self._total_calls),
                "success_rate": self._total_successes / max(1, self._total_calls),
            }

    async def start_monitoring(self) -> None:
        """
        Start monitoring task.
        """
        if not self.config.enable_monitoring or self._monitoring_task is not None:
            return

        self._monitoring_task = asyncio.create_task(self._monitoring_loop())
        logger.info(f"Started monitoring for circuit breaker '{self.name}'")

    async def stop_monitoring(self) -> None:
        """
        Stop monitoring task.
        """
        if self._monitoring_task is None:
            return

        self._shutdown_event.set()
        self._monitoring_task.cancel()

        with contextlib.suppress(asyncio.CancelledError):
            await self._monitoring_task

        self._monitoring_task = None
        logger.info(f"Stopped monitoring for circuit breaker '{self.name}'")

    async def _monitoring_loop(self) -> None:
        """
        Monitoring loop.
        """
        while not self._shutdown_event.is_set():
            try:
                # Check if we should transition from open to half-open
                if self._state == CircuitBreakerState.OPEN and self._should_attempt_reset():
                    with self._lock:
                        self._transition_to_half_open()

                # Log current state
                stats = self.get_stats()
                logger.debug(f"Circuit breaker '{self.name}' stats: {stats}")

                await asyncio.sleep(self.config.monitoring_interval)

            except Exception as e:
                logger.exception(f"Error in circuit breaker monitoring: {e}")
                await asyncio.sleep(5.0)


class CircuitBreakerManager:
    """
    Manages multiple circuit breakers.
    """

    def __init__(self):
        self._circuits: dict[str, CircuitBreaker] = {}
        self._monitoring_task: asyncio.Task | None = None
        self._shutdown_event = asyncio.Event()

    def create_circuit(
        self, name: str, config: CircuitBreakerConfig | None = None,
    ) -> CircuitBreaker:
        """
        Create a new circuit breaker.
        """
        if name in self._circuits:
            raise ValueError(f"Circuit breaker '{name}' already exists")

        circuit = CircuitBreaker(name, config)
        self._circuits[name] = circuit

        logger.info(f"Created circuit breaker '{name}'")
        return circuit

    def get_circuit(self, name: str) -> CircuitBreaker | None:
        """
        Get a circuit breaker by name.
        """
        return self._circuits.get(name)

    def remove_circuit(self, name: str) -> bool:
        """
        Remove a circuit breaker.
        """
        if name in self._circuits:
            circuit = self._circuits[name]
            asyncio.create_task(circuit.stop_monitoring())
            del self._circuits[name]
            logger.info(f"Removed circuit breaker '{name}'")
            return True
        return False

    def list_circuits(self) -> list[str]:
        """
        List all circuit breaker names.
        """
        return list(self._circuits.keys())

    def get_all_stats(self) -> dict[str, dict[str, Any]]:
        """
        Get statistics for all circuit breakers.
        """
        return {name: circuit.get_stats() for name, circuit in self._circuits.items()}

    async def start_monitoring(self) -> None:
        """
        Start monitoring all circuit breakers.
        """
        if self._monitoring_task is not None:
            return

        # Start monitoring for all circuits
        for circuit in self._circuits.values():
            await circuit.start_monitoring()

        self._monitoring_task = asyncio.create_task(self._manager_monitoring_loop())
        logger.info("Started circuit breaker manager monitoring")

    async def stop_monitoring(self) -> None:
        """
        Stop monitoring all circuit breakers.
        """
        if self._monitoring_task is None:
            return

        self._shutdown_event.set()
        self._monitoring_task.cancel()

        with contextlib.suppress(asyncio.CancelledError):
            await self._monitoring_task

        # Stop monitoring for all circuits
        for circuit in self._circuits.values():
            await circuit.stop_monitoring()

        self._monitoring_task = None
        logger.info("Stopped circuit breaker manager monitoring")

    async def _manager_monitoring_loop(self) -> None:
        """
        Manager-level monitoring loop.
        """
        while not self._shutdown_event.is_set():
            try:
                # Log overall stats
                stats = self.get_all_stats()
                logger.debug(f"Circuit breaker manager stats: {stats}")

                await asyncio.sleep(30.0)  # Check every 30 seconds

            except Exception as e:
                logger.exception(f"Error in circuit breaker manager monitoring: {e}")
                await asyncio.sleep(10.0)
