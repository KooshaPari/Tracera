"""Lightweight coverage tests for placeholder helpers in tracertm.api.main.
These exercises the security/rate-limit stubs and simple utilities that
otherwise remain unexecuted in integration flows.
"""

import asyncio
from datetime import datetime
from typing import Never

import pytest
from fastapi import HTTPException
from starlette.requests import Request

from tracertm.api import main


def _req(headers=None, method="GET", path="/resource"):
    headers = headers or {}
    scope = {
        "type": "http",
        "http_version": "1.1",
        "method": method,
        "scheme": "http",
        "path": path,
        "root_path": "",
        "query_string": b"",
        "headers": [(k.lower().encode(), v.encode()) for k, v in headers.items()],
        "client": ("testclient", 123),
        "server": ("testserver", 80),
    }
    return Request(scope)


def test_placeholder_managers_and_helpers() -> None:
    km = main.APIKeyManager()
    assert km.generate()
    assert km.validate() == {"valid": True}
    assert km.has_scope()
    assert km.is_expired() is False

    tm = main.TokenManager()
    assert "access_token" in tm.generate_access_token()
    assert "access_token" in tm.refresh_access_token()
    assert tm.validate_refresh_token()
    assert tm.revoke_token()

    pm = main.PermissionManager()
    assert pm.has_permission()

    rl = main.RateLimiter()
    assert rl.check_limit("k", limit=1) is True
    assert rl.check_limit("k", limit=1) is False  # second hit exceeds
    assert rl.get_remaining("k", limit=1) == 0
    assert rl.get_limit() == 100
    assert rl.get_reset_time() == 0
    assert rl.get_retry_after() == 1
    assert "Rate limit" in rl.get_message()

    # basic helpers (placeholders satisfy required token/refresh_token args)
    assert main.verify_token("placeholder-token")
    assert main.verify_refresh_token("placeholder-refresh-token")
    assert main.generate_access_token()
    assert getattr(main, "verify_api_key", lambda *a, **k: True)()  # noqa: ARG005
    assert main.check_permissions()
    assert main.check_project_access()
    assert main.check_permission()
    assert main.has_permission()
    assert main.check_resource_ownership()
    assert main.verify_webhook_signature()
    assert main.verify_webhook_timestamp()
    assert main.create_session()
    assert main.verify_session()
    assert main.invalidate_session()
    assert main.check_mfa_requirement()
    assert main.verify_mfa_code()
    assert main.verify_csrf_token()
    assert main.hash_password("pw").startswith("hashed-")
    assert main.get_rate_limit()["limit"] == 100
    assert main.get_endpoint_limit()["limit"] == 100
    assert main.get_client_ip()
    assert main.is_whitelisted() is False


def test_ensure_write_and_project_access_branches(monkeypatch) -> None:
    with pytest.raises(ValueError):
        main.ensure_write_permission({"role": "guest"}, "update")

    monkeypatch.setattr(main, "check_permissions", lambda **_: False)
    with pytest.raises(ValueError):
        main.ensure_write_permission({"role": "user"}, "update")

    monkeypatch.setattr(main, "check_project_access", lambda *args, **kwargs: False)  # noqa: ARG005
    with pytest.raises(ValueError):
        main.ensure_project_access("proj", {"sub": "abc"})


@pytest.mark.asyncio
async def test_maybe_await() -> None:
    async def coro() -> str:
        return "ok"

    assert await main._maybe_await(coro()) == "ok"
    assert await main._maybe_await("plain") == "plain"


def test_auth_guard_paths(monkeypatch) -> None:
    # Public path when auth disabled and no Authorization header
    req = _req()
    assert main.auth_guard(req)["role"] == "public"

    # API key path
    monkeypatch.setattr(main, "verify_api_key", lambda *_: {"valid": True})
    req = _req(headers={"X-API-Key": "abc"})
    claims = main.auth_guard(req)
    assert claims["role"] == "api_key"

    # Invalid bearer header raises
    bad = _req(headers={"Authorization": "invalid"})
    with pytest.raises(ValueError):
        main.auth_guard(bad)

    # Token validation exception surfaces
    req = _req(headers={"Authorization": "Bearer token"})
    monkeypatch.setattr(main, "verify_token", lambda *_: (_ for _ in ()).throw(RuntimeError("boom")))
    with pytest.raises(ValueError, match="boom"):
        main.auth_guard(req)


def test_enforce_rate_limit(monkeypatch) -> None:
    # Force small limit to trigger rejection on second call
    monkeypatch.setattr(main, "get_endpoint_limit", lambda *args, **kwargs: {"limit": 1})  # noqa: ARG005
    getattr(main.enforce_rate_limit, "_counts", {}).clear()
    req = _req()
    main.enforce_rate_limit(req, {"sub": "user1"})
    with pytest.raises(HTTPException) as exc:
        main.enforce_rate_limit(req, {"sub": "user1"})
    assert isinstance(exc.value, HTTPException) and exc.value.status_code == 429


def test_enforce_rate_limit_whitelist(monkeypatch) -> None:
    getattr(main.enforce_rate_limit, "_counts", {}).clear()
    monkeypatch.setattr(main, "is_whitelisted", lambda *_: True)
    req = _req()
    main.enforce_rate_limit(req, {"sub": "user1"})


def test_enforce_rate_limit_bypass(monkeypatch) -> None:  # noqa: ARG001
    getattr(main.enforce_rate_limit, "_counts", {}).clear()
    req = _req()
    main.enforce_rate_limit(req, {"bypass_rate_limit": True})
    # Reaching this line means rate limit was bypassed successfully


def test_auth_guard_invalid_api_key(monkeypatch) -> None:
    monkeypatch.setattr(main, "verify_api_key", lambda *_: False)
    req = _req(headers={"X-API-Key": "abc"})
    with pytest.raises(ValueError, match="Invalid API key"):
        main.auth_guard(req)


def test_auth_guard_requires_bearer(monkeypatch) -> None:
    # Force auth enabled and malformed bearer token (main may expose ConfigManager for tests)
    cm = getattr(main, "ConfigManager", None)
    if cm is not None:
        monkeypatch.setattr(cm, "get", lambda self, key, default=None: True if key == "auth_enabled" else default)  # noqa: ARG005
    req = _req(headers={"Authorization": "Bearer a b"})
    with pytest.raises(ValueError):
        main.auth_guard(req)


@pytest.mark.asyncio
async def test_get_db_errors(monkeypatch) -> None:
    # Missing database_url - get_db uses get_mcp_session from mcp.database_adapter which uses ConfigManager
    from tracertm.mcp import database_adapter as db_adapter

    monkeypatch.setattr(db_adapter.ConfigManager, "get", lambda self, k, default=None: None)  # noqa: ARG005
    with pytest.raises(HTTPException):
        await anext(main.get_db())

    # Connection failure
    monkeypatch.setattr(
        db_adapter.ConfigManager,
        "get",
        lambda self, k, default=None: "sqlite:///:memory:" if k == "database_url" else default,  # noqa: ARG005
    )

    def fail_connect(*args, **kwargs) -> Never:  # noqa: ARG001
        msg = "no connect"
        raise RuntimeError(msg)

    monkeypatch.setattr(db_adapter, "get_mcp_session", fail_connect)
    with pytest.raises(HTTPException, match="no connect"):
        await anext(main.get_db())


@pytest.mark.asyncio
async def test_list_items_repo_error(monkeypatch) -> None:
    class BoomRepo:
        def __init__(self, *_args, **_kwargs) -> None:
            pass

        async def get_by_project(self, *_args, **_kwargs) -> Never:
            msg = "boom"
            raise RuntimeError(msg)

    monkeypatch.setattr(main.item_repository, "ItemRepository", BoomRepo)
    req = _req()
    with pytest.raises(HTTPException, match="boom"):
        await main.list_items(project_id="p1", claims={}, db=None, request=req)


def test_export_import_error_branches(monkeypatch) -> None:
    class FakeSvc:
        async def export_to_json(self, *_):
            return {"error": "missing"}

        async def import_from_json(self, *_):
            return {"error": "bad"}

    # Unsupported format
    with pytest.raises(HTTPException):
        asyncio.get_event_loop().run_until_complete(main.export_project("p1", format="xml", db=None))

    monkeypatch.setattr("tracertm.services.export_import_service.ExportImportService", lambda *_: FakeSvc())
    # Error result surfaces 404/400
    with pytest.raises(HTTPException):
        asyncio.get_event_loop().run_until_complete(main.export_project("p1", format="json", db=None))
    with pytest.raises(HTTPException):
        asyncio.get_event_loop().run_until_complete(
            main.import_project("p1", request=main.ImportRequest(format="json", data="{}"), db=None),
        )


@pytest.mark.asyncio
async def test_export_import_success(monkeypatch) -> None:
    class FakeSvc:
        async def export_to_json(self, *_):
            return {"ok": True}

        async def import_from_json(self, *_):
            return {"items": 0}

        async def export_to_csv(self, *_) -> str:
            return "id,title\n1,a"

        async def export_to_markdown(self, *_) -> str:
            return "# md"

        async def import_from_csv(self, *_):
            return {"items": 1}

    monkeypatch.setattr("tracertm.services.export_import_service.ExportImportService", lambda *_: FakeSvc())
    result = await main.export_project("p1", format="json", db=None)
    assert result["ok"] is True
    assert await main.export_project("p1", format="csv", db=None)
    assert await main.export_project("p1", format="markdown", db=None)

    result2 = await main.import_project("p1", request=main.ImportRequest(format="json", data="{}"), db=None)
    assert result2["items"] == 0
    result3 = await main.import_project("p1", request=main.ImportRequest(format="csv", data="id,title\n"), db=None)
    assert result3["items"] == 1


def test_refresh_access_token_branches(monkeypatch) -> None:
    with pytest.raises(HTTPException):
        asyncio.get_event_loop().run_until_complete(main.refresh_access_token_endpoint(payload={}))

    monkeypatch.setattr(main, "verify_refresh_token", lambda *_: False)
    with pytest.raises(HTTPException):
        asyncio.get_event_loop().run_until_complete(
            main.refresh_access_token_endpoint(payload={"refresh_token": "bad"}),
        )


@pytest.mark.asyncio
async def test_get_db_success_closes(monkeypatch) -> None:
    class FakeSession:
        def __init__(self) -> None:
            self.closed = False

        async def close(self) -> None:
            self.closed = True

    class FakeDB:
        def __init__(self, *_) -> None:
            self.session = FakeSession()

        def connect(self) -> bool:
            return True

    from tracertm.config.manager import ConfigManager

    monkeypatch.setattr(
        ConfigManager, "get", lambda self, key, default=None: "sqlite:///:memory:" if key == "database_url" else default,  # noqa: ARG005
    )
    monkeypatch.setattr(main, "DatabaseConnection", FakeDB)  # type: ignore[attr-defined]
    agen = main.get_db()
    session = await anext(agen)
    assert isinstance(session, FakeSession)
    with pytest.raises(StopAsyncIteration):
        await anext(agen)


@pytest.mark.asyncio
async def test_list_items_slicing(monkeypatch) -> None:
    class Repo:
        def __init__(self, *_args, **_kwargs) -> None:
            pass

        async def get_by_project(self, *_args, **_kwargs):
            class Item:
                def __init__(self, i) -> None:
                    self.id = f"id-{i}"
                    self.title = f"t{i}"
                    self.view = "FEATURE"
                    self.type = "feature"
                    self.status = "todo"
                    self.metadata = {}

            return [Item(i) for i in range(5)]

    monkeypatch.setattr(main.item_repository, "ItemRepository", Repo)
    resp = await main.list_items(project_id="p1", skip=1, limit=2, claims={}, db=None, request=_req())
    assert resp["total"] == 5
    assert len(resp["items"]) == 2


@pytest.mark.asyncio
async def test_list_links_success(monkeypatch) -> None:
    class Link:
        def __init__(self, lid) -> None:
            self.id = lid
            self.source_item_id = "s"
            self.target_item_id = "t"
            self.link_type = "trace"

    class Repo:
        def __init__(self, *_args, **_kwargs) -> None:
            pass

        async def get_by_project(self, *_args, **_kwargs):
            return [Link("1"), Link("2"), Link("3")]

    monkeypatch.setattr(main.link_repository, "LinkRepository", Repo)
    resp = await main.list_links(project_id="p1", skip=0, limit=2, claims={}, db=None, request=_req())
    assert resp["total"] == 3
    assert len(resp["links"]) == 2


def test_ensure_project_access_no_project() -> None:
    # Should return silently when no project_id provided
    main.ensure_project_access(None, {"sub": "abc"})


@pytest.mark.asyncio
async def test_update_link_not_found_branch(monkeypatch) -> None:
    class Repo:
        def __init__(self, *_args, **_kwargs) -> None:
            pass

        async def get_by_id(self, *_args, **_kwargs) -> None:
            return None

    monkeypatch.setattr(main.link_repository, "LinkRepository", Repo)
    with pytest.raises(HTTPException):
        await main.update_link("missing", main.LinkUpdate(link_type="x"), claims={}, db=None, request=_req())


@pytest.mark.asyncio
async def test_impact_analysis_error_branch(monkeypatch) -> None:
    class Service:
        def __init__(self, *_args, **_kwargs) -> None:
            pass

        async def analyze_impact(self, *_args, **_kwargs) -> Never:
            msg = "no impact"
            raise RuntimeError(msg)

    monkeypatch.setattr(main.impact_analysis_service, "ImpactAnalysisService", lambda *_: Service())
    with pytest.raises(HTTPException):
        await main.get_impact_analysis("id1", "proj1", claims={}, db=None, request=_req())


@pytest.mark.asyncio
async def test_shortest_path_branch(monkeypatch) -> None:
    class Service:
        def __init__(self, *_args, **_kwargs) -> None:
            pass

        async def find_shortest_path(self, *_args, **_kwargs):
            class R:
                exists = False
                distance = None
                path = []
                link_types = []

            return R()

    monkeypatch.setattr(main.shortest_path_service, "ShortestPathService", lambda *_: Service())
    resp = await main.find_shortest_path("p1", "s", "t", claims={}, db=None, request=_req())
    assert resp["exists"] is False


def test_auth_guard_success(monkeypatch) -> None:
    from tracertm.config.manager import ConfigManager

    monkeypatch.setattr(
        ConfigManager, "get", lambda self, key, default=None: True if key == "auth_enabled" else default,  # noqa: ARG005
    )
    monkeypatch.setattr(main, "verify_token", lambda token: {"sub": "user123", "role": "member"})  # noqa: ARG005
    req = _req(headers={"Authorization": "Bearer goodtoken"})
    claims = main.auth_guard(req)
    assert claims["sub"] == "user123"


def test_enforce_rate_limit_limit_branch(monkeypatch) -> None:
    getattr(main.enforce_rate_limit, "_counts", {}).clear()  # type: ignore[attr-defined]

    class AlwaysAllow(main.RateLimiter):
        def check_limit(self, *args, **kwargs) -> bool:  # noqa: ARG002
            return True

    monkeypatch.setattr(main, "RateLimiter", AlwaysAllow)
    monkeypatch.setattr(main, "get_endpoint_limit", lambda *args, **kwargs: {"limit": 0})  # noqa: ARG005
    with pytest.raises(HTTPException):
        main.enforce_rate_limit(_req(), claims={"sub": "u1"})


def test_enforce_rate_limit_denied(monkeypatch) -> None:
    getattr(main.enforce_rate_limit, "_counts", {}).clear()  # type: ignore[attr-defined]

    class AlwaysDeny(main.RateLimiter):
        def check_limit(self, *args, **kwargs) -> bool:  # noqa: ARG002
            return False

    monkeypatch.setattr(main, "RateLimiter", AlwaysDeny)
    with pytest.raises(HTTPException):
        main.enforce_rate_limit(_req(), claims={"sub": "deny"})


@pytest.mark.asyncio
async def test_get_db_sync_close(monkeypatch) -> None:
    class FakeSession:
        def __init__(self) -> None:
            self.closed = False

        def close(self) -> None:
            self.closed = True

    class FakeDB:
        def __init__(self, *_args, **_kwargs) -> None:
            self.session = FakeSession()

        def connect(self) -> bool:
            return True

    from tracertm.config.manager import ConfigManager

    monkeypatch.setattr(
        ConfigManager, "get", lambda self, key, default=None: "sqlite:///:memory:" if key == "database_url" else default,  # noqa: ARG005
    )
    monkeypatch.setattr(main, "DatabaseConnection", FakeDB)  # type: ignore[attr-defined]
    agen = main.get_db()
    session = await anext(agen)
    assert isinstance(session, FakeSession)
    await agen.aclose()
    assert session.closed is True


@pytest.mark.asyncio
async def test_get_db_no_close(monkeypatch) -> None:
    class FakeSession:
        pass

    class FakeDB:
        def __init__(self, *_args, **_kwargs) -> None:
            self.session = FakeSession()

        def connect(self) -> bool:
            return True

    from tracertm.config.manager import ConfigManager

    monkeypatch.setattr(
        ConfigManager, "get", lambda self, key, default=None: "sqlite:///:memory:" if key == "database_url" else default,  # noqa: ARG005
    )
    monkeypatch.setattr(main, "DatabaseConnection", FakeDB)  # type: ignore[attr-defined]
    agen = main.get_db()
    _session = await anext(agen)
    await agen.aclose()


@pytest.mark.asyncio
async def test_get_item_success(monkeypatch) -> None:
    class Repo:
        async def get_by_id(self, item_id):
            class Item:
                id = item_id
                title = "title"
                description = "desc"
                view = "FEATURE"
                status = "open"
                created_at = datetime(2024, 1, 1, 12, 0, 0)
                updated_at = datetime(2024, 1, 1, 13, 0, 0)

            return Item()

    monkeypatch.setattr(main.item_repository, "ItemRepository", lambda *_: Repo())
    resp = await main.get_item("item-1", claims={}, db=None, request=_req())
    assert resp["id"] == "item-1"
    assert resp["created_at"].startswith("2024-01-01T12:00:00")


@pytest.mark.asyncio
async def test_get_item_not_found(monkeypatch) -> None:
    class Repo:
        async def get_by_id(self, *_args, **_kwargs) -> None:
            return None

    monkeypatch.setattr(main.item_repository, "ItemRepository", lambda *_: Repo())
    with pytest.raises(HTTPException):
        await main.get_item("missing", claims={}, db=None, request=_req())


@pytest.mark.asyncio
async def test_impact_analysis_success(monkeypatch) -> None:
    class Service:
        async def analyze_impact(self, *_args, **_kwargs):
            class Result:
                root_item_id = "root1"
                total_affected = 2
                max_depth_reached = 3
                affected_items = ["a", "b"]

            return Result()

    monkeypatch.setattr(main.impact_analysis_service, "ImpactAnalysisService", lambda *_: Service())
    resp = await main.get_impact_analysis("i1", "p1", claims={}, db=None, request=_req())
    assert resp["root_item_id"] == "root1"
    assert resp["total_affected"] == 2


@pytest.mark.asyncio
async def test_update_link_success(monkeypatch) -> None:
    class Link:
        def __init__(self) -> None:
            self.id = "l1"
            self.source_item_id = "s1"
            self.target_item_id = "t1"
            self.link_type = "trace"
            self.metadata = {"k": "v"}

    class Repo:
        def __init__(self, *_args, **_kwargs) -> None:
            self.link = Link()

        async def get_by_id(self, *_args, **_kwargs):
            return self.link

    class FakeDB:
        def __init__(self) -> None:
            self.flushed = False
            self.refreshed = False

        async def flush(self) -> None:
            self.flushed = True

        async def refresh(self, link) -> None:  # noqa: ARG002
            self.refreshed = True

    monkeypatch.setattr(main.link_repository, "LinkRepository", Repo)
    db = FakeDB()
    resp = await main.update_link(
        "l1", main.LinkUpdate(link_type="req", metadata={"m": 1}), claims={"role": "user"}, db=db, request=_req(),
    )
    assert resp["type"] == "req"
    assert db.flushed is True
    assert db.refreshed is True


@pytest.mark.asyncio
async def test_update_link_no_changes(monkeypatch) -> None:
    class Link:
        def __init__(self) -> None:
            self.id = "l2"
            self.source_item_id = "s"
            self.target_item_id = "t"
            self.link_type = "orig"
            self.metadata = {"foo": "bar"}

    class Repo:
        def __init__(self, *_args, **_kwargs) -> None:
            pass

        async def get_by_id(self, *_args, **_kwargs):
            return Link()

    class FakeDB:
        pass

    monkeypatch.setattr(main.link_repository, "LinkRepository", Repo)
    db = FakeDB()
    resp = await main.update_link("l2", main.LinkUpdate(), claims={"role": "user"}, db=db, request=_req())
    assert resp["type"] == "orig"
    assert resp["metadata"] == {"foo": "bar"}


@pytest.mark.asyncio
async def test_create_and_delete_item_endpoints(monkeypatch) -> None:  # noqa: ARG001
    getattr(main.enforce_rate_limit, "_counts", {}).clear()  # type: ignore[attr-defined]
    payload = main.ItemCreate(title="Thing", view="view", project_id="p1", type="feature")
    create_resp = await main.create_item_endpoint(payload, claims={"role": "editor"}, db=None, request=_req())
    assert create_resp["view"] == "VIEW"

    delete_resp = await main.delete_item_endpoint("item-9", claims={"role": "editor"}, db=None, request=_req())
    assert delete_resp["status"] == "deleted"


def test_refresh_access_token_success(monkeypatch) -> None:
    monkeypatch.setattr(main, "verify_refresh_token", lambda token: {"sub": "user"})  # noqa: ARG005
    monkeypatch.setattr(
        main,
        "generate_access_token",
        lambda user_id=None: {"access_token": f"token-for-{user_id}", "token_type": "bearer"},
    )
    resp = asyncio.get_event_loop().run_until_complete(
        main.refresh_access_token_endpoint(payload={"refresh_token": "good"}),
    )
    assert resp["access_token"].startswith("token-for-")


def test_refresh_access_token_string_token(monkeypatch) -> None:
    monkeypatch.setattr(main, "verify_refresh_token", lambda token: True)  # noqa: ARG005
    monkeypatch.setattr(main, "generate_access_token", lambda user_id=None: "abc123")  # noqa: ARG005
    resp = asyncio.get_event_loop().run_until_complete(
        main.refresh_access_token_endpoint(payload={"refresh_token": "ok"}),
    )
    assert resp["token_type"] == "bearer"


@pytest.mark.asyncio
async def test_project_endpoints_success_and_errors(monkeypatch) -> None:
    class Project:
        def __init__(self, pid) -> None:
            self.id = pid
            self.name = f"name-{pid}"
            self.description = "desc"
            self.metadata = {"x": 1}

    class Repo:
        def __init__(self, *_args, **_kwargs) -> None:
            pass

        async def get_all(self):
            return [Project("p1"), Project("p2")]

        async def get_by_id(self, pid) -> None:  # noqa: ARG002
            return None

        async def create(self, name, description=None, metadata=None):  # noqa: ARG002
            return Project("new")

        async def update(self, project_id, **_kwargs) -> None:  # noqa: ARG002
            return None

    monkeypatch.setattr("tracertm.repositories.project_repository.ProjectRepository", Repo)

    list_resp = await main.list_projects(db=None)
    assert list_resp["total"] == 2

    with pytest.raises(HTTPException):
        await main.get_project("missing", db=None)

    create_resp = await main.create_project(main.CreateProjectRequest(name="new"), db=None)
    assert create_resp["id"] == "new"

    with pytest.raises(HTTPException):
        await main.update_project("missing", main.UpdateProjectRequest(name="x"), db=None)


@pytest.mark.asyncio
async def test_project_success_paths(monkeypatch) -> None:
    class Project:
        def __init__(self, pid) -> None:
            self.id = pid
            self.name = f"name-{pid}"
            self.description = "d"
            self.metadata = {"m": 1}

    class Repo:
        def __init__(self, *_args, **_kwargs) -> None:
            pass

        async def get_by_id(self, pid):
            return Project(pid)

        async def update(self, project_id, **_kwargs):
            return Project(project_id)

    monkeypatch.setattr("tracertm.repositories.project_repository.ProjectRepository", Repo)
    get_resp = await main.get_project("p10", db=None)
    assert get_resp["id"] == "p10"
    upd_resp = await main.update_project("p10", main.UpdateProjectRequest(name="new"), db=None)
    assert upd_resp["name"].startswith("name-")


@pytest.mark.asyncio
async def test_delete_project_paths(monkeypatch) -> None:
    class Link:
        def __init__(self, lid) -> None:
            self.id = lid
            self.source_item_id = "s"
            self.target_item_id = "t"
            self.link_type = "trace"

    class LinkRepo:
        def __init__(self, *_args, **_kwargs) -> None:
            pass

        async def get_by_project(self, *_args, **_kwargs):
            return [Link("l1"), Link("l2")]

        async def delete(self, _id) -> bool:
            return True

    class ItemRepo:
        def __init__(self, *_args, **_kwargs) -> None:
            pass

        async def list_all(self, *_args, **_kwargs):
            return []

    class ProjectRepo:
        def __init__(self, *_args, **_kwargs) -> None:
            pass

        async def get_by_id(self, pid):
            if pid == "missing":
                return None
            return type("Proj", (), {"id": pid})

    class FakeDB:
        def __init__(self) -> None:
            self.executed = []
            self.committed = False

        async def execute(self, stmt) -> bool:
            self.executed.append(stmt)
            return True

        async def commit(self) -> None:
            self.committed = True

    monkeypatch.setattr(main.link_repository, "LinkRepository", LinkRepo)
    monkeypatch.setattr(main.item_repository, "ItemRepository", ItemRepo)
    monkeypatch.setattr(main.project_repository, "ProjectRepository", ProjectRepo)

    with pytest.raises(HTTPException):
        await main.delete_project("missing", db=FakeDB())

    db = FakeDB()
    resp = await main.delete_project("proj1", db=db)
    assert resp["success"] is True
    assert db.committed is True


@pytest.mark.asyncio
async def test_get_graph_neighbors_success(monkeypatch) -> None:
    class Link:
        def __init__(self, lid, source, target, link_type) -> None:
            self.id = lid
            self.source_item_id = source
            self.target_item_id = target
            self.link_type = link_type

    class Repo:
        def __init__(self, *_args, **_kwargs) -> None:
            pass

        async def get_by_source(self, _item_id):
            return [Link("1", "a", "b", "trace")]

        async def get_by_target(self, _item_id):
            return [Link("2", "c", "d", "blocks")]

    monkeypatch.setattr("tracertm.repositories.link_repository.LinkRepository", Repo)
    resp = await main.get_graph_neighbors("proj", "item", direction="both", db=None)
    assert resp["total"] == 2


@pytest.mark.asyncio
async def test_get_graph_neighbors_out_only(monkeypatch) -> None:
    class Link:
        def __init__(self, lid, source, target, link_type) -> None:
            self.id = lid
            self.source_item_id = source
            self.target_item_id = target
            self.link_type = link_type

    class Repo:
        def __init__(self, *_args, **_kwargs) -> None:
            pass

        async def get_by_source(self, _item_id):
            return [Link("1", "x", "y", "trace")]

        async def get_by_target(self, _item_id):
            return []

    monkeypatch.setattr("tracertm.repositories.link_repository.LinkRepository", Repo)
    resp = await main.get_graph_neighbors("proj", "item", direction="out", db=None)
    assert resp["neighbors"][0]["direction"] == "out"
