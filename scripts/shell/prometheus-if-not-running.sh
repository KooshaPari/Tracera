#!/usr/bin/env bash
# Start Prometheus unless it's already running; clear port if a different process is bound.

set -euo pipefail

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
PROM_PORT="${PROMETHEUS_PORT:-9090}"

bash "$ROOT/scripts/shell/guard-port.sh" "Prometheus" "$PROM_PORT" "prometheus"

exec bash "$ROOT/scripts/shell/run-with-config-watch.sh" deploy/monitoring/prometheus.yml -- \
  prometheus \
    --config.file=deploy/monitoring/prometheus.yml \
    --storage.tsdb.path=.prometheus \
    --web.console.libraries=/opt/homebrew/share/prometheus/console_libraries \
    --web.console.templates=/opt/homebrew/share/prometheus/consoles \
    --web.enable-lifecycle
