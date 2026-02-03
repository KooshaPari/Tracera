#!/usr/bin/env bash
# Start node_exporter only if port 9100 is not in use (avoids "address already in use"
# when exporter was started by a previous process-compose run or another process).

set -e
NODE_EXPORTER_PORT="${NODE_EXPORTER_PORT:-9100}"

if command -v lsof >/dev/null 2>&1; then
  if lsof -Pi :"$NODE_EXPORTER_PORT" -sTCP:LISTEN -t >/dev/null 2>&1; then
    echo "node_exporter already listening on port $NODE_EXPORTER_PORT; holding process for process-compose."
    exec sh -c 'while true; do sleep 3600; done'
  fi
fi

exec node_exporter --no-collector.thermal
