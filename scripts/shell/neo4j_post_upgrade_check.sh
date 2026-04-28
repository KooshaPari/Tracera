#!/usr/bin/env bash
set -euo pipefail

launch_agent="$HOME/Library/LaunchAgents/homebrew.mxcl.neo4j.plist"
neo4j_conf_dir="/opt/homebrew/etc/neo4j"
neo4j_conf_file="$neo4j_conf_dir/neo4j.conf"
run_dir="/opt/homebrew/var/run/neo4j"

fail() {
  echo "ERROR: $*" >&2
  exit 1
}

[ -f "$launch_agent" ] || fail "LaunchAgent not found at $launch_agent"

conf_env=$(/usr/libexec/PlistBuddy -c "Print :EnvironmentVariables:NEO4J_CONF" "$launch_agent" 2>/dev/null || true)
[ -n "$conf_env" ] || fail "NEO4J_CONF not set in LaunchAgent"
[ "$conf_env" = "$neo4j_conf_dir" ] || fail "NEO4J_CONF is '$conf_env' (expected '$neo4j_conf_dir')"

[ -d "$neo4j_conf_dir" ] || fail "Config dir missing: $neo4j_conf_dir"
[ -f "$neo4j_conf_file" ] || fail "Config file missing: $neo4j_conf_file"

grep -q "^server.directories.run=$run_dir$" "$neo4j_conf_file" \
  || fail "server.directories.run not set to $run_dir in $neo4j_conf_file"

[ -d "$run_dir" ] || fail "Run dir missing: $run_dir"

if /opt/homebrew/opt/neo4j/bin/neo4j status >/dev/null 2>&1; then
  echo "OK: Neo4j running"
else
  echo "WARN: Neo4j not running"
fi

echo "OK: LaunchAgent and config are sane"
