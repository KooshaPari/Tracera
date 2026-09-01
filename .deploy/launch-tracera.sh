#!/usr/bin/env bash
# Tracera — Unix launcher
set -euo pipefail
TRACERA_HOME="${TRACERA_HOME:-$(cd "$(dirname "$0")/.." && pwd)}"
cd "$TRACERA_HOME"

echo "=== Tracera launcher (Unix) ==="

if command -v process-compose >/dev/null 2>&1; then
    echo "starting process-compose stack..."
    exec process-compose up -f process-compose.yml
fi

if command -v cargo >/dev/null 2>&1; then
    echo "process-compose not found; falling back to cargo run"
    (cd "$TRACERA_HOME/crates/tracera-server" && cargo run --release) &
    SERVER_PID=$!
    sleep 3
    echo "tracera-server PID: $SERVER_PID"
    wait $SERVER_PID
    exit $?
fi

echo "ERROR: neither process-compose nor cargo on PATH" >&2
exit 1
