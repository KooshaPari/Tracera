"""Database connection management for TraceRTM."""

from collections.abc import Generator

from sqlalchemy import Engine, create_engine, text
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import QueuePool

from tracertm.models.base import Base


class DatabaseConnection:
    """Manages database connections with connection pooling.

    Features:
    - Connection pooling (pool_size=20, max_overflow=10)
    - Health checks
    - Automatic schema creation
    """

    def __init__(self, database_url: str) -> None:
        """Initialize database connection.

        Args:
            database_url: PostgreSQL database URL (or sqlite:// for testing)

        Raises:
            ValueError: If database_url is invalid
            ConnectionError: If connection fails
        """
        allowed_prefixes = (
            "postgresql://",
            "postgresql+asyncpg://",
            "sqlite://",
            "sqlite+aiosqlite://",
        )
        if not database_url or not database_url.startswith(allowed_prefixes):
            msg = "Database URL must start with 'postgresql://' or 'sqlite://' (for testing)"
            raise ValueError(msg)

        self.database_url = database_url
        self._engine: Engine | None = None
        self._session_factory: sessionmaker | None = None

    @property
    def engine(self) -> Engine | None:
        """Get the database engine."""
        return self._engine

    def connect(self) -> Engine:
        """Establish database connection with pooling.

        Returns:
            SQLAlchemy engine

        Raises:
            ConnectionError: If connection fails
        """
        try:
            self._engine = create_engine(
                self.database_url,
                poolclass=QueuePool,
                pool_size=20,
                max_overflow=10,
                pool_pre_ping=True,  # Verify connections before using
                echo=False,
            )

            # Test connection
            with self._engine.connect() as conn:
                conn.execute(text("SELECT 1"))

            # Create session factory
            self._session_factory = sessionmaker(
                bind=self._engine,
                autocommit=False,
                autoflush=False,
            )
        except Exception as e:
            msg = (
                f"Failed to connect to database: {e}\n"
                f"Please check:\n"
                f"  1. PostgreSQL is running\n"
                f"  2. Database URL is correct\n"
                f"  3. Database exists and is accessible"
            )
            raise ConnectionError(
                msg,
            ) from e
        else:
            return self._engine

    def create_tables(self) -> None:
        """Create all tables defined in models.

        Raises:
            RuntimeError: If not connected
        """
        if not self._engine:
            msg = "Not connected. Call connect() first."
            raise RuntimeError(msg)

        Base.metadata.create_all(self._engine)

    def drop_tables(self) -> None:
        """Drop all tables (for testing/rollback).

        Raises:
            RuntimeError: If not connected
        """
        if not self._engine:
            msg = "Not connected. Call connect() first."
            raise RuntimeError(msg)

        Base.metadata.drop_all(self._engine)

    def health_check(self) -> dict[str, object]:
        """Check database health and return status.

        Returns:
            Dict with health status information

        Raises:
            RuntimeError: If not connected
        """
        if not self._engine:
            msg = "Not connected. Call connect() first."
            raise RuntimeError(msg)

        try:
            with self._engine.connect() as conn:
                # Check connection (dialect-specific)
                if self._engine.dialect.name == "postgresql":
                    result = conn.execute(text("SELECT version()"))
                    version = result.scalar()

                    # Check tables (PostgreSQL)
                    result = conn.execute(
                        text("SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'public'"),
                    )
                    table_count = result.scalar()
                else:
                    # SQLite
                    result = conn.execute(text("SELECT sqlite_version()"))
                    version = f"SQLite {result.scalar()}"

                    # Check tables (SQLite)
                    result = conn.execute(text("SELECT COUNT(*) FROM sqlite_master WHERE type='table'"))
                    table_count = result.scalar()

                pool = self._engine.pool
                pool_size = getattr(pool, "size", lambda: 0)()
                checked_out = getattr(pool, "checkedout", lambda: 0)()
                return {
                    "status": "connected",
                    "version": version,
                    "tables": table_count,
                    "pool_size": pool_size,
                    "checked_out": checked_out,
                }

        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
            }

    def get_session(self) -> Session:
        """Get a new database session.

        Returns:
            SQLAlchemy session

        Raises:
            RuntimeError: If not connected
        """
        if not self._session_factory:
            msg = "Not connected. Call connect() first."
            raise RuntimeError(msg)

        return self._session_factory()

    def close(self) -> None:
        """Close database connection and dispose of pool."""
        if self._engine:
            self._engine.dispose()
            self._engine = None
            self._session_factory = None


# Global connection instance
_db_connection: DatabaseConnection | None = None


def get_engine(database_url: str) -> Engine:
    """Get or create database engine.

    Args:
        database_url: PostgreSQL database URL

    Returns:
        SQLAlchemy engine
    """
    global _db_connection

    if _db_connection is None:
        _db_connection = DatabaseConnection(database_url)
        _db_connection.connect()

    engine = _db_connection._engine
    if engine is None:
        msg = "Database connection failed: engine is None"
        raise RuntimeError(msg)
    return engine


def get_session(database_url: str) -> Generator[Session, None, None]:
    """Get database session (for dependency injection).

    Args:
        database_url: PostgreSQL database URL

    Yields:
        SQLAlchemy session
    """
    engine = get_engine(database_url)
    session_factory = sessionmaker(bind=engine)
    session = session_factory()

    try:
        yield session
    finally:
        session.close()


def get_db_session(database_url: str) -> Generator[Session, None, None]:
    """Backward-compatible alias for dependency injection."""
    return get_session(database_url)
