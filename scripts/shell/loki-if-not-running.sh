#!/bin/bash
# Start Loki only if it's not already running on port 3100

set -e

PORT=3100
SERVICE_NAME="Loki"
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"

bash "$ROOT/scripts/shell/guard-port.sh" "$SERVICE_NAME" "$PORT" "loki"

echo "Starting $SERVICE_NAME on port $PORT..."
exec loki -config.file=deploy/monitoring/loki-local-config.yaml
