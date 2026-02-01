#!/usr/bin/env python
"""Smoke test for MCP HTTP transport implementation.

This validates that the HTTP transport layer is working without
requiring the full test environment.
"""

import asyncio
import sys
from pathlib import Path

# Add src to path
src_path = Path(__file__).parent.parent.parent / "src"
sys.path.insert(0, str(src_path))


async def test_imports():
    """Test that all HTTP transport modules can be imported."""
    print("Testing imports...")

    try:
        from tracertm.mcp.http_transport import (
            create_standalone_http_app,
            run_http_server,
            mount_mcp_to_fastapi,
            create_progress_stream,
            get_transport_type,
            DEFAULT_HTTP_HOST,
            DEFAULT_HTTP_PORT,
            DEFAULT_MCP_PATH,
        )
        print("✅ All HTTP transport imports successful")
        return True
    except Exception as e:
        print(f"❌ Import failed: {e}")
        return False


async def test_transport_selection():
    """Test transport selection logic."""
    print("\nTesting transport selection...")

    import os
    from tracertm.mcp.http_transport import get_transport_type

    # Test default
    if "TRACERTM_MCP_TRANSPORT" in os.environ:
        del os.environ["TRACERTM_MCP_TRANSPORT"]
    transport = get_transport_type()
    assert transport == "stdio", f"Expected 'stdio', got '{transport}'"
    print("✅ Default transport: stdio")

    # Test HTTP
    os.environ["TRACERTM_MCP_TRANSPORT"] = "http"
    transport = get_transport_type()
    assert transport == "http", f"Expected 'http', got '{transport}'"
    print("✅ HTTP transport selection works")

    # Test streamable-http
    os.environ["TRACERTM_MCP_TRANSPORT"] = "streamable-http"
    transport = get_transport_type()
    assert transport == "streamable-http", f"Expected 'streamable-http', got '{transport}'"
    print("✅ Streamable HTTP transport selection works")

    # Test invalid fallback
    os.environ["TRACERTM_MCP_TRANSPORT"] = "invalid"
    transport = get_transport_type()
    assert transport == "stdio", f"Expected fallback to 'stdio', got '{transport}'"
    print("✅ Invalid transport fallback works")

    # Cleanup
    if "TRACERTM_MCP_TRANSPORT" in os.environ:
        del os.environ["TRACERTM_MCP_TRANSPORT"]

    return True


async def test_progress_stream():
    """Test progress stream generator."""
    print("\nTesting progress stream...")

    from tracertm.mcp.http_transport import create_progress_stream

    async def mock_generator():
        for i in range(3):
            yield {"progress": i, "total": 3}

    events = []
    async for event in create_progress_stream("test-task", mock_generator()):
        events.append(event)

    # Verify events
    assert len(events) == 5, f"Expected 5 events, got {len(events)}"
    assert events[0]["event"] == "stream_start"
    assert events[-1]["event"] == "stream_complete"
    assert sum(1 for e in events if e["event"] == "progress") == 3

    print("✅ Progress stream works correctly")
    return True


async def test_standalone_app_creation():
    """Test creating standalone HTTP app."""
    print("\nTesting standalone app creation...")

    try:
        from tracertm.mcp.http_transport import create_standalone_http_app

        app = create_standalone_http_app(
            path="/mcp",
            transport="http",
            enable_cors=False,
        )

        assert app is not None
        assert hasattr(app, "routes")
        print("✅ Standalone HTTP app creation works")
        return True
    except Exception as e:
        print(f"❌ Standalone app creation failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_main_module():
    """Test that __main__.py can be imported."""
    print("\nTesting __main__ module...")

    try:
        # Try importing the main module
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "tracertm.mcp.__main__",
            src_path / "tracertm" / "mcp" / "__main__.py"
        )
        if spec and spec.loader:
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)

            # Check that key functions exist
            assert hasattr(module, "parse_args")
            assert hasattr(module, "main")

            print("✅ __main__ module loads correctly")
            return True
    except Exception as e:
        print(f"❌ __main__ module test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_streaming_tools():
    """Test that streaming tools module is updated."""
    print("\nTesting streaming tools...")

    try:
        from tracertm.mcp.tools import streaming

        # Check that the module has the expected functions
        assert hasattr(streaming, "stream_impact_analysis")
        assert hasattr(streaming, "get_matrix_page")
        assert hasattr(streaming, "get_impact_by_depth")
        assert hasattr(streaming, "get_items_page")
        assert hasattr(streaming, "get_links_page")

        # Check for logger
        assert hasattr(streaming, "logger")

        print("✅ Streaming tools module is properly configured")
        return True
    except Exception as e:
        print(f"❌ Streaming tools test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    """Run all smoke tests."""
    print("=" * 60)
    print("MCP HTTP Transport Smoke Tests")
    print("=" * 60)

    tests = [
        ("Imports", test_imports),
        ("Transport Selection", test_transport_selection),
        ("Progress Stream", test_progress_stream),
        ("Standalone App", test_standalone_app_creation),
        ("Main Module", test_main_module),
        ("Streaming Tools", test_streaming_tools),
    ]

    results = []
    for name, test_func in tests:
        try:
            result = await test_func()
            results.append((name, result))
        except Exception as e:
            print(f"❌ {name} failed with exception: {e}")
            import traceback
            traceback.print_exc()
            results.append((name, False))

    print("\n" + "=" * 60)
    print("Test Results Summary")
    print("=" * 60)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {name}")

    print("-" * 60)
    print(f"Total: {passed}/{total} tests passed")

    if passed == total:
        print("\n🎉 All smoke tests passed!")
        return 0
    else:
        print(f"\n❌ {total - passed} test(s) failed")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
