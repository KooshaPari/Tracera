#!/usr/bin/env python3
"""Database utility functions for TraceRTM.

Common database operations and maintenance tasks.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import os

from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session


def get_database_url() -> str:
    """Get database URL from environment or use default."""
    return os.getenv("DATABASE_URL", "postgresql://localhost/tracertm")


def check_connection() -> bool:
    """Check if database connection is working."""
    try:
        engine = create_engine(get_database_url())
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            return result.scalar() == 1
    except Exception:
        return False


def create_database() -> bool:
    """Create the database if it doesn't exist."""
    database_url = get_database_url()

    # Parse URL to get database name
    from urllib.parse import urlparse

    parsed = urlparse(database_url)
    db_name = parsed.path.lstrip("/")

    # Connect to default postgres database
    default_url = database_url.replace(f"/{db_name}", "/postgres")

    try:
        engine = create_engine(default_url, isolation_level="AUTOCOMMIT")
        with engine.connect() as conn:
            # Check if database exists
            result = conn.execute(text("SELECT 1 FROM pg_database WHERE datname = :db_name"), {"db_name": db_name})
            exists = result.scalar() is not None

            if exists:
                pass
            else:
                conn.execute(text(f'CREATE DATABASE "{db_name}"'))

    except Exception:
        return False

    return True


def drop_database() -> bool:
    """Drop the database (BE CAREFUL!)."""
    database_url = get_database_url()

    # Parse URL to get database name
    from urllib.parse import urlparse

    parsed = urlparse(database_url)
    db_name = parsed.path.lstrip("/")

    # Confirm
    confirm = input(f"Are you sure you want to DROP database '{db_name}'? (yes/no): ")
    if confirm.lower() != "yes":
        return False

    # Connect to default postgres database
    default_url = database_url.replace(f"/{db_name}", "/postgres")

    try:
        engine = create_engine(default_url, isolation_level="AUTOCOMMIT")
        with engine.connect() as conn:
            # Terminate connections
            conn.execute(
                text("""
                SELECT pg_terminate_backend(pg_stat_activity.pid)
                FROM pg_stat_activity
                WHERE pg_stat_activity.datname = :db_name
                AND pid <> pg_backend_pid()
            """),
                {"db_name": db_name},
            )

            # Drop database
            conn.execute(text(f'DROP DATABASE IF EXISTS "{db_name}"'))

    except Exception:
        return False

    return True


def reset_database() -> bool:
    """Reset database - drop and recreate."""
    return bool(drop_database() and create_database())


def show_stats() -> None:
    """Show database statistics."""
    engine = create_engine(get_database_url())

    with Session(engine) as session:
        from tracertm.models.agent import Agent
        from tracertm.models.project import Project

        # Projects
        project_count = session.query(Project).count()

        if project_count > 0:
            # Items by view
            result = session.execute(
                text("""
                SELECT view, COUNT(*) as count
                FROM items
                WHERE deleted_at IS NULL
                GROUP BY view
                ORDER BY count DESC
            """),
            )
            for _row in result:
                pass

            # Items by status
            result = session.execute(
                text("""
                SELECT status, COUNT(*) as count
                FROM items
                WHERE deleted_at IS NULL
                GROUP BY status
                ORDER BY count DESC
            """),
            )
            for _row in result:
                pass

            # Links by type
            result = session.execute(
                text("""
                SELECT link_type, COUNT(*) as count
                FROM links
                GROUP BY link_type
                ORDER BY count DESC
            """),
            )
            for _row in result:
                pass

            # Agents
            session.query(Agent).count()

            # Recent agent events
            result = session.execute(
                text("""
                SELECT a.name, ae.event_type, ae.created_at
                FROM agent_events ae
                JOIN agents a ON ae.agent_id = a.id
                ORDER BY ae.created_at DESC
                LIMIT 5
            """),
            )
            for _row in result:
                pass


def vacuum_analyze() -> None:
    """Run VACUUM ANALYZE to optimize database."""
    engine = create_engine(get_database_url(), isolation_level="AUTOCOMMIT")

    try:
        with engine.connect() as conn:
            conn.execute(text("VACUUM ANALYZE"))
    except Exception:
        pass


def list_extensions() -> None:
    """List installed PostgreSQL extensions."""
    engine = create_engine(get_database_url())

    with engine.connect() as conn:
        result = conn.execute(
            text("""
            SELECT extname, extversion
            FROM pg_extension
            ORDER BY extname
        """),
        )
        for _row in result:
            pass


def main() -> None:
    """Main CLI interface."""
    import argparse

    parser = argparse.ArgumentParser(description="TraceRTM Database Utilities")
    parser.add_argument(
        "command",
        choices=["check", "create", "drop", "reset", "stats", "vacuum", "extensions"],
        help="Command to execute",
    )

    args = parser.parse_args()

    if args.command == "check":
        if check_connection():
            pass
        else:
            sys.exit(1)

    elif args.command == "create":
        create_database()

    elif args.command == "drop":
        drop_database()

    elif args.command == "reset":
        reset_database()

    elif args.command == "stats":
        show_stats()

    elif args.command == "vacuum":
        vacuum_analyze()

    elif args.command == "extensions":
        list_extensions()


if __name__ == "__main__":
    main()
