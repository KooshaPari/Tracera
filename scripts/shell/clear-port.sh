#!/usr/bin/env bash
# Clear a TCP listening port before starting a service.
# Usage: clear-port.sh <PORT> <SERVICE_NAME>

set -euo pipefail

PORT="${1:?missing PORT}"
SERVICE_NAME="${2:-service}"

if ! command -v lsof >/dev/null 2>&1; then
  echo "[$SERVICE_NAME] lsof not found; cannot clear port ${PORT}."
  exit 1
fi
if ! command -v nc >/dev/null 2>&1; then
  echo "[$SERVICE_NAME] nc not found; cannot clear port ${PORT}."
  exit 1
fi

pids="$(lsof -nP -iTCP:"${PORT}" -sTCP:LISTEN -t 2>/dev/null || true)"
if [[ -z "$pids" ]]; then
  if ! nc -z 127.0.0.1 "$PORT" >/dev/null 2>&1; then
    exit 0
  fi
  pids="$(sudo -n lsof -nP -iTCP:"${PORT}" -sTCP:LISTEN -t 2>/dev/null || true)"
  if [[ -z "$pids" ]]; then
    echo "[$SERVICE_NAME] Port ${PORT} is in use but PID is not visible; cannot clear. Stop the owning process and retry." >&2
    exit 1
  fi
fi

pids="$(echo "$pids" | tr '\n' ' ')"
echo "[$SERVICE_NAME] Port ${PORT} in use by PID(s): ${pids}. Attempting to stop."

for pid in ${pids}; do
  echo "[$SERVICE_NAME] Sending TERM to PID ${pid}"
  kill -TERM "${pid}" >/dev/null 2>&1 || true
done

for _ in {1..10}; do
  sleep 0.5
  if ! lsof -nP -iTCP:"${PORT}" -sTCP:LISTEN -t >/dev/null 2>&1; then
    echo "[$SERVICE_NAME] Port ${PORT} cleared."
    exit 0
  fi
done

pids="$(lsof -nP -iTCP:"${PORT}" -sTCP:LISTEN -t | tr '\n' ' ')"
if [ -n "${pids}" ]; then
  echo "[$SERVICE_NAME] Port ${PORT} still in use; sending KILL to PID(s): ${pids}"
  for pid in ${pids}; do
    kill -KILL "${pid}" >/dev/null 2>&1 || true
  done
fi

sleep 0.5
if lsof -nP -iTCP:"${PORT}" -sTCP:LISTEN -t >/dev/null 2>&1; then
  echo "[$SERVICE_NAME] Failed to clear port ${PORT}; aborting startup."
  exit 1
fi

echo "[$SERVICE_NAME] Port ${PORT} cleared."
