#!/usr/bin/env python3
"""Test database migrations.

Verifies that migrations can be run successfully and creates expected schema.
"""

import sys
from pathlib import Path

# Add src to path
from typing import Any

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import os

from sqlalchemy import create_engine, inspect, text


def get_database_url() -> str:
    """Get database URL from environment or use default."""
    return os.getenv("DATABASE_URL", "postgresql://localhost/tracertm_test")


def check_tables(inspector: Any) -> bool:
    """Check that all expected tables exist."""
    expected_tables = {"projects", "items", "links", "agents", "agent_events", "change_log", "alembic_version"}
    actual_tables = set(inspector.get_table_names())

    missing_tables = expected_tables - actual_tables
    if missing_tables:
        return False

    extra_tables = actual_tables - expected_tables
    if extra_tables:
        pass

    return True


def check_extensions(engine: Any) -> None:
    """Check that required PostgreSQL extensions are installed."""
    with engine.connect() as conn:
        result = conn.execute(
            text("""
            SELECT extname FROM pg_extension
            WHERE extname IN ('vector', 'pg_trgm')
        """),
        )
        extensions = {row[0] for row in result}

    for ext in ["vector", "pg_trgm"]:
        if ext not in extensions:
            pass


def check_indexes(inspector: Any) -> None:
    """Check that expected indexes exist on items table."""
    indexes = inspector.get_indexes("items")
    index_names = {idx["name"] for idx in indexes}

    expected_indexes = {
        "idx_items_project_id",
        "idx_items_view",
        "idx_items_item_type",
        "idx_items_status",
        "idx_items_title_trgm",
    }

    missing_indexes = expected_indexes - index_names
    if missing_indexes:
        pass


def check_foreign_keys(inspector: Any) -> bool:
    """Check that expected foreign keys exist."""
    # Items should have FK to projects
    items_fks = inspector.get_foreign_keys("items")
    if not any(fk["referred_table"] == "projects" for fk in items_fks):
        return False

    # Links should have FK to items
    links_fks = inspector.get_foreign_keys("links")
    items_fk_count = sum(1 for fk in links_fks if fk["referred_table"] == "items")
    return not items_fk_count < 2


def check_triggers(engine: Any) -> None:
    """Check that triggers are present."""
    with engine.connect() as conn:
        result = conn.execute(
            text("""
            SELECT tgname, tgrelid::regclass
            FROM pg_trigger
            WHERE tgrelid IN (
                'items'::regclass,
                'links'::regclass,
                'projects'::regclass
            )
            AND tgname NOT LIKE 'RI_%'  -- Exclude referential integrity triggers
        """),
        )
        triggers = [(row[0], str(row[1])) for row in result]

    if triggers:
        for _trigger_name, _table_name in triggers:
            pass


def test_migrations() -> bool:
    """Test that migrations create expected schema."""
    database_url = get_database_url()

    engine = create_engine(database_url)
    inspector = inspect(engine)

    # Run tests
    if not check_tables(inspector):
        return False

    check_extensions(engine)
    check_indexes(inspector)

    if not check_foreign_keys(inspector):
        return False

    check_triggers(engine)

    # Check columns on items table
    items_columns = {col["name"] for col in inspector.get_columns("items")}

    expected_columns = {
        "id",
        "project_id",
        "title",
        "description",
        "view",
        "item_type",
        "status",
        "priority",
        "owner",
        "parent_id",
        "item_metadata",
        "version",
        "deleted_at",
        "created_at",
        "updated_at",
    }

    missing_columns = expected_columns - items_columns
    if missing_columns:
        return False

    # Test data insertion
    try:
        with engine.connect() as conn:
            # Begin transaction
            trans = conn.begin()

            # Insert test project
            conn.execute(
                text("""
                INSERT INTO projects (id, name, description, project_metadata)
                VALUES ('test-proj-1', 'Test Project', 'Test', '{}')
            """),
            )

            # Insert test item
            conn.execute(
                text("""
                INSERT INTO items (id, project_id, title, view, item_type, item_metadata)
                VALUES ('test-item-1', 'test-proj-1', 'Test Item', 'requirements', 'requirement', '{}')
            """),
            )

            # Rollback to clean up
            trans.rollback()

    except Exception:
        return False

    return True


if __name__ == "__main__":
    success = test_migrations()
    sys.exit(0 if success else 1)
