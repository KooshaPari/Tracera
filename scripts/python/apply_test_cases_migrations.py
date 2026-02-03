#!/usr/bin/env python3
"""Apply 008_add_test_cases and 009_add_test_suites_runs when DB was migrated on a branch that skipped them."""

import os
import pathlib
import sys

# Load .env from repo root (script dir/.. or cwd)
for _dir in (os.path.join(os.path.dirname(__file__), ".."), os.getcwd()):
    env_path = os.path.abspath(os.path.join(_dir, ".env"))
    if pathlib.Path(env_path).is_file():
        with pathlib.Path(env_path).open() as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, _, value = line.partition("=")
                    key = key.strip()
                    value = value.strip().strip("'\"")
                    os.environ.setdefault(key, value)
        break

database_url = os.getenv("TRACERTM_DATABASE_URL") or os.getenv("DATABASE_URL")
if not database_url:
    print("DATABASE_URL or TRACERTM_DATABASE_URL not set", file=sys.stderr)
    sys.exit(1)

# Alembic uses sync driver (database_url is str here after the check above)
if database_url is None:
    sys.exit(1)
if database_url.startswith("postgresql+asyncpg://"):
    database_url = database_url.replace("postgresql+asyncpg://", "postgresql+psycopg2://", 1)
elif database_url.startswith("postgresql://"):
    database_url = database_url.replace("postgresql://", "postgresql+psycopg2://", 1)

from alembic.config import Config
from sqlalchemy import create_engine, text
from sqlalchemy.exc import ProgrammingError

from alembic import command


def run():
    repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    engine = create_engine(database_url, poolclass=None)
    with engine.connect() as conn:
        r = conn.execute(
            text(
                "SELECT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'test_cases')"
            )
        )
        if r.scalar():
            print("test_cases table already exists, skipping 008/009.")
            return

    config = Config(os.path.join(repo_root, "alembic.ini"))
    config.set_main_option("script_location", os.path.join(repo_root, "alembic"))
    config.set_main_option("sqlalchemy.url", database_url or "")

    # DB is at 052 but missing test_cases (migrated on a branch that skipped 008/009).
    # Stamp to 007, run upgrade to 008 only (creates test_cases; 009 may conflict with existing enums), then stamp back to 052.
    print("Stamping to 007_add_problems_and_processes...")
    command.stamp(config, "007_add_problems_and_processes")
    print("Applying 008_add_test_cases (test_cases + test_case_activities)...")
    try:
        command.upgrade(config, "008_add_test_cases")
    except ProgrammingError as e:
        if "already exists" not in str(e).lower():
            raise
        print("(test_cases already present, continuing)")
    print("Stamping back to 052_add_agent_sessions...")
    command.stamp(config, "052_add_agent_sessions")

    # Verify (same URL as script; Alembic uses env DATABASE_URL)
    with create_engine(database_url, poolclass=None).connect() as conn:
        r = conn.execute(
            text(
                "SELECT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'test_cases')"
            )
        )
        if r.scalar():
            print("Done. test_cases (and related) tables created.")
        else:
            print(
                "Done. If the API still reports missing test_cases, ensure DATABASE_URL matches the API .env.",
                file=sys.stderr,
            )


if __name__ == "__main__":
    run()
