#!/usr/bin/env bash
# jaeger-if-not-running.sh
# Wrapper to start Jaeger only if not already running (avoids port conflict).

set -euo pipefail

JAEGER_UI_PORT=16686
OTLP_GRPC_PORT=4317
OTLP_HTTP_PORT=4318
COLLECTOR_OTLP_ENABLED="${COLLECTOR_OTLP_ENABLED:-true}"
export COLLECTOR_OTLP_ENABLED
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"

bash "$ROOT/scripts/shell/guard-port.sh" "Jaeger" "$JAEGER_UI_PORT" "jaeger|jaeger-all-in-one"
bash "$ROOT/scripts/shell/guard-port.sh" "Jaeger" "$OTLP_GRPC_PORT" "jaeger|jaeger-all-in-one"
bash "$ROOT/scripts/shell/guard-port.sh" "Jaeger" "$OTLP_HTTP_PORT" "jaeger|jaeger-all-in-one"

# Check if jaeger is installed
if ! command -v jaeger >/dev/null 2>&1 && ! command -v jaeger-all-in-one >/dev/null 2>&1; then
  echo "❌ Jaeger not found. Install with: brew install jaegertracing/jaeger/jaeger"
  echo "   Or download from: https://www.jaegertracing.io/download/"
  exit 1
fi

# Determine which command to use
JAEGER_CMD="jaeger"
if ! command -v jaeger >/dev/null 2>&1; then
  JAEGER_CMD="jaeger-all-in-one"
fi

echo "🔍 Starting Jaeger all-in-one..."
echo "   UI: http://localhost:${JAEGER_UI_PORT}"
echo "   OTLP gRPC: localhost:${OTLP_GRPC_PORT}"
echo "   OTLP HTTP: localhost:${OTLP_HTTP_PORT}"

# Start Jaeger v2.x with OTLP receivers bound on all interfaces (avoid IPv6 localhost refused).
exec ${JAEGER_CMD} \
  --set=receivers.otlp.protocols.grpc.endpoint=:4317 \
  --set=receivers.otlp.protocols.http.endpoint=:4318 \
  --set=service.extensions=[healthcheckv2,jaeger_storage,jaeger_query,remote_sampling,expvar]
