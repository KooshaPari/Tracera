from types import SimpleNamespace
from typing import Any, Never, cast

import pytest
from sqlalchemy.orm.exc import StaleDataError

from tracertm.api import client as client_mod
from tracertm.api.client import TraceRTMClient
from tracertm.services.concurrent_operations_service import ConcurrencyError


def test_init_without_database_url_raises(monkeypatch) -> None:
    class FakeConfig:
        def get(self, key, default=None) -> None:  # noqa: ARG002
            return None

    monkeypatch.setattr(client_mod, "ConfigManager", FakeConfig)
    c = TraceRTMClient()
    with pytest.raises(ValueError):
        c._get_session()


def test_log_operation_rolls_back_on_error(monkeypatch) -> None:  # noqa: ARG001
    class FakeSession:
        def add(self, obj) -> Never:  # noqa: ARG002
            msg = "fail"
            raise RuntimeError(msg)

        def rollback(self) -> None:
            pass

    class FakeDB:
        engine = None

        def connect(self) -> None:
            return None

        def connect(self) -> None:
            return None

        def connect(self) -> None:
            return None

        def connect(self) -> None:
            return None

        def connect(self) -> None:
            return None

    class FakeConfig:
        def get(self, key, default=None) -> str | None:  # noqa: ARG002
            if key == "database_url":
                return "sqlite://"
            if key == "current_project_id":
                return "proj"
            return None

    c = TraceRTMClient(agent_id="agent-1")
    c.config_manager = FakeConfig()
    c._db = cast("Any", FakeDB())
    c._session = cast("Any", FakeSession())

    # Should swallow errors and not raise
    c._log_operation("evt", "item", "i1", {"a": 1})


def test_register_agent_stores_assigned_projects(monkeypatch) -> None:
    stored = {}

    class FakeSession:
        def __init__(self) -> None:
            self.items = []

        def add(self, obj) -> None:
            self.items.append(obj)

        def commit(self) -> None:
            stored["committed"] = True

    class FakeDB:
        engine = None

        def connect(self) -> None:
            return None

    class FakeConfig:
        def get(self, key, default=None) -> str | None:  # noqa: ARG002
            if key == "database_url":
                return "sqlite://"
            if key == "current_project_id":
                return "proj"
            return None

    monkeypatch.setattr(client_mod, "Session", lambda engine: FakeSession())  # noqa: ARG005
    monkeypatch.setattr(client_mod, "DatabaseConnection", lambda url: FakeDB())  # noqa: ARG005

    c = TraceRTMClient(agent_id=None)
    c.config_manager = FakeConfig()
    agent_id = c.register_agent("AgentX", project_ids=["p2", "p3"])

    assert stored.get("committed") is True
    session_items = getattr(c._session, "items", [])
    assert any("assigned_projects" in getattr(a, "agent_metadata", {}) for a in session_items)


def test_update_item_conflict_raises(monkeypatch) -> None:  # noqa: ARG001
    class FakeSession:
        def query(self, model):  # noqa: ARG002
            class _Q:
                def filter(self, *args, **kwargs):  # noqa: ARG002
                    return self

                def first(self) -> Never:
                    raise StaleDataError

            return _Q()

        def commit(self) -> Never:
            raise StaleDataError

        def rollback(self) -> None:
            return None

    c = TraceRTMClient(agent_id="agent")
    c.config_manager = SimpleNamespace(
        get=lambda key, default=None: "proj" if key == "current_project_id" else "sqlite://",  # noqa: ARG005
    )
    c._get_session = FakeSession  # type: ignore[assignment]

    with pytest.raises(ConcurrencyError):
        c.update_item("i1", status="done")
