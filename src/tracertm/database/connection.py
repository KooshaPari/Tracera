"""Database connection module for TracerTM."""

from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from tracertm.models.base import Base


class DatabaseConnection:
    """Simple database connection manager."""

    _engine = None
    _session_factory = None
