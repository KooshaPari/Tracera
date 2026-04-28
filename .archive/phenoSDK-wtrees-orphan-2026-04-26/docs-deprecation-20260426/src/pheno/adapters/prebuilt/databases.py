"""Prebuilt database adapters."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from .base import AdapterOperationError, BasePrebuiltAdapter

if TYPE_CHECKING:
    from collections.abc import Sequence


class PostgreSQLAdapter(BasePrebuiltAdapter):
    """Adapter that manages a ``psycopg`` connection."""

    name = "postgresql"
    category = "database"

    def __init__(self, *, dsn: str | None = None, autocommit: bool = True, **config: Any):
        super().__init__(dsn=dsn, autocommit=autocommit, **config)
        self._connection: Any | None = None

    def connect(self) -> None:
        psycopg = self._require("psycopg", install_hint="psycopg[binary]")

        def _connect() -> Any:
            kwargs = {k: v for k, v in self._config.items() if v is not None}
            dsn = kwargs.pop("dsn", None)
            conn = psycopg.connect(dsn, **kwargs) if dsn else psycopg.connect(**kwargs)
            conn.autocommit = bool(self._config.get("autocommit", True))
            return conn

        self._connection = self._wrap_errors("connect", _connect)
        super().connect()

    def execute(self, query: str, *params: Any) -> None:
        self.ensure_connected()
        cursor = None
        try:
            cursor = self._connection.cursor()
            cursor.execute(query, params or None)
        except Exception as exc:  # pragma: no cover - relies on driver
            raise AdapterOperationError(f"postgres execute failed: {exc}") from exc
        finally:
            if cursor is not None:
                cursor.close()

    def fetchall(self, query: str, *params: Any) -> list[Any]:
        self.ensure_connected()
        cursor = None
        try:
            cursor = self._connection.cursor()
            cursor.execute(query, params or None)
            return list(cursor.fetchall())
        except Exception as exc:  # pragma: no cover - relies on driver
            raise AdapterOperationError(f"postgres fetch failed: {exc}") from exc
        finally:
            if cursor is not None:
                cursor.close()

    def close(self) -> None:
        if self._connection is not None:
            self._connection.close()
            self._connection = None
        super().close()

    def health_check(self) -> bool:
        if self._connection is None:
            return False
        try:
            with self._connection.cursor() as cursor:
                cursor.execute("SELECT 1")
                return bool(cursor.fetchone())
        except Exception:
            return False


class RedisAdapter(BasePrebuiltAdapter):
    """Adapter that exposes a ``redis.Redis`` client."""

    name = "redis"
    category = "database"

    def __init__(self, **config: Any):
        defaults = {"host": "127.0.0.1", "port": 6379, "db": 0}
        defaults.update(config)
        super().__init__(**defaults)
        self._client: Any | None = None

    def connect(self) -> None:
        redis_pkg = self._require("redis")

        def _connect() -> Any:
            return redis_pkg.Redis(**self._config)

        self._client = self._wrap_errors("connect", _connect)
        super().connect()

    def set(self, key: str, value: Any, *, expire: int | None = None) -> None:
        self.ensure_connected()
        self._wrap_errors("set", lambda: self._client.set(name=key, value=value, ex=expire))

    def get(self, key: str) -> Any:
        self.ensure_connected()
        return self._wrap_errors("get", lambda: self._client.get(name=key))

    def close(self) -> None:
        if self._client is not None:
            try:
                self._client.close()
            except AttributeError:  # pragma: no cover - older redis versions
                self._client.connection_pool.disconnect()
            self._client = None
        super().close()

    def health_check(self) -> bool:
        if self._client is None:
            return False
        try:
            return bool(self._client.ping())
        except Exception:
            return False


class SQLiteAdapter(BasePrebuiltAdapter):
    """Adapter for the stdlib ``sqlite3`` module."""

    name = "sqlite"
    category = "database"

    def __init__(self, *, path: str = ":memory:", **config: Any):
        super().__init__(path=path, **config)
        self._connection: Any | None = None

    def connect(self) -> None:
        import sqlite3

        def _connect() -> Any:
            conn = sqlite3.connect(self._config["path"], isolation_level=self._config.get("isolation_level"))
            if self._config.get("row_factory") == "dict":
                conn.row_factory = sqlite3.Row
            return conn

        self._connection = self._wrap_errors("connect", _connect)
        super().connect()

    def execute(self, query: str, params: Sequence[Any] | None = None) -> None:
        self.ensure_connected()
        cursor = self._connection.cursor()
        try:
            cursor.execute(query, params or [])
            self._connection.commit()
        except Exception as exc:  # pragma: no cover
            self._connection.rollback()
            raise AdapterOperationError(f"sqlite execute failed: {exc}") from exc
        finally:
            cursor.close()

    def fetchall(self, query: str, params: Sequence[Any] | None = None) -> list[Any]:
        self.ensure_connected()
        cursor = self._connection.cursor()
        try:
            cursor.execute(query, params or [])
            return list(cursor.fetchall())
        except Exception as exc:  # pragma: no cover
            raise AdapterOperationError(f"sqlite fetch failed: {exc}") from exc
        finally:
            cursor.close()

    def close(self) -> None:
        if self._connection is not None:
            self._connection.close()
            self._connection = None
        super().close()

    def health_check(self) -> bool:
        return self._connection is not None


__all__ = [
    "PostgreSQLAdapter",
    "RedisAdapter",
    "SQLiteAdapter",
]
