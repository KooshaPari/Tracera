"""Root conftest with manual pytest-asyncio integration.

Works around pytest-asyncio auto-discovery issues.
"""

import sys

# Manually import and register pytest-asyncio plugin
from typing import Any

import pytest


def pytest_configure(config: Any) -> None:
    """Manually register pytest-asyncio plugin."""
    try:
        from pytest_asyncio import plugin as asyncio_plugin

        config.pluginmanager.register(asyncio_plugin, name="asyncio")
    except Exception:
        pass

    # Register asyncio marker
    config.addinivalue_line(
        "markers",
        "asyncio: mark test as an asyncio coroutine",
    )
