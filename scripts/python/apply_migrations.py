#!/usr/bin/env python3
"""Apply database migrations to Supabase and Neo4j."""

import contextlib
import os
import sys
from pathlib import Path

import psycopg2
from dotenv import load_dotenv

# Load .env file
env_path = Path(__file__).parent.parent / ".env"
load_dotenv(env_path)


def apply_supabase_migrations() -> bool | None:
    """Apply migrations to Supabase PostgreSQL."""
    # Try direct URL first, then fall back to pooler URL
    db_url = os.getenv("DB_DIRECT_URL")
    if not db_url:
        db_url = os.getenv("DB_TRANS_POOL_URL")
    if not db_url:
        return False

    try:
        # Connect to database
        conn = psycopg2.connect(db_url)
        cursor = conn.cursor()

        # Read and execute migration files
        migrations_dir = Path(__file__).parent.parent / "backend" / "internal" / "db" / "migrations"

        if not migrations_dir.exists():
            return False

        migration_files = sorted(migrations_dir.glob("*.sql"))

        if not migration_files:
            return False

        for migration_file in migration_files:
            sql = Path(migration_file).read_text(encoding="utf-8")

            try:
                cursor.execute(sql)
                conn.commit()
            except Exception:
                conn.rollback()

        cursor.close()
        conn.close()

        return True

    except Exception:
        return False


def apply_neo4j_migrations() -> bool | None:
    """Apply migrations to Neo4j."""
    try:
        from neo4j import GraphDatabase

        uri = os.getenv("NEO4J_URI")
        username = os.getenv("NEO4J_USERNAME")
        password = os.getenv("NEO4J_PASSWORD")

        if not all([uri, username, password]):
            return False

        driver = GraphDatabase.driver(uri, auth=(username, password))

        # Create constraints and indexes
        with driver.session() as session:
            # Create constraints
            constraints = [
                "CREATE CONSTRAINT item_id_unique IF NOT EXISTS FOR (i:Item) REQUIRE i.id IS UNIQUE",
                "CREATE CONSTRAINT project_id_unique IF NOT EXISTS FOR (p:Project) REQUIRE p.id IS UNIQUE",
                "CREATE CONSTRAINT agent_id_unique IF NOT EXISTS FOR (a:Agent) REQUIRE a.id IS UNIQUE",
            ]

            for constraint in constraints:
                with contextlib.suppress(Exception):
                    session.run(constraint)

            # Create indexes
            indexes = [
                "CREATE INDEX item_project_idx IF NOT EXISTS FOR (i:Item) ON (i.project_id)",
                "CREATE INDEX item_type_idx IF NOT EXISTS FOR (i:Item) ON (i.type)",
                "CREATE INDEX project_name_idx IF NOT EXISTS FOR (p:Project) ON (p.name)",
                "CREATE INDEX agent_project_idx IF NOT EXISTS FOR (a:Agent) ON (a.project_id)",
            ]

            for index in indexes:
                with contextlib.suppress(Exception):
                    session.run(index)

        driver.close()
        return True

    except ImportError:
        return True
    except Exception:
        return False


if __name__ == "__main__":
    supabase_ok = apply_supabase_migrations()
    neo4j_ok = apply_neo4j_migrations()

    if supabase_ok and neo4j_ok:
        sys.exit(0)
    else:
        sys.exit(1)
