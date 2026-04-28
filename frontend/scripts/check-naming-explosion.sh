#!/bin/bash

# Frontend Naming Explosion Detection Script
# Prevents AI from creating versioned/prefixed component names.
# Catches all casing styles (camel, Pascal, snake, kebab) and positions (prefix, suffix, middle).

set -e

RED='\033[0;31m'
YELLOW='\033[1;33m'
GREEN='\033[0;32m'
NC='\033[0m' # No Color

echo "🔍 Checking for naming explosion patterns..."

python3 ../scripts/quality/check_naming_explosion.py --lang frontend --root ..
