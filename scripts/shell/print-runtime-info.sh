#!/usr/bin/env bash
set -euo pipefail

SERVICE_NAME="${1:-service}"

bun_ver="unknown"
node_ver="unknown"
if command -v bun >/dev/null 2>&1; then
  bun_ver="$(bun --version)"
fi
if command -v node >/dev/null 2>&1; then
  node_ver="$(node --version)"
fi

echo "[${SERVICE_NAME}] runtime: bun=${bun_ver} node=${node_ver}"
