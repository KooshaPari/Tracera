#!/usr/bin/env bash
# Start neo4j console only if not already running (avoids "already running" error
# when neo4j was started by brew or a previous process-compose run).
# Used by process-compose so we don't fail when service_manager already has neo4j up.

set -e
NEO4J_BOLT_PORT="${NEO4J_BOLT_PORT:-7687}"

if command -v lsof >/dev/null 2>&1; then
  if lsof -Pi :"$NEO4J_BOLT_PORT" -sTCP:LISTEN -t >/dev/null 2>&1; then
    echo "Neo4j already running on port $NEO4J_BOLT_PORT; holding process for process-compose."
    exec sh -c 'while true; do sleep 3600; done'
  fi
fi

exec neo4j console
