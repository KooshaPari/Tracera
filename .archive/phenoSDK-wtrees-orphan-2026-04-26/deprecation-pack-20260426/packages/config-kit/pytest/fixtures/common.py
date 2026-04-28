"""
Common pytest fixtures for testing.

This module provides commonly used fixtures across different projects.
"""

import os
import shutil
import tempfile
from collections.abc import Generator
from pathlib import Path
from typing import Any
from unittest.mock import Mock

import pytest


@pytest.fixture
def temp_dir() -> Generator[Path, None, None]:
    """Create a temporary directory for testing."""
    temp_path = Path(tempfile.mkdtemp())
    try:
        yield temp_path
    finally:
        shutil.rmtree(temp_path, ignore_errors=True)


@pytest.fixture
def mock_client() -> Mock:
    """Create a mock client for testing."""
    client = Mock()
    client.call_tool = Mock(return_value={"success": True, "data": {}})
    client.list_tools = Mock(return_value={"tools": []})
    client.list_resources = Mock(return_value={"resources": []})
    return client


@pytest.fixture
def test_data() -> dict[str, Any]:
    """Provide test data for testing."""
    return {
        "user": {
            "id": "test-user-123",
            "name": "Test User",
            "email": "test@example.com",
            "roles": ["user"],
        },
        "organization": {
            "id": "test-org-123",
            "name": "Test Organization",
            "description": "Test organization for testing",
        },
        "project": {
            "id": "test-project-123",
            "name": "Test Project",
            "status": "active",
            "organization_id": "test-org-123",
        },
        "document": {
            "id": "test-doc-123",
            "title": "Test Document",
            "content": "Test document content",
            "project_id": "test-project-123",
        },
    }


@pytest.fixture
def performance_monitor() -> Generator[dict[str, Any], None, None]:
    """Monitor performance during test execution."""
    import time

    import psutil

    start_time = time.time()
    start_memory = psutil.Process().memory_info().rss / 1024 / 1024

    monitor_data = {
        "start_time": start_time,
        "start_memory": start_memory,
        "peak_memory": start_memory,
        "measurements": [],
    }

    def measure(name: str):
        current_time = time.time()
        current_memory = psutil.Process().memory_info().rss / 1024 / 1024

        measurement = {
            "name": name,
            "timestamp": current_time,
            "memory": current_memory,
            "duration": current_time - start_time,
        }

        monitor_data["measurements"].append(measurement)

        monitor_data["peak_memory"] = max(monitor_data["peak_memory"], current_memory)

        return measurement

    monitor_data["measure"] = measure

    try:
        yield monitor_data
    finally:
        end_time = time.time()
        end_memory = psutil.Process().memory_info().rss / 1024 / 1024

        monitor_data["end_time"] = end_time
        monitor_data["end_memory"] = end_memory
        monitor_data["total_duration"] = end_time - start_time
        monitor_data["memory_delta"] = end_memory - start_memory


@pytest.fixture
def security_context() -> dict[str, Any]:
    """Provide security context for testing."""
    return {
        "user_id": "test-user-123",
        "organization_id": "test-org-123",
        "roles": ["user"],
        "permissions": ["read", "write"],
        "auth_token": "test-token-123",
        "session_id": "test-session-123",
    }


@pytest.fixture
def mock_http_client() -> Mock:
    """Create a mock HTTP client for testing."""
    client = Mock()
    client.get = Mock(return_value=Mock(status_code=200, json=dict))
    client.post = Mock(return_value=Mock(status_code=201, json=dict))
    client.put = Mock(return_value=Mock(status_code=200, json=dict))
    client.delete = Mock(return_value=Mock(status_code=204, json=dict))
    return client


@pytest.fixture
def mock_database() -> Mock:
    """Create a mock database for testing."""
    db = Mock()
    db.execute = Mock(return_value=Mock(rowcount=1))
    db.fetchone = Mock(return_value={})
    db.fetchall = Mock(return_value=[])
    db.commit = Mock()
    db.rollback = Mock()
    return db


@pytest.fixture
def mock_cache() -> Mock:
    """Create a mock cache for testing."""
    cache = Mock()
    cache.get = Mock(return_value=None)
    cache.set = Mock(return_value=True)
    cache.delete = Mock(return_value=True)
    cache.clear = Mock(return_value=True)
    return cache


@pytest.fixture
def mock_message_broker() -> Mock:
    """Create a mock message broker for testing."""
    broker = Mock()
    broker.publish = Mock(return_value=True)
    broker.subscribe = Mock(return_value=Mock())
    broker.unsubscribe = Mock(return_value=True)
    return broker


@pytest.fixture
def mock_file_system() -> Mock:
    """Create a mock file system for testing."""
    fs = Mock()
    fs.exists = Mock(return_value=True)
    fs.read_text = Mock(return_value="test content")
    fs.write_text = Mock(return_value=10)
    fs.mkdir = Mock(return_value=True)
    fs.rmdir = Mock(return_value=True)
    fs.unlink = Mock(return_value=True)
    return fs


@pytest.fixture
def mock_logger() -> Mock:
    """Create a mock logger for testing."""
    logger = Mock()
    logger.debug = Mock()
    logger.info = Mock()
    logger.warning = Mock()
    logger.error = Mock()
    logger.critical = Mock()
    return logger


@pytest.fixture
def mock_config() -> Mock:
    """Create a mock configuration for testing."""
    config = Mock()
    config.get = Mock(return_value="default_value")
    config.set = Mock(return_value=True)
    config.has = Mock(return_value=True)
    return config


@pytest.fixture
def mock_environment() -> Generator[dict[str, str], None, None]:
    """Create a mock environment for testing."""
    original_env = os.environ.copy()

    test_env = {
        "TEST_MODE": "true",
        "TEST_DATABASE_URL": "sqlite:///:memory:",
        "TEST_CACHE_URL": "memory://",
        "TEST_MESSAGE_BROKER_URL": "memory://",
    }

    os.environ.update(test_env)

    try:
        yield test_env
    finally:
        os.environ.clear()
        os.environ.update(original_env)
