"""
Database access ports that describe how the SDK talks to SQL engines and Redis-style
stores.

These contracts provide a stable surface for adapters that wrap PostgreSQL/asyncpg,
Redis, or compatible systems while allowing the domain layer to remain implementation
agnostic.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from typing import TYPE_CHECKING, Any, AsyncContextManager, Protocol

if TYPE_CHECKING:
    from collections.abc import AsyncIterator, Mapping, Sequence


class IsolationLevel(StrEnum):
    """Supported transaction isolation levels for SQL databases."""

    READ_UNCOMMITTED = "read_uncommitted"
    READ_COMMITTED = "read_committed"
    REPEATABLE_READ = "repeatable_read"
    SERIALIZABLE = "serializable"


@dataclass(slots=True)
class Query:
    """Container for SQL statements with optional positional or named parameters."""

    text: str
    params: Sequence[Any] | Mapping[str, Any] | None = None


@dataclass(slots=True)
class ExecutionResult:
    """Normalized execution result returned by SQL adapters."""

    rowcount: int
    rows: list[Mapping[str, Any]] | None = None
    last_insert_id: Any | None = None
    metadata: dict[str, Any] | None = None


class SQLTransactionPort(Protocol):
    """Transactional context for SQL operations."""

    async def execute(self, query: Query) -> ExecutionResult:
        """Execute a data-modifying statement within this transaction."""
        ...

    async def fetch_one(self, query: Query) -> Mapping[str, Any] | None:
        """Return the first row for the SELECT query or ``None``."""
        ...

    async def fetch_all(self, query: Query) -> list[Mapping[str, Any]]:
        """Return all rows for the SELECT query."""
        ...

    async def commit(self) -> None:
        """Commit the transaction."""
        ...

    async def rollback(self) -> None:
        """Roll back the transaction."""
        ...


class SQLDatabasePort(Protocol):
    """Primary interface for interacting with PostgreSQL or compatible SQL engines."""

    async def execute(self, query: Query) -> ExecutionResult:
        """Run a data definition or manipulation statement and return metadata."""
        ...

    async def fetch_one(self, query: Query) -> Mapping[str, Any] | None:
        """Fetch a single row from the database."""
        ...

    async def fetch_all(self, query: Query) -> list[Mapping[str, Any]]:
        """Fetch all rows produced by the query."""
        ...

    async def stream(
        self,
        query: Query,
        *,
        chunk_size: int = 500,
    ) -> AsyncIterator[Mapping[str, Any]]:
        """Stream result rows in configurable batches."""
        ...

    def transaction(
        self,
        *,
        isolation_level: IsolationLevel = IsolationLevel.READ_COMMITTED,
        readonly: bool = False,
        timeout: float | None = None,
    ) -> AsyncContextManager[SQLTransactionPort]:
        """Return an async context manager that yields a transactional handle."""
        ...

    async def ping(self) -> bool:
        """Perform a lightweight health check against the database."""
        ...

    @property
    def dsn(self) -> str | None:
        """Optional connection string used by the adapter."""
        ...


@dataclass(slots=True)
class LockTicket:
    """Represents an acquired distributed lock."""

    key: str
    token: str
    ttl: int


class KeyValueStorePort(Protocol):
    """Redis-compatible key/value access supporting caching and coordination."""

    async def get(self, key: str) -> bytes | None:
        """Return raw value for ``key`` or ``None``."""
        ...

    async def set(self, key: str, value: bytes | str, *, ttl: int | None = None) -> bool:
        """Store ``value`` optionally expiring after ``ttl`` seconds."""
        ...

    async def delete(self, *keys: str) -> int:
        """Remove one or more keys and return the number of deletions."""
        ...

    async def expire(self, key: str, ttl: int) -> bool:
        """Update TTL for ``key`` without changing the value."""
        ...

    async def increment(self, key: str, amount: int = 1) -> int:
        """Increment an integer counter by ``amount`` and return the new value."""
        ...

    async def scan(self, pattern: str, *, count: int = 100) -> AsyncIterator[str]:
        """Iterate over keys matching ``pattern``."""
        ...

    async def sorted_add(self, key: str, members: Mapping[str, float]) -> int:
        """Add ``members`` to a sorted set and return the number of changes."""
        ...

    async def sorted_range(
        self,
        key: str,
        *,
        min_score: float = float("-inf"),
        max_score: float = float("inf"),
        limit: int | None = None,
        reverse: bool = False,
    ) -> list[str]:
        """Return sorted set members between score bounds."""
        ...

    async def publish(self, channel: str, payload: bytes | str) -> int:
        """Publish an event to ``channel``; return subscriber count when available."""
        ...

    async def acquire_lock(
        self,
        key: str,
        *,
        ttl: int,
        blocking: bool = True,
        timeout: float | None = None,
    ) -> LockTicket | None:
        """Acquire a distributed lock returning a ticket when successful."""
        ...

    async def release_lock(self, ticket: LockTicket) -> bool:
        """Release a previously acquired distributed lock."""
        ...


__all__ = [
    "ExecutionResult",
    "IsolationLevel",
    "KeyValueStorePort",
    "LockTicket",
    "Query",
    "SQLDatabasePort",
    "SQLTransactionPort",
]
