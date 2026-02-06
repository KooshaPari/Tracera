"""
Root conftest with manual pytest-asyncio integration.
Works around pytest-asyncio auto-discovery issues.
"""
import sys
import pytest

# Manually import and register pytest-asyncio plugin
def pytest_configure(config):
    """Manually register pytest-asyncio plugin."""
    try:
        from pytest_asyncio import plugin as asyncio_plugin
        config.pluginmanager.register(asyncio_plugin, name="asyncio")
        print("✓ pytest-asyncio plugin registered successfully")
    except Exception as e:
        print(f"✗ Failed to register pytest-asyncio: {e}")
        
    # Register asyncio marker
    config.addinivalue_line(
        "markers", "asyncio: mark test as an asyncio coroutine"
    )
