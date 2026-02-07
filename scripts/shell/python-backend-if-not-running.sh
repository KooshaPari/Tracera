#!/usr/bin/env bash
# Start python-backend only if port 8000 is not in use or unhealthy.
# This allows multiple agents to share a single running instance.

set -e
PORT="${PORT:-8000}"
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"

if command -v lsof >/dev/null 2>&1; then
  if lsof -Pi :"$PORT" -sTCP:LISTEN -t >/dev/null 2>&1; then
    # Check health if possible
    if curl -sf "http://localhost:${PORT}/health" >/dev/null 2>&1; then
      echo "Python Backend already running and healthy on port $PORT; holding process for process-compose."
      exec sh -c 'while true; do sleep 3600; done'
    else
      echo "Python Backend port $PORT in use but unhealthy; proceeding with startup (clear-port will handle it)."
    fi
  fi
fi

exec bash "${ROOT}/scripts/shell/start-python-backend.sh"
