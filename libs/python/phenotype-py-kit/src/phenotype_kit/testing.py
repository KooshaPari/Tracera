"""Shared pytest fixtures and testing utilities for Phenotype services.

Provides common fixtures for temporary directories, mock configuration,
and test setup/teardown utilities.

Example:
    >>> # In conftest.py:
    >>> from phenotype_kit.testing import tmp_dir, mock_config
    >>>
    >>> # In test files:
    >>> def test_something(tmp_dir, mock_config):
    ...     # tmp_dir is a temporary Path
    ...     # mock_config is a BaseConfig instance with defaults
    ...     pass
"""

import tempfile
from pathlib import Path
from typing import Any, Generator
from unittest.mock import MagicMock

import pytest

from phenotype_kit.config import BaseConfig, clear_settings_cache


@pytest.fixture
def tmp_dir() -> Generator[Path, None, None]:
    """Provide a temporary directory for tests.

    Yields:
        Temporary directory Path, cleaned up after test
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def mock_config() -> BaseConfig:
    """Provide a BaseConfig instance with test defaults.

    Returns:
        BaseConfig with environment=test and debug=True
    """
    clear_settings_cache()
    return BaseConfig(
        environment="test",
        debug=True,
        log_level="DEBUG",
    )


@pytest.fixture
def mock_request_context() -> dict[str, Any]:
    """Provide mock request context data.

    Returns:
        Dictionary with request ID, correlation ID, and other context
    """
    return {
        "request_id": "test-req-123",
        "correlation_id": "test-corr-456",
        "user_id": "test-user",
        "timestamp": "2024-01-01T00:00:00Z",
    }


class AsyncTestHelper:
    """Helper utilities for async testing."""

    @staticmethod
    async def wait_for_condition(
        condition_fn: callable,
        timeout_seconds: float = 5.0,
        poll_interval: float = 0.1,
    ) -> bool:
        """Wait for an async condition to become true.

        Args:
            condition_fn: Async callable that returns bool
            timeout_seconds: Maximum time to wait
            poll_interval: Time between condition checks

        Returns:
            True if condition became true, False if timed out
        """
        import asyncio

        start_time = asyncio.get_event_loop().time()
        while asyncio.get_event_loop().time() - start_time < timeout_seconds:
            if await condition_fn():
                return True
            await asyncio.sleep(poll_interval)
        return False


@pytest.fixture
def async_helper() -> AsyncTestHelper:
    """Provide async test helper.

    Returns:
        AsyncTestHelper instance
    """
    return AsyncTestHelper()
