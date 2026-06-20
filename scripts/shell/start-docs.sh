#!/usr/bin/env bash
set -euo pipefail

scripts/shell/print-runtime-info.sh docs
scripts/shell/require-port-free.sh docs 3001
rm -f frontend/apps/docs/.next/dev/lock
cd frontend
exec bun run dev:docs
