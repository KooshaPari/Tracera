#!/bin/bash
# Start Grafana Alloy as the local log and trace collector.

set -e

PORT=12345
OTLP_GRPC_PORT=4319
SERVICE_NAME="Alloy"
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"

bash "$ROOT/scripts/shell/clear-port.sh" "$PORT" "$SERVICE_NAME"
bash "$ROOT/scripts/shell/clear-port.sh" "$OTLP_GRPC_PORT" "$SERVICE_NAME OTLP gRPC"

ALLOY_BIN="${GRAFANA_ALLOY_BIN:-}"
if [ -z "$ALLOY_BIN" ]; then
  for candidate in alloy grafana-alloy "$HOME/.local/bin/grafana-alloy"; do
    if command -v "$candidate" >/dev/null 2>&1 && "$candidate" run --help 2>&1 | grep -q -- "--server.http.listen-addr"; then
      ALLOY_BIN="$candidate"
      break
    fi
  done
fi

if [ -z "$ALLOY_BIN" ]; then
  echo "Grafana Alloy is required, but no Grafana Alloy binary was found on PATH." >&2
  echo "Install it with: brew install grafana-alloy" >&2
  echo "If another 'alloy' binary shadows Grafana Alloy, install the release binary as grafana-alloy." >&2
  echo "Then set GRAFANA_ALLOY_BIN=/path/to/grafana-alloy if it is not on PATH." >&2
  exit 127
fi

echo "Starting $SERVICE_NAME on port $PORT..."
echo "OTLP gRPC receiver: 127.0.0.1:${OTLP_GRPC_PORT}"
echo "Trace export target: ${PHENO_OBSERVABILITY_OTLP_GRPC_ENDPOINT:-127.0.0.1:4317} (shared Phenotype collector)"

# Ensure target log paths exist so Alloy file readers have stable targets on first boot.
mkdir -p .data/logs backend/logs .temporal/logs .process-compose/logs .alloy/data
touch .data/logs/tracertm.json \
      .data/logs/tracertm.log \
      .data/logs/tracertm_errors.log \
      backend/logs/app.log \
      .temporal/logs/temporal.log \
      .process-compose/logs/placeholder.log

exec "$ALLOY_BIN" run \
  --server.http.listen-addr=127.0.0.1:${PORT} \
  --storage.path=.alloy/data \
  deploy/monitoring/alloy-local.alloy
