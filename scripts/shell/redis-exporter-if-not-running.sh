#!/usr/bin/env bash
# Start redis_exporter for the Redis-compatible endpoint only if port 9121 is not in use.

set -e
REDIS_EXPORTER_PORT="${REDIS_EXPORTER_PORT:-9121}"
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"

bash "$ROOT/scripts/shell/guard-port.sh" "redis_exporter" "$REDIS_EXPORTER_PORT" "redis_exporter"

exec redis_exporter --redis.addr=redis://localhost:6379
