#!/usr/bin/env bash
set -euo pipefail

# Frontend Naming Explosion Detection Script
# Prevents AI from creating versioned/prefixed component names.
# Catches all casing styles (camel, Pascal, snake, kebab) and positions (prefix, suffix, middle).

set -e

RED='\033[0;31m'
YELLOW='\033[1;33m'
GREEN='\033[0;32m'
NC='\033[0m' # No Color

echo "🔍 Checking for naming explosion patterns..."

FRONTEND_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
REPO_ROOT="$(cd "$FRONTEND_ROOT/.." && pwd)"

python3 "$REPO_ROOT/scripts/quality/check_naming_explosion.py" --lang frontend --root "$FRONTEND_ROOT"
