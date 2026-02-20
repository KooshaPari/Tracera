#!/usr/bin/env bash
# Jaeger readiness probe that verifies UI and OTLP gRPC are accepting connections.

set -euo pipefail

SERVICE_NAME="Jaeger"
UI_HOST="127.0.0.1"
UI_PORT="${JAEGER_UI_PORT:-16686}"
OTLP_PORT="${OTLP_GRPC_PORT:-4317}"

if ! command -v curl >/dev/null 2>&1; then
  echo "[$SERVICE_NAME] curl not found; cannot verify UI readiness." >&2
  exit 1
fi
if ! command -v nc >/dev/null 2>&1; then
  echo "[$SERVICE_NAME] nc not found; cannot verify OTLP port readiness." >&2
  exit 1
fi

UI_URL="http://${UI_HOST}:${UI_PORT}/"
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" --connect-timeout 3 --max-time 5 "$UI_URL" 2>/dev/null || echo "000")
if [[ "$HTTP_CODE" != "200" ]]; then
  echo "Readiness failed: $SERVICE_NAME UI GET $UI_URL returned $HTTP_CODE (expected 200)" >&2
  exit 1
fi

if ! nc -z "$UI_HOST" "$OTLP_PORT" >/dev/null 2>&1; then
  echo "Readiness failed: $SERVICE_NAME OTLP gRPC port ${OTLP_PORT} not accepting connections on ${UI_HOST}" >&2
  exit 1
fi

exit 0
