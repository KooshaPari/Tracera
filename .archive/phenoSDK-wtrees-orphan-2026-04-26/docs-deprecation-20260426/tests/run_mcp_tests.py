"""
Simple test runner for MCP tests.
"""

import asyncio
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import os
import tempfile

from pheno.adapters.container import Container
from pheno.mcp import (
    McpManager,
    McpServer,
    McpTool,
    setup_mcp,
    setup_mcp_with_config,
)


async def test_setup_mcp():
    """
    Test MCP setup with default adapters.
    """
    print("Testing MCP setup...")

    manager = setup_mcp()

    assert isinstance(manager, McpManager)
    assert manager.container is not None

    print("✓ MCP setup works")


async def test_connect_disconnect():
    """
    Test connecting and disconnecting from MCP server.
    """
    print("Testing connect/disconnect...")

    manager = setup_mcp()

    server = McpServer(url="http://localhost:8000", name="test-server")
    session = await manager.connect(server)

    assert session is not None
    assert session.server == server
    assert session.is_active()

    await manager.disconnect(session)

    print("✓ Connect/disconnect works")


async def test_register_and_execute_tool():
    """
    Test registering and executing a tool.
    """
    print("Testing tool registration and execution...")

    manager = setup_mcp()

    # Define a simple tool handler
    def search_handler(query: str) -> dict:
        return {"results": [f"Result for: {query}"]}

    # Register tool
    tool = McpTool(
        name="search",
        description="Search documentation",
        parameters={"query": {"type": "string", "required": True}},
    )
    manager.register_tool(tool, handler=search_handler)

    # Execute tool
    result = await manager.execute_tool("search", {"query": "hello"})

    assert result.success
    print(f"  Result output: {result.output}")
    assert result.output == {"results": ["Result for: hello"]}

    print("✓ Tool registration and execution works")


async def test_list_tools():
    """
    Test listing registered tools.
    """
    print("Testing list tools...")

    manager = setup_mcp()

    # Register multiple tools
    tool1 = McpTool(name="search", description="Search docs")
    tool2 = McpTool(name="analyze", description="Analyze data")

    manager.register_tool(tool1)
    manager.register_tool(tool2)

    tools = manager.list_tools()

    assert len(tools) == 2
    assert any(t.name == "search" for t in tools)
    assert any(t.name == "analyze" for t in tools)

    print("✓ List tools works")


async def test_resource_access():
    """
    Test accessing resources via URIs.
    """
    print("Testing resource access...")

    config = {
        "app": {"name": "test-app", "debug": True},
        "database": {"host": "localhost", "port": 5432},
    }

    manager = setup_mcp_with_config(config)

    # Access config resources
    app_config = await manager.get_resource("config://app")
    assert app_config == {"name": "test-app", "debug": True}

    db_host = await manager.get_resource("config://database/host")
    assert db_host == "localhost"

    print("✓ Resource access works")


async def test_memory_scheme():
    """
    Test memory:// scheme for in-memory storage.
    """
    print("Testing memory:// scheme...")

    manager = setup_mcp()

    # Get resource provider
    from pheno.ports.mcp import ResourceProvider

    resource_provider = manager.container.resolve(ResourceProvider)

    # Get memory handler
    memory_handler = resource_provider.get_scheme_handler("memory")

    # Store value
    await memory_handler.set("memory://cache/user-123", {"name": "Alice"})

    # Retrieve value
    user = await manager.get_resource("memory://cache/user-123")
    assert user == {"name": "Alice"}

    print("✓ Memory scheme works")


async def test_session_management():
    """
    Test session management.
    """
    print("Testing session management...")

    manager = setup_mcp()

    server1 = McpServer(url="http://localhost:8000", name="server1")
    server2 = McpServer(url="http://localhost:8001", name="server2")

    # Create sessions
    session1 = await manager.connect(server1)
    session2 = await manager.connect(server2)

    # Get session manager
    from pheno.ports.mcp import SessionManager

    session_manager = manager.container.resolve(SessionManager)

    # List sessions
    sessions = session_manager.list_sessions()
    assert len(sessions) == 2

    # Close one session
    await manager.disconnect(session1)

    sessions = session_manager.list_sessions()
    assert len(sessions) == 1

    # Close all
    await session_manager.close_all_sessions()

    sessions = session_manager.list_sessions()
    assert len(sessions) == 0

    print("✓ Session management works")


async def test_monitoring():
    """
    Test monitoring provider.
    """
    print("Testing monitoring...")

    manager = setup_mcp(with_monitoring=True)

    # Get monitoring provider
    from pheno.ports.mcp import MonitoringProvider

    monitor = manager.container.resolve(MonitoringProvider)

    # Track workflow
    await monitor.track_workflow("test-workflow", {"user": "alice"})

    # Record metrics
    await monitor.record_metric("execution_time", 1.23, {"tool": "search"})
    await monitor.record_counter("tool_executions", tags={"tool": "search"})

    # Get metrics
    metrics = await monitor.get_metrics(filters={"name": "execution_time"})
    assert len(metrics) == 1
    assert metrics[0]["value"] == 1.23

    # Get workflow status
    status = await monitor.get_workflow_status("test-workflow")
    assert status["workflow_id"] == "test-workflow"
    assert status["metadata"]["user"] == "alice"

    print("✓ Monitoring works")


async def test_tool_with_monitoring():
    """
    Test tool execution with automatic monitoring.
    """
    print("Testing tool execution with monitoring...")

    manager = setup_mcp(with_monitoring=True)

    # Register tool
    def slow_tool(value: int) -> int:
        import time

        time.sleep(0.1)  # Simulate work
        return value * 2

    tool = McpTool(name="slow_tool", description="A slow tool")
    manager.register_tool(tool, handler=slow_tool)

    # Execute tool (should be automatically monitored)
    result = await manager.execute_tool("slow_tool", {"value": 5})

    assert result.success
    assert result.output == 10

    # Check that metrics were recorded
    from pheno.ports.mcp import MonitoringProvider

    monitor = manager.container.resolve(MonitoringProvider)

    metrics = await monitor.get_metrics(filters={"name": "tool_execution_time"})
    assert len(metrics) > 0

    print("✓ Tool execution with monitoring works")


async def test_custom_container():
    """
    Test using custom DI container.
    """
    print("Testing custom container...")

    # Create custom container
    container = Container()

    # Setup MCP with custom container
    manager = setup_mcp(container=container)

    assert manager.container is container

    # Verify providers are registered
    from pheno.ports.mcp import McpProvider, ResourceProvider

    assert container.has_service(McpProvider)
    assert container.has_service(ResourceProvider)

    print("✓ Custom container works")


async def test_error_handling():
    """
    Test error handling in tool execution.
    """
    print("Testing error handling...")

    manager = setup_mcp(with_monitoring=True)

    # Register tool that raises error
    def failing_tool(value: int) -> int:
        raise ValueError("Something went wrong!")

    tool = McpTool(name="failing_tool", description="A failing tool")
    manager.register_tool(tool, handler=failing_tool)

    # Execute tool (should catch error)
    try:
        result = await manager.execute_tool("failing_tool", {"value": 5})
        # Should not reach here
        assert False, "Should have raised exception"
    except ValueError as e:
        assert "Something went wrong" in str(e)

    # Check that error was recorded
    from pheno.ports.mcp import MonitoringProvider

    monitor = manager.container.resolve(MonitoringProvider)

    errors = monitor.get_errors()
    assert len(errors) > 0

    print("✓ Error handling works")


async def test_env_scheme():
    """
    Test env:// scheme for environment variables.
    """
    print("Testing env:// scheme...")

    # Set test environment variable
    os.environ["TEST_VAR"] = "test_value"
    os.environ["APP_NAME"] = "pheno"
    os.environ["APP_DEBUG"] = "true"

    manager = setup_mcp(with_extended_schemes=True)

    # Debug: check registered schemes
    from pheno.ports.mcp import ResourceProvider

    resource_provider = manager.container.resolve(ResourceProvider)
    schemes = resource_provider.list_schemes()
    print(f"  Registered schemes: {schemes}")

    # Get single variable
    value = await manager.get_resource("env://TEST_VAR")
    assert value == "test_value"

    # List variables with prefix
    app_vars = await manager.list_resources("env://APP_*")
    assert len(app_vars) >= 2
    assert "env://APP_NAME" in app_vars

    # Cleanup
    del os.environ["TEST_VAR"]
    del os.environ["APP_NAME"]
    del os.environ["APP_DEBUG"]

    print("✓ env:// scheme works")


async def test_file_scheme():
    """Test file:// scheme for file access."""
    print("Testing file:// scheme...")

    # Create temporary file
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        import json

        json.dump({"test": "data", "value": 123}, f)
        temp_file = f.name

    try:
        manager = setup_mcp(with_extended_schemes=True)

        # Read JSON file
        data = await manager.get_resource(f"file://{temp_file}")
        assert data == {"test": "data", "value": 123}

        print("✓ file:// scheme works")
    finally:
        # Cleanup
        os.unlink(temp_file)


async def test_logs_scheme():
    """
    Test logs:// scheme for log access.
    """
    print("Testing logs:// scheme...")

    manager = setup_mcp(with_extended_schemes=True)

    # Get logs handler
    from pheno.ports.mcp import ResourceProvider

    resource_provider = manager.container.resolve(ResourceProvider)
    logs_handler = resource_provider.get_scheme_handler("logs")

    # Add some logs
    logs_handler.add_log("INFO", "Test info message", user="alice")
    logs_handler.add_log("ERROR", "Test error message", code=500)
    logs_handler.add_log("WARNING", "Test warning message")

    # Get all logs
    all_logs = await manager.get_resource("logs://app/all")
    assert len(all_logs) == 3

    # Get error logs
    errors = await manager.get_resource("logs://app/errors")
    assert len(errors) == 1
    assert errors[0]["level"] == "ERROR"

    # Get with limit
    limited = await manager.get_resource("logs://app/all?limit=2")
    assert len(limited) == 2

    print("✓ logs:// scheme works")


async def test_metrics_scheme():
    """
    Test metrics:// scheme for metrics access.
    """
    print("Testing metrics:// scheme...")

    manager = setup_mcp(with_extended_schemes=True)

    # Get metrics handler
    from pheno.ports.mcp import ResourceProvider

    resource_provider = manager.container.resolve(ResourceProvider)
    metrics_handler = resource_provider.get_scheme_handler("metrics")

    # Record some metrics
    metrics_handler.record_counter("http_requests_total", 1, status="200")
    metrics_handler.record_counter("http_requests_total", 1, status="404")
    metrics_handler.record_gauge("memory_usage_bytes", 1024000)
    metrics_handler.record_histogram("response_time_seconds", 0.123)
    metrics_handler.record_histogram("response_time_seconds", 0.456)

    # Get all metrics
    all_metrics = await manager.get_resource("metrics://all")
    assert "counters" in all_metrics
    assert "gauges" in all_metrics
    assert "histograms" in all_metrics

    # Get specific counter
    counters = await manager.get_resource("metrics://counters/http_requests_total")
    assert len(counters) == 2

    # Get gauge
    gauges = await manager.get_resource("metrics://gauges/memory_usage_bytes")
    assert len(gauges) == 1

    print("✓ metrics:// scheme works")


async def run_all_tests():
    """
    Run all async tests.
    """
    print("\n" + "=" * 60)
    print("Running MCP Tests")
    print("=" * 60 + "\n")

    tests = [
        test_setup_mcp,
        test_connect_disconnect,
        test_register_and_execute_tool,
        test_list_tools,
        test_resource_access,
        test_memory_scheme,
        test_session_management,
        test_monitoring,
        test_tool_with_monitoring,
        test_custom_container,
        test_error_handling,
        test_env_scheme,
        test_file_scheme,
        test_logs_scheme,
        test_metrics_scheme,
    ]

    passed = 0
    failed = 0

    for test in tests:
        try:
            await test()
            passed += 1
        except Exception as e:
            print(f"✗ {test.__name__} failed: {e}")
            import traceback

            traceback.print_exc()
            failed += 1

    print("\n" + "=" * 60)
    print(f"Results: {passed} passed, {failed} failed")
    print("=" * 60 + "\n")

    return failed == 0


if __name__ == "__main__":
    success = asyncio.run(run_all_tests())
    sys.exit(0 if success else 1)
