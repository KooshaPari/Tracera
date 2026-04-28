#!/usr/bin/env bash
set -euo pipefail

SERVICE_NAME="${1:-}"
PORT="${2:-}"

if [[ -z "$SERVICE_NAME" || -z "$PORT" ]]; then
  echo "usage: require-port-free.sh <service> <port>" >&2
  exit 1
fi

if lsof -nP -iTCP:"$PORT" -sTCP:LISTEN >/dev/null 2>&1; then
  echo "[$SERVICE_NAME] port $PORT is already in use:" >&2
  lsof -nP -iTCP:"$PORT" -sTCP:LISTEN >&2 || true
  exit 1
fi
