"""
Test configuration for unit tests.
"""

import pytest

# Configure pytest-asyncio
pytest_plugins = ("pytest_asyncio",)


@pytest.fixture(scope="session")
def event_loop_policy():
    """Set the event loop policy for all async tests."""
    import asyncio

    return asyncio.DefaultEventLoopPolicy()
