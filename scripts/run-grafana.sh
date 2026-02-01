#!/usr/bin/env bash
# Run Grafana with correct --homepath so it finds config defaults.
# Use 'grafana server' (grafana-server is deprecated).
# Call from process-compose or run-with-config-watch.sh.
# GRAFANA_HOME is auto-detected if unset (Homebrew, binary location, or common paths).

set -e
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

if [ -z "$GRAFANA_HOME" ]; then
  # 1) Homebrew (exact prefix for grafana formula)
  if command -v brew &>/dev/null; then
    PREFIX=$(brew --prefix grafana 2>/dev/null || true)
    [ -n "$PREFIX" ] && [ -d "$PREFIX/share/grafana" ] && GRAFANA_HOME="$PREFIX/share/grafana"
  fi
  # 2) Derive from `grafana` binary location (e.g. /opt/homebrew/bin/grafana -> /opt/homebrew/share/grafana)
  if [ -z "$GRAFANA_HOME" ] && GRAFANA_BIN=$(command -v grafana 2>/dev/null); then
    BIN_DIR=$(dirname "$GRAFANA_BIN")
    PREFIX=$(dirname "$BIN_DIR")
    CANDIDATE="$PREFIX/share/grafana"
    [ -d "$CANDIDATE" ] && GRAFANA_HOME="$CANDIDATE"
  fi
  # 3) Common install paths (only set if directory exists)
  [ -z "$GRAFANA_HOME" ] && [ -d /opt/homebrew/share/grafana ] && GRAFANA_HOME=/opt/homebrew/share/grafana
  [ -z "$GRAFANA_HOME" ] && [ -d /usr/local/share/grafana ] && GRAFANA_HOME=/usr/local/share/grafana
  [ -z "$GRAFANA_HOME" ] && [ -d /usr/share/grafana ] && GRAFANA_HOME=/usr/share/grafana
fi

if [ -z "$GRAFANA_HOME" ] || [ ! -d "${GRAFANA_HOME}" ]; then
  echo "Grafana home not found. Install Grafana (e.g. brew install grafana) or set GRAFANA_HOME to the share/grafana directory." >&2
  exit 1
fi

exec grafana server --config monitoring/grafana.ini --homepath "$GRAFANA_HOME"
