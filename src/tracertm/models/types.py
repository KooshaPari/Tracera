"""Custom SQLAlchemy types for TracerTM."""

from sqlalchemy import JSON
from sqlalchemy.types import TypeDecorator


class JSONType(TypeDecorator):
    """Platform-independent JSON type.

    Uses PostgreSQL JSON type when available, falls back to JSON TEXT.
    """

    impl = JSON
    cache_ok = True

    def load_dialect_impl(self, dialect):  # noqa: ANN001, ANN201, D102
        return dialect.type_descriptor(JSON())
