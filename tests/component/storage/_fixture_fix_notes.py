# File with fixed mock_db_connection fixture
# Copy this to test_storage_comprehensive.py to replace the broken fixture

from typing import Any

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from tracertm.models.base import Base


@pytest.fixture
def mock_db_connection(temp_dir: Any) -> None:
    """Create mock database connection with SQLite - FIXED VERSION."""
    db_path = temp_dir / "test.db"
    engine = create_engine(f"sqlite:///{db_path}", echo=False)
    Base.metadata.create_all(engine)

    # Create a proper mock with engine attribute
    class MockConnection:
        def __init__(self, engine: Any) -> None:
            self.engine = engine

        def execute(self, *args: Any, **kwargs: Any) -> None:
            """Execute SQL with proper text() wrapping for SQLAlchemy 2.0."""
            from sqlalchemy import text as sql_text

            with self.engine.connect() as conn:
                # Wrap string SQL in text() if needed
                if args and isinstance(args[0], str):
                    result = conn.execute(sql_text(args[0]), *args[1:], **kwargs)
                    conn.commit()
                    return result
                result = conn.execute(*args, **kwargs)
                conn.commit()
                return result

        def get_session(self) -> None:
            SessionLocal = sessionmaker(bind=self.engine)
            return SessionLocal()

    return MockConnection(engine)
