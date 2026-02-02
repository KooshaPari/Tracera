#!/usr/bin/env bash
# jaeger-if-not-running.sh
# Wrapper to start Jaeger only if not already running (avoids port conflict).

set -euo pipefail

JAEGER_UI_PORT=16686
JAEGER_OTLP_PORT=4317

# Check if Jaeger UI is already running
if lsof -Pi :${JAEGER_UI_PORT} -sTCP:LISTEN -t >/dev/null 2>&1; then
  echo "ℹ️  Jaeger UI already running on port ${JAEGER_UI_PORT} (skipping start)"
  # Keep process alive so process-compose sees it as healthy
  tail -f /dev/null
  exit 0
fi

# Check if Jaeger OTLP collector is already running
if lsof -Pi :${JAEGER_OTLP_PORT} -sTCP:LISTEN -t >/dev/null 2>&1; then
  echo "ℹ️  Jaeger OTLP collector already running on port ${JAEGER_OTLP_PORT} (skipping start)"
  # Keep process alive so process-compose sees it as healthy
  tail -f /dev/null
  exit 0
fi

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
echo "   OTLP gRPC: localhost:${JAEGER_OTLP_PORT}"

# Start Jaeger all-in-one with OTLP enabled
# --collector.otlp.enabled=true enables OTLP receiver
# --collector.otlp.grpc.host-port=:4317 sets OTLP gRPC port
# --collector.otlp.http.host-port=:4318 sets OTLP HTTP port
exec ${JAEGER_CMD} \
  --collector.otlp.enabled=true \
  --collector.otlp.grpc.host-port=:${JAEGER_OTLP_PORT} \
  --collector.otlp.http.host-port=:4318
