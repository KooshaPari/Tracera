#!/usr/bin/env bash
# Start postgres only if not already running (avoids "postmaster.pid already exists"
# when postgres was started by brew or a previous process-compose run).

set -e
PGPORT="${PGPORT:-5432}"

if command -v lsof >/dev/null 2>&1; then
  if lsof -Pi :"$PGPORT" -sTCP:LISTEN -t >/dev/null 2>&1; then
    echo "PostgreSQL already running on port $PGPORT; holding process for process-compose."
    exec sh -c 'while true; do sleep 3600; done'
  fi
fi

exec postgres -D /opt/homebrew/var/postgresql@17
