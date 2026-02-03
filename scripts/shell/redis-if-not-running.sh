#!/usr/bin/env bash
# Start redis only if not already running (avoids "6379 already in use"
# when redis was started by brew or a previous process-compose run).

set -e
REDIS_PORT="${REDIS_PORT:-6379}"

if command -v lsof >/dev/null 2>&1; then
  if lsof -Pi :"$REDIS_PORT" -sTCP:LISTEN -t >/dev/null 2>&1; then
    echo "Redis already running on port $REDIS_PORT; holding process for process-compose."
    exec sh -c 'while true; do sleep 3600; done'
  fi
fi

exec redis-server /opt/homebrew/etc/redis.conf
