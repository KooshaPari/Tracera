"""Fix for API layer test isolation issues.

This conftest patch implements proper fixture cleanup and test isolation.
"""

import pathlib
import sqlite3
import tempfile
from typing import Any
from unittest.mock import MagicMock, patch

import pytest


@pytest.fixture(autouse=True)
def reset_mocks() -> None:
    """Reset all mock patches between tests to prevent state pollution."""
    yield
    # Clean up any dangling patches
    patch.stopall()


@pytest.fixture
def isolated_db_session() -> None:
    """Create an isolated database session that resets after each test."""
    # Create a fresh temporary database for each test
    temp_db = tempfile.NamedTemporaryFile(delete=False, suffix=".db")
    db_path = temp_db.name
    temp_db.close()

    try:
        # Initialize database
        conn = sqlite3.connect(db_path)
        conn.execute("PRAGMA foreign_keys = ON")
        conn.close()
        yield db_path
    finally:
        # Clean up database file after test
        if pathlib.Path(db_path).exists():
            try:
                pathlib.Path(db_path).unlink()
            except:
                pass


@pytest.fixture
def mock_api_config() -> None:
    """Provide a fresh mock API configuration for each test."""
    with patch("tracertm.api.client.ApiConfig") as mock_config:
        config_instance = MagicMock()
        config_instance.base_url = "http://localhost:8000"
        config_instance.api_key = "test-key"
        config_instance.timeout = 10
        config_instance.max_retries = 3
        mock_config.return_value = config_instance
        yield mock_config


@pytest.fixture
def mock_http_client() -> None:
    """Provide a fresh mock HTTP client for each test."""
    with patch("tracertm.api.client.httpx.Client") as mock_client:
        client_instance = MagicMock()
        mock_client.return_value = client_instance
        yield mock_client


@pytest.fixture
def api_test_isolation() -> None:
    """Ensure complete isolation between API tests."""
    # Setup
    import sys

    # Clear any cached imports
    modules_to_clear = [k for k in sys.modules if "tracertm.api" in k]
    original_modules = {k: sys.modules.pop(k) for k in modules_to_clear}

    yield

    # Teardown - restore original state
    for module_name, module in original_modules.items():
        sys.modules[module_name] = module

    # Clear any remaining patches
    patch.stopall()


# Marker for API tests that need special isolation handling
def pytest_configure(config: Any) -> None:
    """Register custom markers."""
    config.addinivalue_line("markers", "api_isolated: mark test as needing API isolation")
