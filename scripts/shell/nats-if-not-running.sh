#!/usr/bin/env bash
# Start nats-server only if port 4222 is not in use (avoids "address already in use"
# when nats was started by brew or a previous process-compose run).

set -e
NATS_PORT="${NATS_PORT:-4222}"
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
NATS_CONFIG_PATH="${NATS_CONFIG_PATH:-${ROOT}/config/nats-server.conf}"

if command -v lsof >/dev/null 2>&1; then
  if lsof -Pi :"$NATS_PORT" -sTCP:LISTEN -t >/dev/null 2>&1; then
    echo "NATS already running on port $NATS_PORT; holding process for process-compose."
    exec sh -c 'while true; do sleep 3600; done'
  fi
fi

exec nats-server -c "${NATS_CONFIG_PATH}"
