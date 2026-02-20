"""Custom SQLAlchemy types for TraceRTM."""

from typing import Any

from sqlalchemy import JSON
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.engine.interfaces import Dialect
from sqlalchemy.types import TypeDecorator, TypeEngine


class JSONType(TypeDecorator[dict[str, object]]):
    """JSON type that uses JSONB for PostgreSQL and JSON for other databases.

    This allows us to use SQLite for testing while using JSONB in production.
    """

    impl = JSON
    cache_ok = True

    def load_dialect_impl(self, dialect: Dialect) -> TypeEngine[Any]:
        """Load the appropriate type for the dialect."""
        if dialect.name == "postgresql":
            return dialect.type_descriptor(JSONB())
        return dialect.type_descriptor(JSON())
