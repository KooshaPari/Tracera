#!/usr/bin/env bash
set -euo pipefail

scripts/shell/print-runtime-info.sh python-backend

exec bash scripts/shell/hot-reload-guard.sh \
  --name python-backend \
  --watch src \
  --exts py \
  --guard "PYTHONPATH=./src .venv/bin/python -m compileall -q src" \
  -- bash scripts/shell/python-backend-run.sh
