#!/usr/bin/env bash
set -euo pipefail

scripts/shell/print-runtime-info.sh frontend
scripts/shell/require-port-free.sh frontend 5173

cd frontend/apps/web
exec bun run dev
