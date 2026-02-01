#!/usr/bin/env bash
# Start temporal server only if not already running (avoids "addr already in use"
# when temporal was started by brew or a previous process-compose run).

set -e
TEMPORAL_PORT="${TEMPORAL_PORT:-7233}"

if command -v lsof >/dev/null 2>&1; then
  if lsof -Pi :"$TEMPORAL_PORT" -sTCP:LISTEN -t >/dev/null 2>&1; then
    echo "Temporal already running on port $TEMPORAL_PORT; holding process for process-compose."
    exec sh -c 'while true; do sleep 3600; done'
  fi
fi

exec temporal server start-dev --db-filename .temporal/temporal.db
