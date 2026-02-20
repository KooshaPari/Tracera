#!/usr/bin/env bash
set -euo pipefail

scripts/shell/print-runtime-info.sh go-backend

exec bash scripts/shell/hot-reload-guard.sh \
  --name go-backend \
  --watch backend/internal \
  --watch backend/cmd \
  --watch backend/main.go \
  --watch backend/go.mod \
  --watch backend/go.sum \
  --exts go,mod,sum \
  --guard scripts/shell/build-go-backend.sh \
  -- ./backend/tmp/main
