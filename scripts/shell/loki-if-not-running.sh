#!/bin/bash
# Start Loki only if it's not already running on port 3100

set -e

PORT=3100
SERVICE_NAME="Loki"

# Check if port is already in use
if lsof -Pi :$PORT -sTCP:LISTEN -t >/dev/null 2>&1; then
    echo "$SERVICE_NAME is already running on port $PORT. Skipping start."
    # Keep process alive so process-compose doesn't restart
    tail -f /dev/null
else
    echo "Starting $SERVICE_NAME on port $PORT..."
    exec loki -config.file=deploy/monitoring/loki-local-config.yaml
fi
