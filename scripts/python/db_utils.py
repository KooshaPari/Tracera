#!/usr/bin/env python3
"""
Database utility functions for TraceRTM.

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
    except Exception as e:
        print(f"Connection failed: {e}")
        return False


def create_database():
    """Create the database if it doesn't exist."""
    database_url = get_database_url()
    print(f"Database URL: {database_url}")

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
                print(f"Database '{db_name}' already exists.")
            else:
                conn.execute(text(f'CREATE DATABASE "{db_name}"'))
                print(f"Database '{db_name}' created successfully.")

    except Exception as e:
        print(f"Error creating database: {e}")
        return False

    return True


def drop_database():
    """Drop the database (BE CAREFUL!)."""
    database_url = get_database_url()

    # Parse URL to get database name
    from urllib.parse import urlparse

    parsed = urlparse(database_url)
    db_name = parsed.path.lstrip("/")

    # Confirm
    confirm = input(f"Are you sure you want to DROP database '{db_name}'? (yes/no): ")
    if confirm.lower() != "yes":
        print("Aborted.")
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
            print(f"Database '{db_name}' dropped successfully.")

    except Exception as e:
        print(f"Error dropping database: {e}")
        return False

    return True


def reset_database():
    """Reset database - drop and recreate."""
    print("Resetting database...")
    if drop_database() and create_database():
        print("Database reset complete. Run migrations with: alembic upgrade head")
        return True
    return False


def show_stats():
    """Show database statistics."""
    engine = create_engine(get_database_url())

    with Session(engine) as session:
        from tracertm.models.agent import Agent
        from tracertm.models.project import Project

        print("\n=== TraceRTM Database Statistics ===\n")

        # Projects
        project_count = session.query(Project).count()
        print(f"Projects: {project_count}")

        if project_count > 0:
            # Items by view
            print("\nItems by view:")
            result = session.execute(
                text("""
                SELECT view, COUNT(*) as count
                FROM items
                WHERE deleted_at IS NULL
                GROUP BY view
                ORDER BY count DESC
            """)
            )
            for row in result:
                print(f"  {row.view}: {row.count}")

            # Items by status
            print("\nItems by status:")
            result = session.execute(
                text("""
                SELECT status, COUNT(*) as count
                FROM items
                WHERE deleted_at IS NULL
                GROUP BY status
                ORDER BY count DESC
            """)
            )
            for row in result:
                print(f"  {row.status}: {row.count}")

            # Links by type
            print("\nLinks by type:")
            result = session.execute(
                text("""
                SELECT link_type, COUNT(*) as count
                FROM links
                GROUP BY link_type
                ORDER BY count DESC
            """)
            )
            for row in result:
                print(f"  {row.link_type}: {row.count}")

            # Agents
            agent_count = session.query(Agent).count()
            print(f"\nAgents: {agent_count}")

            # Recent agent events
            print("\nRecent agent events (last 5):")
            result = session.execute(
                text("""
                SELECT a.name, ae.event_type, ae.created_at
                FROM agent_events ae
                JOIN agents a ON ae.agent_id = a.id
                ORDER BY ae.created_at DESC
                LIMIT 5
            """)
            )
            for row in result:
                print(f"  {row.created_at}: {row.name} - {row.event_type}")

        print("\n")


def vacuum_analyze():
    """Run VACUUM ANALYZE to optimize database."""
    engine = create_engine(get_database_url(), isolation_level="AUTOCOMMIT")

    print("Running VACUUM ANALYZE...")
    try:
        with engine.connect() as conn:
            conn.execute(text("VACUUM ANALYZE"))
        print("VACUUM ANALYZE completed successfully.")
    except Exception as e:
        print(f"Error running VACUUM ANALYZE: {e}")


def list_extensions():
    """List installed PostgreSQL extensions."""
    engine = create_engine(get_database_url())

    with engine.connect() as conn:
        print("\n=== Installed PostgreSQL Extensions ===\n")
        result = conn.execute(
            text("""
            SELECT extname, extversion
            FROM pg_extension
            ORDER BY extname
        """)
        )
        for row in result:
            print(f"{row.extname}: {row.extversion}")
        print("\n")


def main():
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
            print("Database connection: OK")
        else:
            print("Database connection: FAILED")
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
