#!/bin/bash

# Python Naming Explosion Detection Script
# Prevents AI from creating versioned/prefixed module names.
# Catches all casing styles (snake, camel, Pascal, kebab, UPPER) and positions (prefix, suffix, middle).

set -e

RED='\033[0;31m'
YELLOW='\033[1;33m'
GREEN='\033[0;32m'
NC='\033[0m' # No Color

echo "🔍 Checking Python files for naming explosion patterns..."

python3 scripts/quality/check_naming_explosion.py --lang python --root .
