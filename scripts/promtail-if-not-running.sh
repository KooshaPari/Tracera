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
    exec promtail -config.file=monitoring/promtail-local-config.yaml
fi
