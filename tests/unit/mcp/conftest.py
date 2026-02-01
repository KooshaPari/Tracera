"""
Pytest configuration for MCP unit tests.
"""

import pytest
from pathlib import Path
import tempfile
import os

from sqlalchemy import text
from tracertm.config.manager import ConfigManager
from tracertm.mcp.database_adapter import get_async_engine, reset_engine
from tracertm.models.base import Base


@pytest.fixture(scope="session")
def temp_config_dir():
    """Create a temporary config directory for tests."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture(scope="session")
def test_database_url(temp_config_dir):
    """Provide a test database URL."""
    db_path = temp_config_dir / "test.db"
    return f"sqlite:///{db_path}"


@pytest.fixture(scope="function", autouse=True)
async def setup_test_database(test_database_url, temp_config_dir, monkeypatch):
    """Set up test database for each test."""
    # CRITICAL: Set environment variables BEFORE any imports or engine creation
    # This ensures ConfigManager picks up the test database URL
    monkeypatch.setenv("TRACERTM_CONFIG_DIR", str(temp_config_dir))
    monkeypatch.setenv("TRACERTM_DATABASE_URL", test_database_url)
    monkeypatch.setenv("DATABASE_URL", test_database_url)

    # Create a config file in the temp directory
    config_path = temp_config_dir / "config.yaml"
    config_path.parent.mkdir(parents=True, exist_ok=True)
    import yaml
    with open(config_path, "w") as f:
        yaml.safe_dump({
            "database_url": test_database_url,
            "current_project_id": None,
            "default_view": "FEATURE",
            "output_format": "table",
            "max_agents": 4,
            "log_level": "INFO",
        }, f)

    # Reset any existing engine
    await reset_engine()

    # Get async engine and create tables
    engine = await get_async_engine()

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield

    # Cleanup
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    await reset_engine()


@pytest.fixture
def config_manager(temp_config_dir, test_database_url):
    """Provide a ConfigManager instance for tests."""
    manager = ConfigManager(config_dir=temp_config_dir)
    manager.init(database_url=test_database_url)
    return manager
