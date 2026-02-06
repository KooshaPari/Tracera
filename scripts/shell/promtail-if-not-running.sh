#!/bin/bash
# Start Promtail, clearing port 9080 if needed.

set -e

PORT=9080
SERVICE_NAME="Promtail"
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"

bash "$ROOT/scripts/shell/clear-port.sh" "$PORT" "$SERVICE_NAME"

echo "Starting $SERVICE_NAME on port $PORT..."
# Ensure target log paths exist so Promtail readiness doesn't fail on empty tails
mkdir -p .data/logs backend/logs .temporal/logs .process-compose/logs .promtail
touch .data/logs/tracertm.json \
      .data/logs/tracertm.log \
      .data/logs/tracertm_errors.log \
      backend/logs/app.log \
      .temporal/logs/temporal.log \
      .process-compose/logs/placeholder.log
exec promtail -config.file=deploy/monitoring/promtail-local-config.yaml
