"""Tests for auth, config, and database MCP tools.

Closes: https://github.com/KooshaPari/trace/issues/232

Strategy: patch out the FastMCP server singleton (tracertm.mcp.core) before
importing the tool module so the heavy MCP boot sequence is never triggered in
unit-test context.
"""

from __future__ import annotations

import sys
from pathlib import Path
from types import ModuleType
from unittest.mock import MagicMock, patch

import pytest

# ---------------------------------------------------------------------------
# Stub out tracertm.mcp.core BEFORE the tool module is imported so that the
# @mcp.tool() decorator calls are no-ops during test collection.
# ---------------------------------------------------------------------------


def _stub_mcp_core() -> None:
    """Insert a lightweight stub for tracertm.mcp.core into sys.modules."""
    if "tracertm.mcp.core" in sys.modules:
        return  # already stubbed by a previous test run in the same process

    stub = ModuleType("tracertm.mcp.core")
    mock_mcp = MagicMock()

    # Make @mcp.tool() a pass-through decorator (returns the function unchanged)
    def _passthrough_decorator(*_args: object, **_kwargs: object):  # type: ignore[return]
        def _wrap(fn):  # type: ignore[return]
            return fn

        return _wrap

    mock_mcp.tool = _passthrough_decorator
    stub.mcp = mock_mcp
    sys.modules["tracertm.mcp.core"] = stub

    # Ensure tracertm.mcp package is the real package (not overridden)
    import tracertm.mcp  # noqa: PLC0415 – intentional deferred import

    tracertm.mcp.core = stub  # type: ignore[attr-defined]


_stub_mcp_core()

# Now it is safe to import the tool functions directly
from tracertm.mcp.tools.auth_config_db import (  # noqa: E402
    auth_logout,
    auth_status,
    config_get,
    config_list,
    config_set,
    config_unset,
    db_init,
    db_migrate,
    db_reset,
    db_status,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture()
def mock_ctx() -> MagicMock:
    """Minimal MCP context mock – actor extraction is patched away."""
    return MagicMock()


# ---------------------------------------------------------------------------
# Auth Tools
# ---------------------------------------------------------------------------


def test_auth_status_no_token(mock_ctx: MagicMock) -> None:
    """auth_status returns authenticated=False when no token is stored."""
    with patch("tracertm.mcp.tools.auth_config_db.ConfigManager") as MockCM:
        mgr = MockCM.return_value
        mgr.get.return_value = None
        mgr.config_path = Path("/tmp/config.yaml")

        result = auth_status(mock_ctx)

    assert result["ok"] is True
    assert result["action"] == "auth_status"
    data = result["data"]
    assert data["authenticated"] is False
    assert data["has_token"] is False


def test_auth_status_with_token(mock_ctx: MagicMock) -> None:
    """auth_status returns authenticated=True when a token exists."""
    with patch("tracertm.mcp.tools.auth_config_db.ConfigManager") as MockCM:
        mgr = MockCM.return_value
        mgr.get.return_value = "tok_abc123"
        mgr.config_path = Path("/tmp/config.yaml")

        result = auth_status(mock_ctx)

    assert result["ok"] is True
    data = result["data"]
    assert data["authenticated"] is True
    assert data["has_token"] is True


def test_auth_logout_clears_token(mock_ctx: MagicMock) -> None:
    """auth_logout sets api_token to None and returns a confirmation message."""
    with patch("tracertm.mcp.tools.auth_config_db.ConfigManager") as MockCM:
        mgr = MockCM.return_value
        mgr.config_path = Path("/tmp/config.yaml")

        result = auth_logout(mock_ctx)

    assert result["ok"] is True
    assert result["action"] == "auth_logout"
    mgr.set.assert_called_once_with("api_token", None)
    assert "message" in result["data"]


# ---------------------------------------------------------------------------
# Config Tools
# ---------------------------------------------------------------------------


def test_config_get_returns_value(mock_ctx: MagicMock) -> None:
    """config_get returns the stored value for a key."""
    with patch("tracertm.mcp.tools.auth_config_db.ConfigManager") as MockCM:
        mgr = MockCM.return_value
        mgr.get.return_value = "proj-001"

        result = config_get(mock_ctx, key="current_project_id")

    assert result["ok"] is True
    assert result["action"] == "config_get"
    assert result["data"]["key"] == "current_project_id"
    assert result["data"]["value"] == "proj-001"


def test_config_set_persists_value(mock_ctx: MagicMock) -> None:
    """config_set calls set on the manager and echoes key/value."""
    with patch("tracertm.mcp.tools.auth_config_db.ConfigManager") as MockCM:
        mgr = MockCM.return_value

        result = config_set(mock_ctx, key="current_project_id", value="proj-999")

    assert result["ok"] is True
    assert result["action"] == "config_set"
    mgr.set.assert_called_once_with("current_project_id", "proj-999")
    assert result["data"]["key"] == "current_project_id"
    assert result["data"]["value"] == "proj-999"


def test_config_unset_clears_key(mock_ctx: MagicMock) -> None:
    """config_unset sets the key to None in the manager."""
    with patch("tracertm.mcp.tools.auth_config_db.ConfigManager") as MockCM:
        mgr = MockCM.return_value

        result = config_unset(mock_ctx, key="current_project_id")

    assert result["ok"] is True
    assert result["action"] == "config_unset"
    mgr.set.assert_called_once_with("current_project_id", None)


@pytest.mark.asyncio
async def test_config_list_returns_all_keys(mock_ctx: MagicMock) -> None:
    """config_list returns every config key including a count."""
    fake_config = {
        "database_url": None,
        "current_project_id": "proj-1",
        "output_format": "table",
        "api_token": None,
    }

    with patch("tracertm.mcp.tools.auth_config_db.ConfigManager") as MockCM:
        mgr = MockCM.return_value
        mgr.get_all.return_value = fake_config

        result = await config_list(mock_ctx)

    assert result["ok"] is True
    assert result["action"] == "config_list"
    assert result["data"]["count"] == len(fake_config)
    assert result["data"]["config"]["api_token"] is None


# ---------------------------------------------------------------------------
# Database Tools
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_db_status_no_url_returns_error(mock_ctx: MagicMock) -> None:
    """db_status returns NO_DATABASE_URL when no database_url is configured."""
    from tracertm.config.schema import Config

    with patch("tracertm.mcp.tools.auth_config_db.ConfigManager") as MockCM:
        mgr = MockCM.return_value
        mgr.load.return_value = Config(database_url=None)

        result = await db_status(mock_ctx)

    assert result["ok"] is False
    assert result["error_code"] == "NO_DATABASE_URL"


@pytest.mark.asyncio
async def test_db_migrate_no_url_returns_error(mock_ctx: MagicMock) -> None:
    """db_migrate returns NO_DATABASE_URL when no database_url is configured."""
    from tracertm.config.schema import Config

    with patch("tracertm.mcp.tools.auth_config_db.ConfigManager") as MockCM:
        mgr = MockCM.return_value
        mgr.load.return_value = Config(database_url=None)

        result = await db_migrate(mock_ctx)

    assert result["ok"] is False
    assert result["error_code"] == "NO_DATABASE_URL"


@pytest.mark.asyncio
async def test_db_reset_requires_confirm(mock_ctx: MagicMock) -> None:
    """db_reset returns CONFIRMATION_REQUIRED when confirm=False (default)."""
    result = await db_reset(mock_ctx, confirm=False)

    assert result["ok"] is False
    assert result["error_code"] == "CONFIRMATION_REQUIRED"


@pytest.mark.asyncio
async def test_db_init_sets_url_and_succeeds(mock_ctx: MagicMock) -> None:
    """db_init stores the database_url and returns a success response."""
    with patch("tracertm.mcp.tools.auth_config_db.ConfigManager") as MockCM:
        mgr = MockCM.return_value
        mgr.config_path = Path("/tmp/test/config.yaml")

        result = await db_init(mock_ctx, database_url="sqlite:///test.db")

    assert result["ok"] is True
    assert result["action"] == "db_init"
    mgr.set.assert_called_once_with("database_url", "sqlite:///test.db")
