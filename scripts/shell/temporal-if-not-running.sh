#!/usr/bin/env bash
# Start temporal server only if not already running (avoids "addr already in use"
# when temporal was started by brew or a previous process-compose run).

set -e
TEMPORAL_PORT="${TEMPORAL_PORT:-7233}"
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"

bash "$ROOT/scripts/shell/guard-port.sh" "Temporal" "$TEMPORAL_PORT" "temporal"

exec temporal server start-dev --db-filename .temporal/temporal.db
