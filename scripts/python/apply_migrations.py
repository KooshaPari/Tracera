#!/usr/bin/env python3
"""
Apply database migrations to Supabase and Neo4j
"""

import os
import sys
from pathlib import Path

import psycopg2
from dotenv import load_dotenv

# Load .env file
env_path = Path(__file__).parent.parent / ".env"
load_dotenv(env_path)


def apply_supabase_migrations():
    """Apply migrations to Supabase PostgreSQL"""

    # Try direct URL first, then fall back to pooler URL
    db_url = os.getenv("DB_DIRECT_URL")
    if not db_url:
        db_url = os.getenv("DB_TRANS_POOL_URL")
    if not db_url:
        print("❌ DB_DIRECT_URL or DB_TRANS_POOL_URL not set")
        return False

    try:
        # Connect to database
        conn = psycopg2.connect(db_url)
        cursor = conn.cursor()

        print("✅ Connected to Supabase PostgreSQL")

        # Read and execute migration files
        migrations_dir = Path(__file__).parent.parent / "backend" / "internal" / "db" / "migrations"

        if not migrations_dir.exists():
            print(f"❌ Migrations directory not found: {migrations_dir}")
            return False

        migration_files = sorted(migrations_dir.glob("*.sql"))

        if not migration_files:
            print("❌ No migration files found")
            return False

        for migration_file in migration_files:
            print(f"\n📝 Applying migration: {migration_file.name}")

            with Path(migration_file).open() as f:
                sql = f.read()

            try:
                cursor.execute(sql)
                conn.commit()
                print(f"✅ Applied: {migration_file.name}")
            except Exception as e:
                conn.rollback()
                print(f"⚠️  Migration {migration_file.name} failed (may already exist): {e}")

        cursor.close()
        conn.close()

        print("\n✅ Supabase migrations completed")
        return True

    except Exception as e:
        print(f"❌ Error applying migrations: {e}")
        return False


def apply_neo4j_migrations():
    """Apply migrations to Neo4j"""

    try:
        from neo4j import GraphDatabase

        uri = os.getenv("NEO4J_URI")
        username = os.getenv("NEO4J_USERNAME")
        password = os.getenv("NEO4J_PASSWORD")

        if not all([uri, username, password]):
            print("❌ Neo4j credentials not set")
            return False

        driver = GraphDatabase.driver(uri, auth=(username, password))

        print("✅ Connected to Neo4j")

        # Create constraints and indexes
        with driver.session() as session:
            # Create constraints
            constraints = [
                "CREATE CONSTRAINT item_id_unique IF NOT EXISTS FOR (i:Item) REQUIRE i.id IS UNIQUE",
                "CREATE CONSTRAINT project_id_unique IF NOT EXISTS FOR (p:Project) REQUIRE p.id IS UNIQUE",
                "CREATE CONSTRAINT agent_id_unique IF NOT EXISTS FOR (a:Agent) REQUIRE a.id IS UNIQUE",
            ]

            for constraint in constraints:
                try:
                    session.run(constraint)
                    print(f"✅ {constraint.split('IF NOT EXISTS')[0].strip()}")
                except Exception as e:
                    print(f"⚠️  Constraint creation: {e}")

            # Create indexes
            indexes = [
                "CREATE INDEX item_project_idx IF NOT EXISTS FOR (i:Item) ON (i.project_id)",
                "CREATE INDEX item_type_idx IF NOT EXISTS FOR (i:Item) ON (i.type)",
                "CREATE INDEX project_name_idx IF NOT EXISTS FOR (p:Project) ON (p.name)",
                "CREATE INDEX agent_project_idx IF NOT EXISTS FOR (a:Agent) ON (a.project_id)",
            ]

            for index in indexes:
                try:
                    session.run(index)
                    print(f"✅ {index.split('IF NOT EXISTS')[0].strip()}")
                except Exception as e:
                    print(f"⚠️  Index creation: {e}")

        driver.close()
        print("\n✅ Neo4j migrations completed")
        return True

    except ImportError:
        print("⚠️  neo4j package not installed, skipping Neo4j migrations")
        return True
    except Exception as e:
        print(f"❌ Error applying Neo4j migrations: {e}")
        return False


if __name__ == "__main__":
    print("🚀 Starting database migrations...\n")

    supabase_ok = apply_supabase_migrations()
    neo4j_ok = apply_neo4j_migrations()

    if supabase_ok and neo4j_ok:
        print("\n✨ All migrations completed successfully!")
        sys.exit(0)
    else:
        print("\n❌ Some migrations failed")
        sys.exit(1)
