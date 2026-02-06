#!/usr/bin/env bash
# Start Caddy unless it's already running; clear port if a different process is bound.

set -euo pipefail

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
CADDY_PORT="${CADDY_PORT:-4000}"

bash "$ROOT/scripts/shell/guard-port.sh" "Caddy" "$CADDY_PORT" "caddy"

exec bash "$ROOT/scripts/shell/with-lifecycle.sh" caddy \
  caddy run --config config/Caddyfile.dev --adapter caddyfile --watch
