#!/usr/bin/env python3
"""Database utilities for development.

Provides helper functions for database operations, migrations,
and data management during development.
"""

import os
import subprocess
from pathlib import Path
from typing import Any

import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT


def get_db_config() -> dict[str, Any]:
    """Get database configuration from environment."""
    db_url = os.getenv("DATABASE_URL", "postgresql://tracertm:password@localhost:5432/tracertm")

    # Parse database URL
    # Format: postgresql://user:password@host:port/dbname
    parts = db_url.replace("postgresql://", "").replace("postgresql+asyncpg://", "")
    user_pass, host_port_db = parts.split("@")
    user, password = user_pass.split(":")
    host_port, dbname = host_port_db.split("/")

    if ":" in host_port:
        host, port = host_port.split(":")
    else:
        host = host_port
        port = "5432"

    return {
        "host": host,
        "port": int(port),
        "user": user,
        "password": password,
        "dbname": dbname,
    }


def get_connection(autocommit: bool = False) -> None:
    """Get database connection."""
    config = get_db_config()
    conn = psycopg2.connect(
        host=config["host"],
        port=config["port"],
        user=config["user"],
        password=config["password"],
        dbname=config["dbname"],
    )

    if autocommit:
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)

    return conn


def execute_sql_file(filepath: Path) -> bool:
    """Execute SQL file."""
    try:
        sql = Path(filepath).read_text(encoding="utf-8")

        conn = get_connection(autocommit=True)
        cursor = conn.cursor()
        cursor.execute(sql)
        cursor.close()
        conn.close()
        return True
    except Exception:
        return False


def table_exists(table_name: str) -> bool:
    """Check if table exists."""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = %s)", (table_name,))
        exists = cursor.fetchone()[0]
        cursor.close()
        conn.close()
        return exists
    except Exception:
        return False


def get_table_count(table_name: str) -> int | None:
    """Get row count for a table."""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
        count = cursor.fetchone()[0]
        cursor.close()
        conn.close()
        return count
    except Exception:
        return None


def truncate_table(table_name: str, cascade: bool = False) -> bool:
    """Truncate a table."""
    try:
        conn = get_connection(autocommit=True)
        cursor = conn.cursor()
        if cascade:
            cursor.execute(f"TRUNCATE TABLE {table_name} CASCADE")
        else:
            cursor.execute(f"TRUNCATE TABLE {table_name}")
        cursor.close()
        conn.close()
        return True
    except Exception:
        return False


def run_migrations(direction: str = "up") -> bool:
    """Run database migrations using Alembic."""
    try:
        backend_dir = Path(__file__).parent.parent.parent / "backend"

        if direction == "up":
            result = subprocess.run(["alembic", "upgrade", "head"], cwd=backend_dir, capture_output=True, text=True)
        elif direction == "down":
            result = subprocess.run(["alembic", "downgrade", "-1"], cwd=backend_dir, capture_output=True, text=True)
        else:
            return False

        return result.returncode == 0

    except Exception:
        return False


def get_migration_status() -> str | None:
    """Get current migration status."""
    try:
        backend_dir = Path(__file__).parent.parent.parent / "backend"
        result = subprocess.run(["alembic", "current"], cwd=backend_dir, capture_output=True, text=True)

        if result.returncode == 0:
            return result.stdout.strip()
        return None

    except Exception:
        return None


def backup_database(backup_dir: Path | None = None) -> Path | None:
    """Create database backup using pg_dump."""
    try:
        if backup_dir is None:
            backup_dir = Path(__file__).parent.parent.parent / "backups"

        backup_dir.mkdir(exist_ok=True)

        config = get_db_config()
        timestamp = __import__("datetime").datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file = backup_dir / f"tracertm_backup_{timestamp}.sql"

        # Set PGPASSWORD environment variable
        env = os.environ.copy()
        env["PGPASSWORD"] = config["password"]

        result = subprocess.run(
            [
                "pg_dump",
                "-h",
                config["host"],
                "-p",
                str(config["port"]),
                "-U",
                config["user"],
                "-d",
                config["dbname"],
                "-f",
                str(backup_file),
            ],
            env=env,
            capture_output=True,
            text=True,
        )

        if result.returncode == 0:
            return backup_file
        return None

    except Exception:
        return None


def restore_database(backup_file: Path) -> bool:
    """Restore database from backup."""
    try:
        config = get_db_config()

        # Set PGPASSWORD environment variable
        env = os.environ.copy()
        env["PGPASSWORD"] = config["password"]

        result = subprocess.run(
            [
                "psql",
                "-h",
                config["host"],
                "-p",
                str(config["port"]),
                "-U",
                config["user"],
                "-d",
                config["dbname"],
                "-f",
                str(backup_file),
            ],
            env=env,
            capture_output=True,
            text=True,
        )

        return result.returncode == 0

    except Exception:
        return False
