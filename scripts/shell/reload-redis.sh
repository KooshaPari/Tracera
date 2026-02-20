#!/usr/bin/env bash
# Redis doesn't support config file reload; restart via process-compose if possible.

set -euo pipefail

SERVICE="redis"
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"

if command -v process-compose >/dev/null 2>&1; then
  process-compose process restart "$SERVICE"
  exit 0
fi

echo "[redis] reload failed: process-compose not available for restart." >&2
exit 1
