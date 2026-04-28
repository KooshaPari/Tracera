#!/usr/bin/env bash
set -euo pipefail

cd backend
mkdir -p ./tmp

echo "[go-backend] build: go build -o ./tmp/main ."
if ! go build -o ./tmp/main .; then
  echo "[go-backend] build failed; keeping current process running" >&2
  exit 1
fi

echo "[go-backend] build ok"
