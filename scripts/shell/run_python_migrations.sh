#!/usr/bin/env bash
# Run Alembic migrations for the Python backend (test_cases, links, graphs, etc.).
# Requires: DATABASE_URL or TRACERTM_DATABASE_URL set (or in .env).
# Usage: ./scripts/run_python_migrations.sh   # from repo root

set -e
cd "$(dirname "$0")/.."

if [ -f .env ]; then
  set -a
  # shellcheck source=/dev/null
  source .env
  set +a
fi

if [ -z "${DATABASE_URL:-}" ] && [ -z "${TRACERTM_DATABASE_URL:-}" ]; then
  echo "❌ DATABASE_URL or TRACERTM_DATABASE_URL not set. Set it in .env or export it."
  exit 1
fi

echo "Running Python (Alembic) migrations..."
uv run alembic upgrade head
echo "✅ Python migrations applied."
