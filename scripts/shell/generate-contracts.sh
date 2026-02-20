#!/usr/bin/env bash
# Generate OpenAPI specs + typed clients for all services.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"

cd "$PROJECT_ROOT"

if ! command -v bun >/dev/null 2>&1; then
  echo "[contracts] bun is required to generate TypeScript types." >&2
  exit 1
fi

if ! command -v go >/dev/null 2>&1; then
  echo "[contracts] go is required to generate Go OpenAPI specs." >&2
  exit 1
fi

if [ ! -d "$PROJECT_ROOT/.venv" ]; then
  echo "[contracts] .venv not found. Run: uv sync --all" >&2
  exit 1
fi

bash "$PROJECT_ROOT/scripts/shell/generate-openapi-python.sh"
bash "$PROJECT_ROOT/scripts/shell/generate-openapi-go.sh"
bash "$PROJECT_ROOT/scripts/shell/generate-typescript-types.sh"
bash "$PROJECT_ROOT/scripts/shell/generate-python-client.sh"
bash "$PROJECT_ROOT/scripts/shell/generate-grpc.sh" --typescript

echo "[contracts] Generation complete."
