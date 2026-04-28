import time
from typing import Any, Never

import pytest
from sqlalchemy.orm.exc import StaleDataError

from tests.test_constants import COUNT_THREE, COUNT_TWO
from tracertm.services.concurrent_operations_service import (
    ConcurrencyError,
    ConcurrentOperationsService,
    retry_with_backoff,
)


def test_retry_with_backoff_retries_then_raises(monkeypatch: Any) -> None:
    calls = {"count": 0}

    def op() -> Never:
        calls["count"] += 1
        raise StaleDataError

    # avoid real sleep
    monkeypatch.setattr(time, "sleep", lambda _x: None)
    wrapped = retry_with_backoff(max_retries=2, initial_delay=0.01, jitter=False)(op)

    with pytest.raises(ConcurrencyError):
        wrapped()
    assert calls["count"] == COUNT_THREE  # initial + 2 retries


def test_execute_with_retry_success_after_conflict(monkeypatch: Any) -> None:
    calls = {"count": 0}

    def op() -> str:
        calls["count"] += 1
        if calls["count"] == 1:
            raise StaleDataError
        return "ok"

    monkeypatch.setattr(time, "sleep", lambda _x: None)
    svc = ConcurrentOperationsService(session=None)
    result = svc.execute_with_retry(op, max_retries=2, initial_delay=0.01)

    assert result == "ok"
    assert calls["count"] == COUNT_TWO


def test_execute_with_retry_exhausts_and_raises(monkeypatch: Any) -> None:
    monkeypatch.setattr(time, "sleep", lambda _x: None)
    svc = ConcurrentOperationsService(session=None)

    with pytest.raises(ConcurrencyError):
        svc.execute_with_retry(lambda: (_ for _ in ()).throw(StaleDataError()), max_retries=1, initial_delay=0.0)


def test_execute_in_transaction_rolls_back_on_error(_monkeypatch: Any) -> None:
    class DummySession:
        def __init__(self) -> None:
            self.committed = False
            self.rolled = False

        def commit(self) -> None:
            self.committed = True

        def rollback(self) -> None:
            self.rolled = True

    session = DummySession()
    svc = ConcurrentOperationsService(session)

    def ok() -> int:
        return 1

    def boom() -> Never:
        msg = "fail"
        raise RuntimeError(msg)

    with pytest.raises(RuntimeError):
        svc.execute_in_transaction([ok, boom])

    assert session.rolled is True
    assert session.committed is False
