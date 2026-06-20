#!/usr/bin/env bash
# Redis-compatible runtime config reload. Dragonfly is the default runtime and does not use
# config/redis.conf; when Redis fallback is selected, restart via process-compose if possible.

set -euo pipefail

SERVICE="${REDIS_COMPAT_PROCESS:-dragonfly}"
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"

if command -v process-compose >/dev/null 2>&1; then
  process-compose process restart "$SERVICE"
  exit 0
fi

echo "[redis-compatible] reload failed: process-compose not available for restart." >&2
exit 1
