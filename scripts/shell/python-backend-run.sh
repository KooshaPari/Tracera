#!/usr/bin/env bash
# Ensure python-backend port is clear before starting uvicorn.

set -euo pipefail

PYTHON_BACKEND_PORT="${PYTHON_BACKEND_PORT:-8000}"
existing_pids="$(pgrep -f "uvicorn tracertm.api.main:app" || true)"
if [[ -n "$existing_pids" ]]; then
  echo "[python-backend] Stopping existing uvicorn: ${existing_pids}"
  kill -TERM ${existing_pids} >/dev/null 2>&1 || true
  sleep 0.5
  still_running=()
  for pid in ${existing_pids}; do
    if kill -0 "${pid}" >/dev/null 2>&1; then
      still_running+=("${pid}")
    fi
  done
  if [[ ${#still_running[@]} -gt 0 ]]; then
    kill -KILL "${still_running[@]}" >/dev/null 2>&1 || true
  fi
fi

bash scripts/shell/clear-port.sh "${PYTHON_BACKEND_PORT}" python-backend

exec .venv/bin/uvicorn tracertm.api.main:app \
  --host 0.0.0.0 \
  --port "${PYTHON_BACKEND_PORT}"
