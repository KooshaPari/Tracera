#!/usr/bin/env bash
# Guard a TCP port before starting a service.
# - If port is free: return success.
# - If port is in use by matching process: hold process for process-compose.
# - If port is in use by non-matching process: clear the port (TERM/KILL) or fail.
# Usage: guard-port.sh <SERVICE_NAME> <PORT> <MATCH_REGEX>

set -euo pipefail

SERVICE_NAME="${1:?missing SERVICE_NAME}"
PORT="${2:?missing PORT}"
MATCH_REGEX="${3:?missing MATCH_REGEX}"

if ! command -v lsof >/dev/null 2>&1; then
  echo "[$SERVICE_NAME] lsof not found; cannot guard port ${PORT}." >&2
  exit 1
fi
if ! command -v ps >/dev/null 2>&1; then
  echo "[$SERVICE_NAME] ps not found; cannot guard port ${PORT}." >&2
  exit 1
fi
if ! command -v nc >/dev/null 2>&1; then
  echo "[$SERVICE_NAME] nc not found; cannot guard port ${PORT}." >&2
  exit 1
fi

pids="$(lsof -nP -iTCP:"${PORT}" -sTCP:LISTEN -t 2>/dev/null || true)"
if [[ -z "$pids" ]]; then
  if nc -z 127.0.0.1 "$PORT" >/dev/null 2>&1; then
    pids="$(sudo -n lsof -nP -iTCP:"${PORT}" -sTCP:LISTEN -t 2>/dev/null || true)"
    if [[ -z "$pids" ]]; then
      # If sudo failed or returned nothing, but nc says it's in use,
      # we might be in a restricted environment (e.g. root-owned process).
      # Instead of failing, we can try to be "graceful" if it's a known service port.
      if [[ "$SERVICE_NAME" == "Neo4j" || "$SERVICE_NAME" == "PostgreSQL" || "$SERVICE_NAME" == "Redis" || "$SERVICE_NAME" == "NATS" ]]; then
        echo "[$SERVICE_NAME] Port ${PORT} is in use but PID is not visible (likely root-owned). Assuming service is up and holding."
        exec sh -c 'while true; do sleep 3600; done'
      fi
      echo "[$SERVICE_NAME] Port ${PORT} is in use but PID is not visible; cannot clear. Stop the owning process and retry." >&2
      exit 1
    fi
  else
    exit 0
  fi
fi

expected_found=0
for pid in $pids; do
  cmd="$(ps -p "$pid" -o comm= 2>/dev/null || true)"
  args="$(ps -p "$pid" -o args= 2>/dev/null || true)"
  if [[ "$cmd $args" =~ $MATCH_REGEX ]]; then
    expected_found=1
    break
  fi
done

if (( expected_found )); then
  echo "[$SERVICE_NAME] Already running on port ${PORT}; holding process for process-compose."
  exec sh -c 'while true; do sleep 3600; done'
fi

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
CLEAR_PORT="${ROOT}/scripts/shell/clear-port.sh"

if [[ ! -x "$CLEAR_PORT" ]]; then
  echo "[$SERVICE_NAME] clear-port.sh not found or not executable at ${CLEAR_PORT}." >&2
  exit 1
fi

echo "[$SERVICE_NAME] Port ${PORT} in use by non-matching process; clearing."
"$CLEAR_PORT" "$PORT" "$SERVICE_NAME"
