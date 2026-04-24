import asyncio
from types import SimpleNamespace
from typing import Any

import pytest
from fastmcp.exceptions import ToolError

from tests.test_constants import COUNT_TWO
from tracertm.mcp.tools import param as param_tools


@pytest.mark.asyncio
async def test_config_manage_set_get(tmp_path: Any, monkeypatch: Any) -> None:
    monkeypatch.setenv("TRACERTM_CONFIG_DIR", str(tmp_path))

    result = await param_tools._config_manage_impl(
        action="set",
        payload={"key": "database_url", "value": "sqlite:///test.db"},
        ctx=None,
    )
    assert result["ok"] is True
    assert result["data"]["key"] == "database_url"

    fetched = await param_tools._config_manage_impl(
        action="get",
        payload={"key": "database_url"},
        ctx=None,
    )
    assert fetched["data"]["value"] == "sqlite:///test.db"


@pytest.mark.asyncio
async def test_sync_manage_status(monkeypatch: Any) -> None:
    class FakeState:
        status = SimpleNamespace(value="idle")
        last_sync = None
        pending_changes = 2
        conflicts_count = 0
        last_error = None

    class FakeSync:
        def get_status(self) -> None:
            return FakeState()

        async def sync(self, _force: Any = False) -> None:
            return SimpleNamespace(
                success=True,
                entities_synced=0,
                conflicts=[],
                errors=[],
                duration_seconds=0.1,
            )

        async def pull_changes(self) -> None:
            return SimpleNamespace(
                success=True,
                entities_synced=1,
                conflicts=[],
                errors=[],
                duration_seconds=0.1,
            )

    monkeypatch.setattr(param_tools, "_build_sync_engine", FakeSync)

    result = await param_tools._sync_manage_impl(action="status", payload={}, ctx=None)
    assert result["data"]["status"] == "idle"
    assert result["data"]["pending_changes"] == COUNT_TWO


@pytest.mark.asyncio
async def test_project_scope_enforced(monkeypatch: Any) -> None:
    token = SimpleNamespace(claims={"project_ids": ["proj-1", "proj-2"]})
    monkeypatch.setattr(param_tools, "_get_access_token_from_ctx", lambda: token)

    async def noop_select_project(project_id: Any) -> None:
        await asyncio.sleep(0)
        return {"project_id": project_id}

    async def noop_query_items(**_kwargs: Any) -> None:
        await asyncio.sleep(0)
        return {"items": []}

    monkeypatch.setattr(param_tools.core, "select_project", noop_select_project)
    monkeypatch.setattr(param_tools.core, "query_items", noop_query_items)

    with pytest.raises(ToolError, match="project_id required"):
        await param_tools._item_manage_impl(action="query", payload={}, ctx=SimpleNamespace())

    allowed = await param_tools._item_manage_impl(
        action="query",
        payload={"project_id": "proj-1"},
        ctx=SimpleNamespace(),
    )
    assert allowed["ok"] is True


@pytest.mark.asyncio
async def test_saved_queries_manage(tmp_path: Any, monkeypatch: Any) -> None:
    monkeypatch.setenv("HOME", str(tmp_path))

    saved = await param_tools._saved_queries_manage_impl(
        action="save",
        payload={"name": "my-query", "view": "FEATURE", "status": "todo"},
        ctx=None,
    )
    assert saved["data"]["saved"] == "my-query"

    listed = await param_tools._saved_queries_manage_impl(action="list", payload={}, ctx=None)
    assert "my-query" in listed["data"]["queries"]

    deleted = await param_tools._saved_queries_manage_impl(
        action="delete",
        payload={"name": "my-query"},
        ctx=None,
    )
    assert deleted["data"]["deleted"] == "my-query"


@pytest.mark.asyncio
async def test_test_manage_discover(monkeypatch: Any) -> None:
    dummy = [
        SimpleNamespace(
            path="tests/unit/test_example.py",
            language="python",
            package=None,
        ),
    ]
    from tracertm.cli.commands.test.discovery import TestDiscovery

    monkeypatch.setattr(TestDiscovery, "discover", lambda self, languages=None, _scope="all": dummy)
    result = await param_tools._test_manage_impl(action="discover", payload={}, ctx=None)
    assert result["data"]["count"] == 1
