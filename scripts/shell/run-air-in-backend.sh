#!/usr/bin/env bash
# Run the Go hot-reload air (github.com/air-verse/air), not the R "air" language server.
# Use $HOME/go/bin/air so we don't pick up the wrong binary from PATH.
set -e
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "${ROOT}/backend"
AIR_BIN="${GOPATH:-$HOME/go}/bin/air"
if [[ ! -x "$AIR_BIN" ]]; then
  AIR_BIN="$(command -v air || true)"
fi
if [[ -z "$AIR_BIN" || ! -x "$AIR_BIN" ]]; then
  if [[ -x "/opt/homebrew/bin/air" ]]; then
    AIR_BIN="/opt/homebrew/bin/air"
  elif [[ -x "/usr/local/bin/air" ]]; then
    AIR_BIN="/usr/local/bin/air"
  fi
fi
if [[ -z "$AIR_BIN" || ! -x "$AIR_BIN" ]]; then
  echo "error: Go air not found (install: go install github.com/air-verse/air@latest)" >&2
  exit 1
fi
AIR_CONFIG="${AIR_CONFIG:-${ROOT}/backend/.air.toml}"
exec "$AIR_BIN" -c "$AIR_CONFIG"
