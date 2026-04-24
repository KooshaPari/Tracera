#!/usr/bin/env bash
# Start node_exporter only if port 9100 is not in use (avoids "address already in use"
# when exporter was started by a previous process-compose run or another process).

set -e
NODE_EXPORTER_PORT="${NODE_EXPORTER_PORT:-9100}"
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"

bash "$ROOT/scripts/shell/guard-port.sh" "node_exporter" "$NODE_EXPORTER_PORT" "node_exporter"

exec node_exporter --no-collector.thermal
