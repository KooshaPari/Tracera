#!/usr/bin/env python3
"""
Complete TraceRTM Setup Script
Applies all database migrations and initializes all services
"""

import os
import sys
import subprocess
import time
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def run_command(cmd_list, description, cwd=None):
    """Run a command and report status

    Args:
        cmd_list: List of command arguments (e.g., ['git', 'clone', url])
        description: Human-readable description of the command
        cwd: Optional working directory for the command
    """
    print(f"\n{'='*60}")
    print(f"▶ {description}")
    print(f"{'='*60}")
    try:
        result = subprocess.run(cmd_list, shell=False, check=True, text=True, capture_output=False, cwd=cwd)
        print(f"✅ {description} - SUCCESS")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} - FAILED")
        print(f"Error: {e}")
        return False

def main():
    print("\n" + "="*60)
    print("🚀 TraceRTM Complete Setup")
    print("="*60)
    
    # Phase 1: Database Setup
    print("\n📦 PHASE 1: Database Setup")
    
    # Get database URL
    db_url = os.getenv("DB_DIRECT_URL")
    if not db_url:
        print("❌ DB_DIRECT_URL not found in .env")
        sys.exit(1)
    
    # Apply PostgreSQL migrations
    migration_file = Path(__file__).parent.parent / "backend/internal/db/migrations/20250130000000_init.sql"
    if migration_file.exists():
        print(f"\n📝 Applying PostgreSQL migrations from {migration_file}")
        with open(migration_file, 'r') as f:
            sql_content = f.read()

        # Use psql to apply migrations with separate arguments
        cmd = ["psql", db_url, "-f", str(migration_file)]
        if run_command(cmd, "Apply PostgreSQL migrations"):
            print("✅ PostgreSQL migrations applied successfully")
        else:
            print("⚠️  PostgreSQL migrations may have failed - check manually")

    # Phase 2: Neo4j Setup
    print("\n📦 PHASE 2: Neo4j Setup")
    neo4j_uri = os.getenv("NEO4J_URI")
    neo4j_user = os.getenv("NEO4J_USERNAME")
    neo4j_pass = os.getenv("NEO4J_PASSWORD")

    if neo4j_uri and neo4j_user and neo4j_pass:
        print(f"Neo4j URI: {neo4j_uri}")
        print("⚠️  Neo4j setup requires manual execution in Neo4j Browser")
        print("See DATABASE_SETUP_INSTRUCTIONS.md for Cypher commands")

    # Phase 3: Build Backend
    print("\n📦 PHASE 3: Build Backend")
    # Use safe subprocess invocation without shell=True
    # Split command into separate list items to avoid shell injection
    backend_dir = Path(__file__).parent.parent / "backend"
    if run_command(["go", "build", "-o", "tracertm-backend", "."], "Build backend binary", cwd=str(backend_dir)):
        print("✅ Backend built successfully")

    # Phase 4: Run Tests
    print("\n📦 PHASE 4: Run Tests")
    if run_command(["go", "test", "./...", "-v"], "Run all tests", cwd=str(backend_dir)):
        print("✅ All tests passed")
    
    print("\n" + "="*60)
    print("✅ Setup Complete!")
    print("="*60)
    print("\nNext steps:")
    print("1. Setup Neo4j schema (see DATABASE_SETUP_INSTRUCTIONS.md)")
    print("2. Run backend: cd backend && ./tracertm-backend")
    print("3. Test endpoints: curl http://localhost:8080/health")

if __name__ == "__main__":
    main()

