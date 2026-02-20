#!/usr/bin/env bash
# Start Grafana unless it's already running; clear port if a different process is bound.

set -euo pipefail

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
GRAFANA_PORT="${GRAFANA_PORT:-3000}"

bash "$ROOT/scripts/shell/guard-port.sh" "Grafana" "$GRAFANA_PORT" "grafana"

exec bash "$ROOT/scripts/shell/run-with-config-watch.sh" deploy/monitoring/grafana.ini -- \
  bash "$ROOT/scripts/shell/run-grafana.sh"
