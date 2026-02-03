#!/bin/bash
# Start Promtail only if it's not already running on port 9080

set -e

PORT=9080
SERVICE_NAME="Promtail"

# Check if port is already in use
if lsof -Pi :$PORT -sTCP:LISTEN -t >/dev/null 2>&1; then
    echo "$SERVICE_NAME is already running on port $PORT. Skipping start."
    # Keep process alive so process-compose doesn't restart
    tail -f /dev/null
else
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
fi
