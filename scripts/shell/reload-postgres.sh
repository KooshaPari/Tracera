#!/usr/bin/env bash
# Reload PostgreSQL config without full restart.

set -euo pipefail

PGDATA="${PGDATA:-/opt/homebrew/var/postgresql@17}"

if command -v pg_ctl >/dev/null 2>&1; then
  if [[ -d "$PGDATA" ]]; then
    pg_ctl -D "$PGDATA" reload
    exit 0
  fi
fi

if command -v psql >/dev/null 2>&1; then
  psql -d postgres -c "SELECT pg_reload_conf();"
  exit 0
fi

echo "[postgres] reload failed: pg_ctl or psql not available (PGDATA=$PGDATA)" >&2
exit 1
