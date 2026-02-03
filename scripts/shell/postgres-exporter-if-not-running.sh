#!/usr/bin/env bash
# Start postgres_exporter only if port 9187 is not in use (avoids "address already in use"
# when exporter was started by a previous process-compose run or another process).

set -e
POSTGRES_EXPORTER_PORT="${POSTGRES_EXPORTER_PORT:-9187}"

if command -v lsof >/dev/null 2>&1; then
  if lsof -Pi :"$POSTGRES_EXPORTER_PORT" -sTCP:LISTEN -t >/dev/null 2>&1; then
    echo "postgres_exporter already listening on port $POSTGRES_EXPORTER_PORT; holding process for process-compose."
    exec sh -c 'while true; do sleep 3600; done'
  fi
fi

exec postgres_exporter --no-collector.wal
