#!/usr/bin/env bash
# Start Grafana Alloy unless an Alloy-compatible collector is already running.

set -euo pipefail

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
ALLOY_PORT="${ALLOY_PORT:-12345}"
ALLOY_STORAGE_PATH="${ALLOY_STORAGE_PATH:-.alloy/data}"
ALLOY_CONFIG="${ALLOY_CONFIG:-deploy/monitoring/alloy-local.alloy}"

find_grafana_alloy() {
  local candidate
  for candidate in "${GRAFANA_ALLOY_BIN:-}" grafana-alloy "$HOME/.local/bin/grafana-alloy" alloy; do
    [ -z "$candidate" ] && continue
    if command -v "$candidate" >/dev/null 2>&1 && "$candidate" run --help 2>&1 | grep -q -- "--server.http.listen-addr"; then
      printf '%s\n' "$candidate"
      return 0
    fi
  done
  return 1
}

if curl -fsS "http://127.0.0.1:${ALLOY_PORT}/-/ready" >/dev/null 2>&1; then
  echo "Grafana Alloy already ready on port ${ALLOY_PORT}."
  exec tail -f /dev/null
fi

ALLOY_BIN="$(find_grafana_alloy)" || {
  echo "Grafana Alloy binary not found." >&2
  echo "Install grafana-alloy or set GRAFANA_ALLOY_BIN to the official Grafana Alloy binary." >&2
  exit 1
}

cd "$ROOT"
mkdir -p "$ALLOY_STORAGE_PATH" .process-compose/logs

if [ ! -f "$ALLOY_CONFIG" ]; then
  echo "Alloy config not found: $ALLOY_CONFIG" >&2
  exit 1
fi

echo "Starting Grafana Alloy on port ${ALLOY_PORT}..."
exec "$ALLOY_BIN" run \
  --server.http.listen-addr="127.0.0.1:${ALLOY_PORT}" \
  --storage.path="$ALLOY_STORAGE_PATH" \
  "$ALLOY_CONFIG"
