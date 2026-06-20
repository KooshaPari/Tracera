#!/bin/bash

# Enforce route entrypoint rules (no index/root route files).
# We rely on explicit route files (e.g., landing.tsx) + redirects where needed.

set -euo pipefail

ROOT_DIR="${1:-.}"
ROUTES_DIR="$ROOT_DIR/frontend/apps/web/src/routes"

if [ ! -d "$ROUTES_DIR" ]; then
  echo "❌ Routes directory not found: $ROUTES_DIR"
  exit 1
fi

if [ -f "$ROUTES_DIR/index.tsx" ] || [ -f "$ROUTES_DIR/index.ts" ]; then
  echo "❌ index route entrypoint is not allowed in $ROUTES_DIR"
  exit 1
fi

if [ -f "$ROUTES_DIR/root.tsx" ] || [ -f "$ROUTES_DIR/root.ts" ]; then
  echo "❌ root route entrypoint is not allowed in $ROUTES_DIR"
  exit 1
fi

ROUTE_TREE="$ROOT_DIR/frontend/apps/web/src/routeTree.gen.ts"
if [ -f "$ROUTE_TREE" ]; then
  if rg -q "'/root'" "$ROUTE_TREE"; then
    echo "❌ routeTree.gen.ts still references '/root' (delete root route entrypoint and regenerate)"
    exit 1
  fi
fi

echo "✅ Route entrypoint checks passed"
