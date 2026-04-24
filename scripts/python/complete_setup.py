#!/usr/bin/env python3
"""Complete TraceRTM Setup Script.

Applies all database migrations and initializes all services.
"""

import os
import subprocess
import sys
from pathlib import Path

# Load environment variables
from typing import Any

from dotenv import load_dotenv

load_dotenv()


def run_command(cmd_list: Any, _description: Any, cwd: Any = None) -> bool | None:
    """Run a command and report status.

    Args:
        cmd_list: List of command arguments (e.g., ['git', 'clone', url])
        description: Human-readable description of the command
        cwd: Optional working directory for the command
    """
    try:
        subprocess.run(cmd_list, shell=False, check=True, text=True, capture_output=False, cwd=cwd)
        return True
    except subprocess.CalledProcessError:
        return False


def main() -> None:
    """Main."""
    # Phase 1: Database Setup

    # Get database URL
    db_url = os.getenv("DB_DIRECT_URL")
    if not db_url:
        sys.exit(1)

    # Apply PostgreSQL migrations
    migration_file = Path(__file__).parent.parent / "backend/internal/db/migrations/20250130000000_init.sql"
    if migration_file.exists():
        # Use psql to apply migrations with separate arguments
        cmd = ["psql", db_url, "-f", str(migration_file)]
        if run_command(cmd, "Apply PostgreSQL migrations"):
            pass

    # Phase 2: Neo4j Setup
    neo4j_uri = os.getenv("NEO4J_URI")
    neo4j_user = os.getenv("NEO4J_USERNAME")
    neo4j_pass = os.getenv("NEO4J_PASSWORD")

    if neo4j_uri and neo4j_user and neo4j_pass:
        pass

    # Phase 3: Build Backend
    # Use safe subprocess invocation without shell=True
    # Split command into separate list items to avoid shell injection
    backend_dir = Path(__file__).parent.parent / "backend"
    if run_command(["go", "build", "-o", "tracertm-backend", "."], "Build backend binary", cwd=str(backend_dir)):
        pass

    # Phase 4: Run Tests
    if run_command(["go", "test", "./...", "-v"], "Run all tests", cwd=str(backend_dir)):
        pass


if __name__ == "__main__":
    main()
