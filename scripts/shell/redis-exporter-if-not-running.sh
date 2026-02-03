#!/usr/bin/env bash
# Start redis_exporter only if port 9121 is not in use (avoids "address already in use"
# when exporter was started by a previous process-compose run or another process).

set -e
REDIS_EXPORTER_PORT="${REDIS_EXPORTER_PORT:-9121}"

if command -v lsof >/dev/null 2>&1; then
  if lsof -Pi :"$REDIS_EXPORTER_PORT" -sTCP:LISTEN -t >/dev/null 2>&1; then
    echo "redis_exporter already listening on port $REDIS_EXPORTER_PORT; holding process for process-compose."
    exec sh -c 'while true; do sleep 3600; done'
  fi
fi

exec redis_exporter --redis.addr=redis://localhost:6379
