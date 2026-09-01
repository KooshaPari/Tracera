#!/usr/bin/env bash
# Tracera — macOS launcher (double-clickable)
set -euo pipefail
cd "$(dirname "$0")/.."
BASE="$(pwd)"

echo "=== Tracera launcher (macOS) ==="

if command -v process-compose >/dev/null 2>&1; then
    process-compose up -f process-compose.yml
    open "http://localhost:8080"
    exit $?
fi

if command -v cargo >/dev/null 2>&1; then
    (cd "$BASE/crates/tracera-server" && cargo run --release) &
    sleep 3
    open "http://localhost:8080"
    wait
    exit $?
fi

osascript -e 'display alert "Tracera launcher" message "Neither process-compose nor cargo on PATH"'
exit 1
