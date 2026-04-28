#!/bin/bash
# PhenoSDK Root Cleanup Script
# Phase 4b: Consolidate Config Files

set -e  # Exit on error

echo "🧹 PhenoSDK Root Cleanup - Phase 4b: Config Files"
echo "=================================================="
echo ""

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

print_status() {
    echo -e "${GREEN}✓${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

# Create backup
echo "📦 Creating backup..."
BACKUP_DIR="backups/cleanup-phase4b-$(date +%Y%m%d-%H%M%S)"
mkdir -p "$BACKUP_DIR"
cp *.yaml *.yml *.json 2>/dev/null "$BACKUP_DIR/" || true
print_status "Backup created at $BACKUP_DIR"
echo ""

# Count before
BEFORE_COUNT=$(ls -1 *.yaml *.yml *.json 2>/dev/null | wc -l)
echo "📊 Before cleanup: $BEFORE_COUNT config files at root"
echo ""

# Create directories
echo "📁 Creating directories..."
mkdir -p config/examples
mkdir -p docker
print_status "Directories created"
echo ""

# Move example configs
echo "📦 Moving example configs to config/examples/..."
echo ""

EXAMPLE_CONFIGS=(
    "advanced-config.yaml"
    "config.yml.example"
    "generated-example.yaml"
    "project.example.yaml"
    "secrets.yml.example"
)

MOVED_EXAMPLES=0

for file in "${EXAMPLE_CONFIGS[@]}"; do
    if [ -f "$file" ]; then
        mv "$file" "config/examples/"
        echo "  ✓ Moved: $file → config/examples/"
        MOVED_EXAMPLES=$((MOVED_EXAMPLES + 1))
    else
        echo "  ⚠ Not found: $file"
    fi
done

echo ""
print_status "Moved $MOVED_EXAMPLES example configs"
echo ""

# Move docker configs
echo "🐳 Moving docker configs to docker/..."
echo ""

DOCKER_CONFIGS=(
    "docker-compose.xaas.yml"
    "docker-compose.yml"
)

MOVED_DOCKER=0

for file in "${DOCKER_CONFIGS[@]}"; do
    if [ -f "$file" ]; then
        mv "$file" "docker/"
        echo "  ✓ Moved: $file → docker/"
        MOVED_DOCKER=$((MOVED_DOCKER + 1))
    else
        echo "  ⚠ Not found: $file"
    fi
done

echo ""
print_status "Moved $MOVED_DOCKER docker configs"
echo ""

# Delete test configs
echo "🗑️  Deleting test configs..."
echo ""

TEST_CONFIGS=(
    "test-config.json"
    "test-config.yaml"
    "test_project_config_demo.py"
)

DELETED_TESTS=0

for file in "${TEST_CONFIGS[@]}"; do
    if [ -f "$file" ]; then
        rm "$file"
        echo "  ✓ Deleted: $file"
        DELETED_TESTS=$((DELETED_TESTS + 1))
    else
        echo "  ⚠ Not found: $file"
    fi
done

echo ""
print_status "Deleted $DELETED_TESTS test configs"
echo ""

# Count after
AFTER_COUNT=$(ls -1 *.yaml *.yml *.json 2>/dev/null | wc -l)
echo "📊 After cleanup: $AFTER_COUNT config files at root"
echo ""

echo "✨ Phase 4b Complete!"
echo "===================="
echo ""
echo "Summary:"
echo "  Moved to config/examples/: $MOVED_EXAMPLES files"
echo "  Moved to docker/: $MOVED_DOCKER files"
echo "  Deleted: $DELETED_TESTS files"
echo "  Total removed from root: $((MOVED_EXAMPLES + MOVED_DOCKER + DELETED_TESTS)) files"
echo ""
echo "Backup location: $BACKUP_DIR"

