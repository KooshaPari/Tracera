#!/usr/bin/env python3
"""Resilience Patterns Example.

This example demonstrates how to use the pheno.resilience module for circuit breakers,
retry strategies, and error handling.
"""

import asyncio

from pheno.resilience import (
    Bulkhead,
    BulkheadConfig,
    CircuitBreaker,
    CircuitBreakerConfig,
    ErrorCategorizer,
    ErrorHandler,
    ExponentialBackoffRetry,
    HealthCheck,
    HealthChecker,
    HealthStatus,
    RetryConfig,
)


async def unreliable_service(call_number: int) -> str:
    """
    Simulate an unreliable service.
    """
    # Simulate different failure patterns
    if call_number % 3 == 0:
        raise ConnectionError("Connection failed")
    if call_number % 5 == 0:
        raise TimeoutError("Request timed out")
    if call_number % 7 == 0:
        raise ValueError("Invalid response")
    await asyncio.sleep(0.1)  # Simulate work
    return f"Success from call {call_number}"


async def circuit_breaker_example():
    """
    Demonstrate circuit breaker pattern.
    """
    print("🔌 Circuit Breaker Example")
    print("-" * 30)

    config = CircuitBreakerConfig(
        failure_threshold=3, failure_window=10.0, recovery_timeout=5.0, enable_monitoring=True,
    )

    breaker = CircuitBreaker("unreliable_service", config)
    await breaker.start_monitoring()

    print(f"Circuit state: {breaker.state.value}")

    # Make several calls
    for i in range(10):
        try:
            result = await breaker.call_async(unreliable_service, i)
            print(f"  Call {i}: ✅ {result}")
        except Exception as e:
            print(f"  Call {i}: ❌ {e}")

        print(f"  Circuit state: {breaker.state.value}")
        await asyncio.sleep(0.5)

    # Get circuit breaker stats
    stats = breaker.get_stats()
    print("\nCircuit Breaker Stats:")
    print(f"  • Total calls: {stats['total_calls']}")
    print(f"  • Failures: {stats['total_failures']}")
    print(f"  • Success rate: {stats['success_rate']:.2%}")

    await breaker.stop_monitoring()


async def retry_strategy_example():
    """
    Demonstrate retry strategies.
    """
    print("\n🔄 Retry Strategy Example")
    print("-" * 30)

    config = RetryConfig(max_attempts=3, base_delay=0.5, max_delay=5.0, jitter=True)

    retry_strategy = ExponentialBackoffRetry(config)

    # Test with different error types
    test_cases = [
        ("ConnectionError", ConnectionError("Connection failed")),
        ("TimeoutError", TimeoutError("Request timed out")),
        ("ValueError", ValueError("Invalid input")),
    ]

    for error_name, error in test_cases:
        print(f"\nTesting with {error_name}:")

        async def failing_function():
            raise error

        try:
            result = await retry_strategy.execute_async(failing_function)
            print(f"  ✅ Unexpected success: {result}")
        except Exception as e:
            print(f"  ❌ Failed as expected: {e}")


async def error_handling_example():
    """
    Demonstrate error categorization and handling.
    """
    print("\n⚠️ Error Handling Example")
    print("-" * 30)

    categorizer = ErrorCategorizer()
    error_handler = ErrorHandler(categorizer)

    # Test different error types
    test_errors = [
        ConnectionError("Network connection failed"),
        TimeoutError("Request timed out"),
        ValueError("Invalid input parameter"),
        PermissionError("Access denied"),
        RuntimeError("System error occurred"),
    ]

    for error in test_errors:
        category = categorizer.categorize(error)
        is_retryable = categorizer.is_retryable(error)

        print(f"Error: {type(error).__name__}")
        print(f"  Category: {category.value}")
        print(f"  Retryable: {is_retryable}")
        print(f"  Message: {error}")


async def bulkhead_example():
    """
    Demonstrate bulkhead pattern.
    """
    print("\n🚧 Bulkhead Example")
    print("-" * 30)

    config = BulkheadConfig(max_concurrent_calls=2, max_wait_time=1.0, timeout=5.0)

    bulkhead = Bulkhead("resource_pool", config)
    await bulkhead.start_monitoring()

    async def slow_task(task_id: int) -> str:
        print(f"  Starting slow task {task_id}")
        await asyncio.sleep(2.0)
        print(f"  Completed slow task {task_id}")
        return f"Result from task {task_id}"

    # Try to execute multiple tasks concurrently
    tasks = []
    for i in range(5):
        try:
            result = await bulkhead.execute_async(slow_task, i)
            print(f"  ✅ Task {i}: {result}")
        except Exception as e:
            print(f"  ❌ Task {i}: {e}")

    # Get bulkhead stats
    stats = bulkhead.get_stats()
    print("\nBulkhead Stats:")
    print(f"  • Max concurrent: {stats['max_concurrent_calls']}")
    print(f"  • Active calls: {stats['active_calls']}")
    print(f"  • Utilization: {stats['utilization']:.2%}")

    await bulkhead.stop_monitoring()


class SampleHealthChecker(HealthChecker):
    """
    Sample health checker for demonstration.
    """

    def __init__(self, name: str, healthy: bool = True):
        self.name = name
        self.healthy = healthy

    async def check_health(self) -> HealthCheck:
        """
        Perform health check.
        """
        # Simulate health check
        await asyncio.sleep(0.1)

        if self.healthy:
            return HealthCheck(
                name=self.name, status=HealthStatus.HEALTHY, message="Service is healthy",
            )
        return HealthCheck(
            name=self.name, status=HealthStatus.UNHEALTHY, message="Service is unhealthy",
        )


async def health_monitoring_example():
    """
    Demonstrate health monitoring.
    """
    print("\n🏥 Health Monitoring Example")
    print("-" * 30)

    from pheno.resilience.health import HealthConfig, HealthMonitor

    config = HealthConfig(check_interval=2.0, timeout=1.0, retry_count=2)

    monitor = HealthMonitor(config)

    # Add health checkers
    monitor.add_checker("database", SampleHealthChecker("database", True))
    monitor.add_checker("api", SampleHealthChecker("api", True))
    monitor.add_checker("cache", SampleHealthChecker("cache", False))

    # Start monitoring
    await monitor.start_monitoring()

    # Check health a few times
    for i in range(3):
        health = await monitor.get_overall_health()
        print(f"  Overall health: {health.value}")

        checks = await monitor.check_all()
        for name, check in checks.items():
            status_emoji = "✅" if check.status == HealthStatus.HEALTHY else "❌"
            print(f"    {status_emoji} {name}: {check.status.value}")

        await asyncio.sleep(3)

    await monitor.stop_monitoring()


async def main():
    """
    Main example function.
    """
    print("🛡️ Resilience Patterns Example")
    print("=" * 50)

    # Run all examples
    await circuit_breaker_example()
    await retry_strategy_example()
    await error_handling_example()
    await bulkhead_example()
    await health_monitoring_example()

    print("\n✅ All resilience examples completed!")


if __name__ == "__main__":
    asyncio.run(main())
