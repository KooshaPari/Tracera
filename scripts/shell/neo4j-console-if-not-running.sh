#!/usr/bin/env bash
# Start neo4j console only if not already running (avoids "already running" error
# when neo4j was started by brew or a previous process-compose run).
# Used by process-compose so we don't fail when service_manager already has neo4j up.

set -e
NEO4J_BOLT_PORT="${NEO4J_BOLT_PORT:-7687}"
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"

bash "$ROOT/scripts/shell/guard-port.sh" "Neo4j" "$NEO4J_BOLT_PORT" "neo4j"

exec neo4j console
