#!/usr/bin/env bash
# Reload NATS config (SIGHUP or nats-server --signal reload).

set -euo pipefail

if command -v nats-server >/dev/null 2>&1; then
  nats-server --signal reload || true
fi

pids="$(pgrep -f "nats-server" || true)"
if [[ -z "$pids" ]]; then
  echo "[nats] reload failed: nats-server not running." >&2
  exit 1
fi

kill -HUP ${pids} >/dev/null 2>&1 || true
exit 0
