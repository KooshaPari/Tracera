"""Database connection module for TracerTM."""


class DatabaseConnection:
    """Simple database connection manager."""

    _engine = None
    _session_factory = None
