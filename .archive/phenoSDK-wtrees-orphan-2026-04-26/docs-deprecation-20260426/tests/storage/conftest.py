"""
Configuration for storage tests.
"""

import inspect

import pytest


# Enable pytest-asyncio for all tests in this directory
def pytest_collection_modifyitems(items):
    """Add asyncio marker to all async tests."""
    for item in items:
        if inspect.iscoroutinefunction(item.function):
            item.add_marker(pytest.mark.asyncio)
