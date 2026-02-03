#!/usr/bin/env bash
# jaeger-if-not-running.sh
# Wrapper to start Jaeger only if not already running (avoids port conflict).

set -euo pipefail

JAEGER_UI_PORT=16686

# Check if Jaeger UI is already running
if lsof -Pi :${JAEGER_UI_PORT} -sTCP:LISTEN -t >/dev/null 2>&1; then
  echo "ℹ️  Jaeger UI already running on port ${JAEGER_UI_PORT} (skipping start)"
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

# Start Jaeger v2.x with default all-in-one settings (OTLP enabled by default)
exec ${JAEGER_CMD}
