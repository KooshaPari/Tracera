import asyncio
from types import SimpleNamespace

import pytest
from fastmcp.exceptions import ToolError

from tracertm.mcp.tools import param as param_tools


@pytest.mark.asyncio
async def test_config_manage_set_get(tmp_path, monkeypatch) -> None:
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
async def test_sync_manage_status(monkeypatch) -> None:
    class FakeState:
        status = SimpleNamespace(value="idle")
        last_sync = None
        pending_changes = 2
        conflicts_count = 0
        last_error = None

    class FakeSync:
        def get_status(self):
            return FakeState()

        async def sync(self, force=False):  # noqa: ARG002
            return SimpleNamespace(
                success=True,
                entities_synced=0,
                conflicts=[],
                errors=[],
                duration_seconds=0.1,
            )

        async def pull_changes(self):
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
    assert result["data"]["pending_changes"] == 2


@pytest.mark.asyncio
async def test_project_scope_enforced(monkeypatch) -> None:
    token = SimpleNamespace(claims={"project_ids": ["proj-1", "proj-2"]})
    monkeypatch.setattr(param_tools, "_get_access_token_from_ctx", lambda: token)

    async def noop_select_project(project_id):
        await asyncio.sleep(0)
        return {"project_id": project_id}

    async def noop_query_items(**_kwargs):
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
async def test_saved_queries_manage(tmp_path, monkeypatch) -> None:
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
async def test_test_manage_discover(monkeypatch) -> None:
    dummy = [
        SimpleNamespace(
            path="tests/unit/test_example.py",
            language="python",
            package=None,
        ),
    ]
    from tracertm.cli.commands.test.discovery import TestDiscovery

    monkeypatch.setattr(TestDiscovery, "discover", lambda self, languages=None, scope="all": dummy)  # noqa: ARG005
    result = await param_tools._test_manage_impl(action="discover", payload={}, ctx=None)
    assert result["data"]["count"] == 1
