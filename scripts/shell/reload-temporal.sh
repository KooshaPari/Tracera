#!/usr/bin/env bash
# Temporal dev server doesn't support hot reload; restart via process-compose.

set -euo pipefail

SERVICE="temporal"
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"

if command -v process-compose >/dev/null 2>&1; then
  process-compose process restart "$SERVICE"
  exit 0
fi

echo "[temporal] reload failed: process-compose not available for restart." >&2
exit 1
