#!/usr/bin/env bash
# Start frontend only if port 5173 is not in use.
# This allows multiple agents to share a single running instance.

set -e
PORT="${FRONTEND_PORT:-5173}"
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"

if command -v lsof >/dev/null 2>&1; then
  if lsof -Pi :"$PORT" -sTCP:LISTEN -t >/dev/null 2>&1; then
    echo "Frontend already running on port $PORT; holding process for process-compose."
    exec sh -c 'while true; do sleep 3600; done'
  fi
fi

exec bash "${ROOT}/scripts/shell/start-frontend.sh"
