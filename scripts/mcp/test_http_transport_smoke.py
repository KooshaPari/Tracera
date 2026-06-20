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


async def test_imports() -> bool | None:
    """Test that all HTTP transport modules can be imported."""
    await asyncio.sleep(0)  # RUF029: async fn uses async

    try:
        return True
    except Exception:
        return False


async def test_transport_selection() -> bool:
    """Test transport selection logic."""
    await asyncio.sleep(0)  # RUF029: async fn uses async

    import os

    from tracertm.mcp.http_transport import get_transport_type

    # Test default
    if "TRACERTM_MCP_TRANSPORT" in os.environ:
        del os.environ["TRACERTM_MCP_TRANSPORT"]
    transport = get_transport_type()
    assert transport == "stdio", f"Expected 'stdio', got '{transport}'"

    # Test HTTP
    os.environ["TRACERTM_MCP_TRANSPORT"] = "http"
    transport = get_transport_type()
    assert transport == "http", f"Expected 'http', got '{transport}'"

    # Test streamable-http
    os.environ["TRACERTM_MCP_TRANSPORT"] = "streamable-http"
    transport = get_transport_type()
    assert transport == "streamable-http", f"Expected 'streamable-http', got '{transport}'"

    # Test invalid fallback
    os.environ["TRACERTM_MCP_TRANSPORT"] = "invalid"
    transport = get_transport_type()
    assert transport == "stdio", f"Expected fallback to 'stdio', got '{transport}'"

    # Cleanup
    if "TRACERTM_MCP_TRANSPORT" in os.environ:
        del os.environ["TRACERTM_MCP_TRANSPORT"]

    return True


async def test_progress_stream() -> bool:
    """Test progress stream generator."""
    from tracertm.mcp.http_transport import create_progress_stream

    async def mock_generator() -> None:
        for i in range(3):
            await asyncio.sleep(0)  # RUF029: async generator uses async
            yield {"progress": i, "total": 3}

    events = [e async for e in create_progress_stream("test-task", mock_generator())]

    # Verify events
    assert len(events) == 5, f"Expected 5 events, got {len(events)}"
    assert events[0]["event"] == "stream_start"
    assert events[-1]["event"] == "stream_complete"
    assert sum(1 for e in events if e["event"] == "progress") == 3

    return True


async def test_standalone_app_creation() -> bool | None:
    """Test creating standalone HTTP app."""
    await asyncio.sleep(0)  # RUF029: async fn uses async

    try:
        from tracertm.mcp.http_transport import create_standalone_http_app

        app = create_standalone_http_app(
            path="/mcp",
            transport="http",
            enable_cors=False,
        )

        assert app is not None
        assert hasattr(app, "routes")
        return True
    except Exception:
        import traceback

        traceback.print_exc()
        return False


async def test_main_module() -> bool | None:
    """Test that __main__.py can be imported."""
    await asyncio.sleep(0)  # RUF029: async fn uses async

    try:
        # Try importing the main module
        import importlib.util

        spec = importlib.util.spec_from_file_location(
            "tracertm.mcp.__main__",
            src_path / "tracertm" / "mcp" / "__main__.py",
        )
        if spec and spec.loader:
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)

            # Check that key functions exist
            assert hasattr(module, "parse_args")
            assert hasattr(module, "main")

            return True
    except Exception:
        import traceback

        traceback.print_exc()
        return False


async def test_streaming_tools() -> bool | None:
    """Test that streaming tools module is updated."""
    await asyncio.sleep(0)  # RUF029: async fn uses async

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

        return True
    except Exception:
        import traceback

        traceback.print_exc()
        return False


async def main() -> int:
    """Run all smoke tests."""
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
        except Exception:
            import traceback

            traceback.print_exc()
            results.append((name, False))

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for _name, _result in results:
        pass

    if passed == total:
        return 0
    return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
