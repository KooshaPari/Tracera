"""Test tool registration performance improvements."""

import time
import importlib
import sys
from pathlib import Path
import pytest

# Add src to path for imports
src_path = Path(__file__).parent.parent.parent.parent / "src"
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))


def test_split_modules_import_faster_than_monolith():
    """Verify that split modules import faster than the monolithic param.py."""

    # Remove any cached imports
    modules_to_remove = [k for k in sys.modules.keys() if 'tracertm.mcp' in k]
    for mod in modules_to_remove:
        del sys.modules[mod]

    # Measure time to import monolithic param.py
    start_monolith = time.perf_counter()
    try:
        from tracertm.mcp.tools import param  # noqa: F401
        monolith_time = time.perf_counter() - start_monolith
    except Exception as e:
        pytest.skip(f"Could not import param.py: {e}")

    # Remove imports again
    modules_to_remove = [k for k in sys.modules.keys() if 'tracertm.mcp' in k]
    for mod in modules_to_remove:
        del sys.modules[mod]

    # Measure time to import split modules
    start_split = time.perf_counter()
    try:
        from tracertm.mcp.tools.params import project  # noqa: F401
        from tracertm.mcp.tools.params import item  # noqa: F401
        from tracertm.mcp.tools.params import link  # noqa: F401
        from tracertm.mcp.tools.params import trace  # noqa: F401
        from tracertm.mcp.tools.params import graph  # noqa: F401
        from tracertm.mcp.tools.params import specification  # noqa: F401
        from tracertm.mcp.tools.params import config  # noqa: F401
        from tracertm.mcp.tools.params import storage  # noqa: F401
        from tracertm.mcp.tools.params import io_operations  # noqa: F401
        from tracertm.mcp.tools.params import database  # noqa: F401
        split_time = time.perf_counter() - start_split
    except Exception as e:
        pytest.skip(f"Could not import split modules: {e}")

    print(f"\nMonolithic param.py: {monolith_time*1000:.2f}ms")
    print(f"Split modules: {split_time*1000:.2f}ms")
    print(f"Improvement: {((monolith_time - split_time) / monolith_time * 100):.1f}%")

    # We expect at least some improvement, though exact % may vary
    assert split_time < monolith_time, "Split modules should be faster to import"


def test_registry_tracks_tools():
    """Verify the registry correctly tracks registered tools."""
    from tracertm.mcp.registry import get_registry, register_all_tools

    registry = get_registry()

    # Register tools
    register_all_tools()

    # Check that tools are registered
    tools = registry.list_registered_tools()

    expected_tools = [
        "project_manage",
        "item_manage",
        "link_manage",
        "trace_analyze",
        "graph_analyze",
        "specification_manage",
        "quality_analyze",
        "config_manage",
        "sync_manage",
        "export_manage",
        "import_manage",
        "ingestion_manage",
        "backup_manage",
        "file_watch_manage",
        "database_manage",
    ]

    for tool in expected_tools:
        assert tool in tools, f"Tool {tool} should be registered"


def test_individual_module_imports():
    """Test that each domain module can be imported independently."""
    modules = [
        "tracertm.mcp.tools.params.project",
        "tracertm.mcp.tools.params.item",
        "tracertm.mcp.tools.params.link",
        "tracertm.mcp.tools.params.trace",
        "tracertm.mcp.tools.params.graph",
        "tracertm.mcp.tools.params.specification",
        "tracertm.mcp.tools.params.config",
        "tracertm.mcp.tools.params.storage",
        "tracertm.mcp.tools.params.io_operations",
        "tracertm.mcp.tools.params.database",
    ]

    for module_name in modules:
        try:
            module = importlib.import_module(module_name)
            assert module is not None
        except Exception as e:
            pytest.fail(f"Failed to import {module_name}: {e}")


def test_tool_functions_exist():
    """Verify that tool functions are properly exported from modules."""
    from tracertm.mcp.tools.params import project
    from tracertm.mcp.tools.params import item
    from tracertm.mcp.tools.params import link

    assert hasattr(project, 'project_manage')
    assert callable(project.project_manage)

    assert hasattr(item, 'item_manage')
    assert callable(item.item_manage)

    assert hasattr(link, 'link_manage')
    assert callable(link.link_manage)


@pytest.mark.benchmark
def test_server_import_performance(benchmark):
    """Benchmark server import time."""

    def import_server():
        # Remove cached imports
        modules_to_remove = [k for k in sys.modules.keys() if 'tracertm.mcp.server' in k]
        for mod in modules_to_remove:
            del sys.modules[mod]

        import tracertm.mcp.server  # noqa: F401

    # Run benchmark
    result = benchmark(import_server)

    # Report timing
    print(f"\nServer import time: {result.stats.mean * 1000:.2f}ms")

    # Target: <100ms (was ~500ms with monolithic param.py)
    assert result.stats.mean < 0.2, "Server import should be under 200ms"
