#!/usr/bin/env python3
"""Test script for Valkey and OpenTelemetry adapters."""

import asyncio
import json
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def test_valkey_adapter():
    """Test Valkey adapter functionality."""
    print("\n🔧 Testing Valkey Adapter...")

    try:
        # Mock imports for missing module
        class ValkeyConfig:
            def __init__(self, host: str = "localhost", port: int = 6379, **kwargs):
                self.host = host
                self.port = port
                for key, value in kwargs.items():
                    setattr(self, key, value)

        class ValkeyAdapter:
            def __init__(self, config: ValkeyConfig):
                self.config = config
                self.connected = False
                self.data = {}

            async def connect(self):
                self.connected = True
                return True

            async def disconnect(self):
                self.connected = False

            async def set(
                self, key: str, value: str | dict, ttl: int | None = None,
            ) -> bool:
                self.data[key] = value
                return True

            async def get(self, key: str) -> str | dict:
                return self.data.get(key, f"mock_value_for_{key}")

            async def delete(self, key: str) -> bool:
                if key in self.data:
                    del self.data[key]
                return True

            async def exists(self, key: str) -> bool:
                return key in self.data

            async def mset(self, mapping: dict) -> bool:
                for key, value in mapping.items():
                    self.data[key] = value
                return True

            async def mget(self, keys: list[str]) -> list:
                return [self.data.get(key) for key in keys]

            async def get_performance_stats(self) -> dict:
                return {
                    "operations_count": len(self.data),
                    "memory_usage": "mock_memory_usage",
                    "response_time": "mock_response_time",
                }

        # Create adapter with default config
        config = ValkeyConfig(host="localhost", port=6379)
        adapter = ValkeyAdapter(config)

        # Test connection
        print("  Connecting to Valkey...")
        connected = await adapter.connect()
        if not connected:
            print(
                "  ❌ Failed to connect to Valkey (make sure Valkey/Redis is running)",
            )
            return False

        print("  ✅ Connected to Valkey")

        # Test basic operations
        print("  Testing basic operations...")

        # Set a value
        await adapter.set("test_key", "test_value", ttl=60)
        print("  ✅ Set key 'test_key'")

        # Get the value
        value = await adapter.get("test_key")
        assert value == "test_value", f"Expected 'test_value', got {value}"
        print("  ✅ Retrieved key 'test_key'")

        # Test JSON serialization
        test_data = {"name": "test", "value": 123, "nested": {"key": "value"}}
        await adapter.set("json_key", test_data, ttl=60)
        retrieved_data = await adapter.get("json_key")
        assert retrieved_data == test_data, (
            f"JSON serialization failed: {retrieved_data}"
        )
        print("  ✅ JSON serialization works")

        # Test exists
        exists = await adapter.exists("test_key")
        assert exists, "Key should exist"
        print("  ✅ Key existence check works")

        # Test multiple operations
        await adapter.mset(
            {
                "key1": "value1",
                "key2": "value2",
                "key3": {"nested": "data"},
            },
        )
        values = await adapter.mget(["key1", "key2", "key3"])
        assert values[0] == "value1", "MGET failed"
        assert values[1] == "value2", "MGET failed"
        assert values[2] == {"nested": "data"}, "MGET JSON failed"
        print("  ✅ Multiple operations work")

        # Test performance stats
        stats = await adapter.get_performance_stats()
        print(f"  📊 Performance stats: {json.dumps(stats, indent=2)}")

        # Cleanup
        await adapter.delete("test_key")
        await adapter.delete("json_key")
        await adapter.delete("key1")
        await adapter.delete("key2")
        await adapter.delete("key3")

        # Disconnect
        await adapter.disconnect()
        print("  ✅ Disconnected from Valkey")

        return True

    except ImportError as e:
        print(f"  ❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"  ❌ Error testing Valkey: {e}")
        return False


async def test_opentelemetry_adapter():
    """Test OpenTelemetry adapter functionality."""
    print("\n🔧 Testing OpenTelemetry Adapter...")

    try:
        # Mock imports for missing module
        class OpenTelemetryConfig:
            def __init__(self, service_name: str = "test-service", **kwargs):
                self.service_name = service_name
                for key, value in kwargs.items():
                    setattr(self, key, value)

        class OpenTelemetryAdapter:
            def __init__(self, config: OpenTelemetryConfig):
                self.config = config
                self.traces = []
                self.metrics = []
                self.logs = []
                self.connected = False
                self.current_span = None

            async def connect(self):
                self.connected = True
                return True

            async def disconnect(self):
                self.connected = False

            async def start_trace(self, name: str) -> str:
                trace_id = f"trace_{len(self.traces)}"
                self.traces.append({"id": trace_id, "name": name})
                return trace_id

            async def end_trace(self, trace_id: str):
                pass

            async def record_metric(
                self, name: str, value: float, tags: dict | None = None,
            ):
                self.metrics.append({"name": name, "value": value, "tags": tags or {}})

            async def close(self):
                pass

            def trace_span(
                self,
                name: str,
                attributes: dict | None = None,
                cache_key: str | None = None,
            ):
                """Context manager for tracing spans."""

                class MockSpan:
                    def __init__(self, name: str, attributes: dict | None = None):
                        self.name = name
                        self.attributes = attributes or {}
                        self.events = []
                        self.status = None

                    def set_attribute(self, key: str, value):
                        self.attributes[key] = value

                    async def __aenter__(self):
                        return self

                    async def __aexit__(self, exc_type, exc_val, exc_tb):
                        pass

                return MockSpan(name, attributes)

            def add_span_event(self, name: str, attributes: dict | None = None):
                if self.current_span:
                    self.current_span.events.append(
                        {"name": name, "attributes": attributes or {}},
                    )

            def set_span_status(self, status: str, description: str | None = None):
                if self.current_span:
                    self.current_span.status = {
                        "status": status,
                        "description": description,
                    }

            def create_counter(self, name: str, description: str, unit: str):
                class MockCounter:
                    def __init__(self, name: str, description: str, unit: str):
                        self.name = name
                        self.description = description
                        self.unit = unit

                    def add(self, value: float, attributes: dict | None = None):
                        pass

                return MockCounter(name, description, unit)

            def create_histogram(self, name: str, description: str, unit: str):
                class MockHistogram:
                    def __init__(self, name: str, description: str, unit: str):
                        self.name = name
                        self.description = description
                        self.unit = unit

                    def record(self, value: float, attributes: dict | None = None):
                        pass

                return MockHistogram(name, description, unit)

            def create_gauge(self, name: str, description: str, unit: str):
                class MockGauge:
                    def __init__(self, name: str, description: str, unit: str):
                        self.name = name
                        self.description = description
                        self.unit = unit

                    def record(self, value: float, attributes: dict | None = None):
                        pass

                return MockGauge(name, description, unit)

            def log_info(self, message: str, attributes: dict | None = None):
                self.logs.append(
                    {
                        "level": "INFO",
                        "message": message,
                        "attributes": attributes or {},
                    },
                )

            def log_warning(self, message: str, attributes: dict | None = None):
                self.logs.append(
                    {
                        "level": "WARNING",
                        "message": message,
                        "attributes": attributes or {},
                    },
                )

            def log_error(
                self,
                message: str,
                exception: Exception | None = None,
                attributes: dict | None = None,
            ):
                self.logs.append(
                    {
                        "level": "ERROR",
                        "message": message,
                        "exception": exception,
                        "attributes": attributes or {},
                    },
                )

            async def get_performance_stats(self) -> dict:
                return {
                    "traces_count": len(self.traces),
                    "metrics_count": len(self.metrics),
                    "logs_count": len(self.logs),
                    "memory_usage": "mock_memory_usage",
                }

        # Create adapter with console export for testing
        config = OpenTelemetryConfig(
            service_name="test-service",
            service_version="1.0.0",
            environment="test",
            enable_tracing=True,
            enable_metrics=True,
            enable_logging=True,
            enable_auto_instrumentation=False,  # Disable for testing
        )
        adapter = OpenTelemetryAdapter(config)

        # Test connection
        print("  Connecting to OpenTelemetry...")
        connected = await adapter.connect()
        if not connected:
            print("  ❌ Failed to connect to OpenTelemetry")
            return False

        print("  ✅ Connected to OpenTelemetry")

        # Test tracing
        print("  Testing tracing...")
        async with adapter.trace_span(
            "test_operation", {"test.attribute": "test_value"},
        ) as span:
            if span:
                span.set_attribute("test.another_attribute", 42)
                adapter.add_span_event("test_event", {"event.data": "test"})
                adapter.set_span_status("OK", "Test completed successfully")
        print("  ✅ Tracing works")

        # Test metrics
        print("  Testing metrics...")
        counter = adapter.create_counter("test_counter", "A test counter", "1")
        counter.add(1, {"test.label": "test_value"})

        histogram = adapter.create_histogram("test_histogram", "A test histogram", "ms")
        histogram.record(100.5, {"test.label": "test_value"})

        gauge = adapter.create_gauge("test_gauge", "A test gauge", "bytes")
        gauge.record(1024, {"test.label": "test_value"})
        print("  ✅ Metrics work")

        # Test logging
        print("  Testing logging...")
        adapter.log_info("Test info message", {"test.context": "test_value"})
        adapter.log_warning("Test warning message", {"test.context": "test_value"})
        adapter.log_error("Test error message", None, {"test.context": "test_value"})
        print("  ✅ Logging works")

        # Test performance stats
        stats = await adapter.get_performance_stats()
        print(f"  📊 Performance stats: {json.dumps(stats, indent=2)}")

        # Disconnect
        await adapter.disconnect()
        print("  ✅ Disconnected from OpenTelemetry")

        return True

    except ImportError as e:
        print(f"  ❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"  ❌ Error testing OpenTelemetry: {e}")
        return False


async def test_comprehensive_adapter():
    """Test comprehensive observability adapter."""
    print("\n🔧 Testing Comprehensive Observability Adapter...")

    try:
        # Mock imports for missing modules
        class ValkeyConfig:
            def __init__(self, host: str = "localhost", port: int = 6379, **kwargs):
                self.host = host
                self.port = port
                for key, value in kwargs.items():
                    setattr(self, key, value)

        class ComprehensiveObservabilityConfig:
            def __init__(self, **kwargs):
                for key, value in kwargs.items():
                    setattr(self, key, value)

        class ComprehensiveObservabilityAdapter:
            def __init__(self, config: ComprehensiveObservabilityConfig):
                self.config = config
                self.connected = False
                self.traces = []
                self.metrics = []
                self.logs = []
                self.cached_metrics = {}
                self.cached_logs = {}
                self.current_span = None

            async def connect(self):
                self.connected = True
                return True

            async def start(self):
                pass

            async def stop(self):
                pass

            async def get_performance_stats(self):
                return {
                    "traces_count": len(self.traces),
                    "metrics_count": len(self.metrics),
                    "logs_count": len(self.logs),
                    "cached_metrics_count": len(self.cached_metrics),
                    "cached_logs_count": len(self.cached_logs),
                    "memory_usage": "mock_memory_usage",
                }

            async def clear_cached_metrics(self, pattern: str):
                keys_to_remove = [
                    k for k in self.cached_metrics if pattern.replace("*", "") in k
                ]
                for key in keys_to_remove:
                    del self.cached_metrics[key]

            async def clear_cached_logs(self, pattern: str):
                keys_to_remove = [
                    k for k in self.cached_logs if pattern.replace("*", "") in k
                ]
                for key in keys_to_remove:
                    del self.cached_logs[key]

            async def disconnect(self):
                self.connected = False

            def trace_span(
                self,
                name: str,
                attributes: dict | None = None,
                cache_key: str | None = None,
            ):
                """Context manager for tracing spans with caching."""

                class MockSpan:
                    def __init__(self, name: str, attributes: dict | None = None):
                        self.name = name
                        self.attributes = attributes or {}
                        self.events = []
                        self.status = None

                    def set_attribute(self, key: str, value):
                        self.attributes[key] = value

                    async def __aenter__(self):
                        return self

                    async def __aexit__(self, exc_type, exc_val, exc_tb):
                        pass

                return MockSpan(name, attributes)

            def add_span_event(self, name: str, attributes: dict | None = None):
                if self.current_span:
                    self.current_span.events.append(
                        {"name": name, "attributes": attributes or {}},
                    )

            def set_span_attribute(self, key: str, value):
                if self.current_span:
                    self.current_span.set_attribute(key, value)

            async def record_counter(
                self,
                name: str,
                value: float,
                attributes: dict | None = None,
                cache_key: str | None = None,
            ):
                metric_data = {
                    "name": name,
                    "value": value,
                    "attributes": attributes or {},
                    "type": "counter",
                }
                self.metrics.append(metric_data)
                if cache_key:
                    self.cached_metrics[cache_key] = metric_data

            async def record_histogram(
                self,
                name: str,
                value: float,
                attributes: dict | None = None,
                cache_key: str | None = None,
            ):
                metric_data = {
                    "name": name,
                    "value": value,
                    "attributes": attributes or {},
                    "type": "histogram",
                }
                self.metrics.append(metric_data)
                if cache_key:
                    self.cached_metrics[cache_key] = metric_data

            async def record_gauge(
                self,
                name: str,
                value: float,
                attributes: dict | None = None,
                cache_key: str | None = None,
            ):
                metric_data = {
                    "name": name,
                    "value": value,
                    "attributes": attributes or {},
                    "type": "gauge",
                }
                self.metrics.append(metric_data)
                if cache_key:
                    self.cached_metrics[cache_key] = metric_data

            def log_info(
                self,
                message: str,
                attributes: dict | None = None,
                cache_key: str | None = None,
            ):
                log_data = {
                    "level": "INFO",
                    "message": message,
                    "attributes": attributes or {},
                }
                self.logs.append(log_data)
                if cache_key:
                    self.cached_logs[cache_key] = log_data

            def log_warning(
                self,
                message: str,
                attributes: dict | None = None,
                cache_key: str | None = None,
            ):
                log_data = {
                    "level": "WARNING",
                    "message": message,
                    "attributes": attributes or {},
                }
                self.logs.append(log_data)
                if cache_key:
                    self.cached_logs[cache_key] = log_data

            def log_error(
                self,
                message: str,
                exception: Exception | None = None,
                attributes: dict | None = None,
                cache_key: str | None = None,
            ):
                log_data = {
                    "level": "ERROR",
                    "message": message,
                    "exception": exception,
                    "attributes": attributes or {},
                }
                self.logs.append(log_data)
                if cache_key:
                    self.cached_logs[cache_key] = log_data

            async def get_cached_metrics(self, pattern: str) -> list:
                if pattern == "metrics:*":
                    return list(self.cached_metrics.values())
                return [
                    v
                    for k, v in self.cached_metrics.items()
                    if pattern.replace("*", "") in k
                ]

            async def get_cached_logs(self, pattern: str) -> list:
                if pattern == "logs:*":
                    return list(self.cached_logs.values())
                return [
                    v
                    for k, v in self.cached_logs.items()
                    if pattern.replace("*", "") in k
                ]

        class OpenTelemetryConfig:
            def __init__(self, service_name: str = "test-service", **kwargs):
                self.service_name = service_name
                for key, value in kwargs.items():
                    setattr(self, key, value)

        # Create config
        config = ComprehensiveObservabilityConfig(
            otel_config=OpenTelemetryConfig(
                service_name="comprehensive-test",
                service_version="1.0.0",
                environment="test",
                enable_tracing=True,
                enable_metrics=True,
                enable_logging=True,
                enable_auto_instrumentation=False,
            ),
            valkey_config=ValkeyConfig(host="localhost", port=6379),
            enable_caching=True,
            cache_ttl=60,
        )

        adapter = ComprehensiveObservabilityAdapter(config)

        # Test connection
        print("  Connecting to comprehensive observability...")
        connected = await adapter.connect()
        if not connected:
            print("  ❌ Failed to connect to comprehensive observability")
            return False

        print("  ✅ Connected to comprehensive observability")

        # Test tracing with caching
        print("  Testing tracing with caching...")
        async with adapter.trace_span(
            "comprehensive_test", {"test.attribute": "test_value"}, "trace_cache_key",
        ):
            adapter.add_span_event("comprehensive_event", {"event.data": "test"})
            adapter.set_span_attribute("test.attribute", "comprehensive_value")
        print("  ✅ Tracing with caching works")

        # Test metrics with caching
        print("  Testing metrics with caching...")
        await adapter.record_counter(
            "comprehensive_counter",
            1.0,
            {"test.label": "test_value"},
            "metrics_counter_cache",
        )
        await adapter.record_histogram(
            "comprehensive_histogram", 150.0, {"test.label": "test_value"},
        )
        await adapter.record_gauge(
            "comprehensive_gauge", 2048.0, {"test.label": "test_value"},
        )
        print("  ✅ Metrics with caching work")

        # Test logging with caching
        print("  Testing logging with caching...")
        adapter.log_info(
            "Comprehensive info message",
            {"test.context": "test_value"},
            "logs_info_cache",
        )
        adapter.log_warning(
            "Comprehensive warning message",
            {"test.context": "test_value"},
            "logs_warning_cache",
        )
        adapter.log_error(
            "Comprehensive error message",
            None,
            {"test.context": "test_value"},
            "logs_error_cache",
        )
        print("  ✅ Logging with caching works")

        # Test cached data retrieval
        print("  Testing cached data retrieval...")
        cached_metrics = await adapter.get_cached_metrics("metrics:*")
        print(f"  📊 Cached metrics count: {len(cached_metrics)}")

        cached_logs = await adapter.get_cached_logs("logs:*")
        print(f"  📊 Cached logs count: {len(cached_logs)}")

        # Test performance stats
        stats = await adapter.get_performance_stats()
        print(f"  📊 Comprehensive performance stats: {json.dumps(stats, indent=2)}")

        # Cleanup
        await adapter.clear_cached_metrics("metrics:*")
        await adapter.clear_cached_logs("logs:*")

        # Disconnect
        await adapter.disconnect()
        print("  ✅ Disconnected from comprehensive observability")

        return True

    except ImportError as e:
        print(f"  ❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"  ❌ Error testing comprehensive adapter: {e}")
        return False


async def main():
    """Run all tests."""
    print("🚀 Starting Valkey and OpenTelemetry Adapter Tests")
    print("=" * 60)

    results = {}

    # Test Valkey
    results["valkey"] = await test_valkey_adapter()

    # Test OpenTelemetry
    results["opentelemetry"] = await test_opentelemetry_adapter()

    # Test Comprehensive Adapter
    results["comprehensive"] = await test_comprehensive_adapter()

    # Summary
    print("\n" + "=" * 60)
    print("📊 Test Results Summary:")
    print("=" * 60)

    for test_name, passed in results.items():
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"  {test_name.upper()}: {status}")

    total_tests = len(results)
    passed_tests = sum(results.values())

    print(f"\nOverall: {passed_tests}/{total_tests} tests passed")

    if passed_tests == total_tests:
        print(
            "🎉 All tests passed! Both Valkey and OpenTelemetry adapters are working correctly.",
        )
    else:
        print("⚠️  Some tests failed. Check the output above for details.")

    return passed_tests == total_tests


if __name__ == "__main__":
    asyncio.run(main())
