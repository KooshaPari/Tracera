#!/usr/bin/env bash
# Start the Redis-compatible cache service only if it is not already running.
# Dragonfly is the default runtime; set REDIS_COMPAT_PROVIDER=redis only for
# explicit Redis compatibility testing.

set -e
REDIS_PORT="${REDIS_PORT:-6379}"
REDIS_COMPAT_PROVIDER="${REDIS_COMPAT_PROVIDER:-dragonfly}"
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
    echo "Redis-compatible service already running on port $REDIS_PORT; holding process for process-compose."
    exec sh -c 'while true; do sleep 3600; done'
  fi
fi

case "$REDIS_COMPAT_PROVIDER" in
  redis)
    if ! command -v redis-server >/dev/null 2>&1; then
      echo "Redis fallback requested with REDIS_COMPAT_PROVIDER=redis, but 'redis-server' is not on PATH." >&2
      exit 127
    fi
    exec redis-server "${REDIS_CONFIG_PATH}"
    ;;
  dragonfly)
    if command -v dragonfly >/dev/null 2>&1; then
      exec dragonfly --port "$REDIS_PORT" --dir .dragonfly
    fi
    if command -v docker >/dev/null 2>&1; then
      mkdir -p "$ROOT/.dragonfly"
      exec docker run --rm \
        --name tracera-dragonfly \
        -p "$REDIS_PORT:6379" \
        -v "$ROOT/.dragonfly:/data" \
        docker.dragonflydb.io/dragonflydb/dragonfly:latest \
        --dir /data
    fi
    echo "Dragonfly requested with REDIS_COMPAT_PROVIDER=dragonfly, but neither 'dragonfly' nor 'docker' is on PATH." >&2
    echo "Install Dragonfly, or set REDIS_COMPAT_PROVIDER=redis for explicit fallback testing." >&2
    exit 127
    ;;
  *)
    echo "Unsupported REDIS_COMPAT_PROVIDER=$REDIS_COMPAT_PROVIDER; expected 'redis' or 'dragonfly'." >&2
    exit 2
    ;;
esac
