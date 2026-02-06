#!/usr/bin/env bash
# Start redis only if not already running (avoids "6379 already in use"
# when redis was started by brew or a previous process-compose run).

set -e
REDIS_PORT="${REDIS_PORT:-6379}"
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
REDIS_CONFIG_PATH="${REDIS_CONFIG_PATH:-}"
if [[ -z "$REDIS_CONFIG_PATH" ]]; then
  if [[ -f "${ROOT}/config/redis.conf" ]]; then
    REDIS_CONFIG_PATH="${ROOT}/config/redis.conf"
  elif [[ -f "/opt/homebrew/etc/redis.conf" ]]; then
    REDIS_CONFIG_PATH="/opt/homebrew/etc/redis.conf"
  else
    REDIS_CONFIG_PATH="${ROOT}/config/redis.conf"
  fi
fi

if command -v lsof >/dev/null 2>&1; then
  if lsof -Pi :"$REDIS_PORT" -sTCP:LISTEN -t >/dev/null 2>&1; then
    echo "Redis already running on port $REDIS_PORT; holding process for process-compose."
    exec sh -c 'while true; do sleep 3600; done'
  fi
fi

exec redis-server "${REDIS_CONFIG_PATH}"
