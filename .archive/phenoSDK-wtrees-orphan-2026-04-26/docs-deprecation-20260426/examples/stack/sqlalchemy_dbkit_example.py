"""SQLAlchemy + db-kit integration example.

- Uses SQLAlchemy for ORM (SQLite for simplicity)
- Shows how you might also use db-kit for async Postgres operations in the same service

Dependencies (optional example):
  pip install sqlalchemy aiosqlite asyncpg
"""

from __future__ import annotations

# SQLAlchemy imports
try:
    from sqlalchemy import Column, Integer, String, create_engine
    from sqlalchemy.orm import Session, declarative_base
except Exception:  # pragma: no cover
    create_engine = None  # type: ignore
    declarative_base = lambda: None  # type: ignore
    Session = None  # type: ignore

# db-kit imports (optional, used for async Postgres section)
try:
    from pheno.database.adapters.postgres import PostgreSQLAdapter
    from pheno.database.core.engine import Database
except Exception:  # pragma: no cover
    PostgreSQLAdapter = None  # type: ignore
    Database = None  # type: ignore


def main_sqlalchemy_sqlite():
    if create_engine is None:
        print("SQLAlchemy not installed. pip install sqlalchemy")
        return

    Base = declarative_base()

    class User(Base):  # type: ignore
        __tablename__ = "users"
        id = Column(Integer, primary_key=True)
        name = Column(String(100), nullable=False)

    # In-memory SQLite for demo
    engine = create_engine("sqlite+pysqlite:///:memory:", echo=False)
    Base.metadata.create_all(engine)

    # Insert and query using ORM
    with Session(engine) as session:
        session.add_all([User(name="alice"), User(name="bob")])
        session.commit()
        users = session.query(User).all()
        print("Users via SQLAlchemy ORM:", [u.name for u in users])


async def main_dbkit_postgres():
    if PostgreSQLAdapter is None:
        print("db-kit not importable; ensure the package is installed in this environment.")
        return
    # Example DSN: set POSTGRES_USER/POSTGRES_PASSWORD for convenience
    adapter = PostgreSQLAdapter(host="localhost", port=5432, database="postgres")
    db = Database(adapter)
    rows = await adapter.query("pg_catalog.pg_tables", select="schemaname, tablename", limit=5)
    print("Sample tables via db-kit:", rows)
    await adapter.close()


if __name__ == "__main__":  # pragma: no cover
    main_sqlalchemy_sqlite()
    # For async example, run in an event loop if desired
    # import asyncio; asyncio.run(main_dbkit_postgres())
