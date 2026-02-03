#!/usr/bin/env bash
# Run the Go hot-reload air (github.com/air-verse/air), not the R "air" language server.
# Use $HOME/go/bin/air so we don't pick up the wrong binary from PATH.
set -e
cd "$(dirname "$0")/../../backend"
AIR_BIN="${GOPATH:-$HOME/go}/bin/air"
if [[ ! -x "$AIR_BIN" ]]; then
  echo "error: Go air not found at $AIR_BIN (install: go install github.com/air-verse/air@latest)" >&2
  exit 1
fi
exec "$AIR_BIN"
