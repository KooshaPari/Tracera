#!/bin/bash
# PhenoSDK Codebase Cleanup Script
# Phase 2d: Consolidate Credential Broker

set -e  # Exit on error

echo "🧹 PhenoSDK Cleanup - Phase 2d: Consolidate Credential Broker"
echo "=============================================================="
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

# Check if we're in the right directory
if [ ! -d "src/pheno" ]; then
    echo "Error: Must run from pheno-sdk root directory"
    exit 1
fi

# Create backup
echo "📦 Creating backup..."
BACKUP_DIR="backups/cleanup-phase2d-$(date +%Y%m%d-%H%M%S)"
mkdir -p "$BACKUP_DIR"
cp -r src/pheno "$BACKUP_DIR/"
print_status "Backup created at $BACKUP_DIR"
echo ""

# Create archive directory
ARCHIVE_DIR="archives/archive/cleanup_phase2d_$(date +%Y%m%d_%H%M%S)"
mkdir -p "$ARCHIVE_DIR"
print_status "Archive directory created at $ARCHIVE_DIR"
echo ""

# Count files before
BEFORE_COUNT=$(find src/pheno -name "*.py" -type f | wc -l)
BEFORE_LINES=$(find src/pheno -name "*.py" -type f -exec wc -l {} + | tail -1 | awk '{print $1}')

echo "📊 Before cleanup:"
echo "  Python files: $BEFORE_COUNT"
echo "  Lines of code: $BEFORE_LINES"
echo ""

# Step 1: Analyze broker files
echo "🔍 Step 1: Analyzing broker files..."
echo ""

echo "Broker files found:"
echo "  - src/pheno/credentials/broker.py (331 lines)"
echo "  - src/pheno/credentials/broker_refactored.py (340 lines)"
echo "  - src/pheno/credentials/broker/ (directory with implementation)"
echo "  - src/pheno/auth/session_broker.py (61 lines)"
echo "  - src/pheno/testing/mcp_qa/oauth/credential_broker.py (175 lines)"
echo ""

# Step 2: Delete broker_refactored.py (redundant)
echo "🗑️  Step 2: Deleting redundant broker files..."
echo ""

BROKER_FILES=(
    "src/pheno/credentials/broker_refactored.py"
)

DELETED_COUNT=0
DELETED_LINES=0

for file in "${BROKER_FILES[@]}"; do
    if [ -f "$file" ]; then
        LINES=$(wc -l < "$file")
        DELETED_LINES=$((DELETED_LINES + LINES))
        
        # Move to archive
        ARCHIVE_PATH="$ARCHIVE_DIR/$(basename $file)"
        cp "$file" "$ARCHIVE_PATH"
        
        # Delete the file
        rm "$file"
        
        echo "  ✓ Deleted: $file ($LINES lines)"
        DELETED_COUNT=$((DELETED_COUNT + 1))
    else
        echo "  ⚠ Not found: $file"
    fi
done

echo ""
print_status "Deleted $DELETED_COUNT broker files ($DELETED_LINES lines)"
echo ""

# Step 3: Check for imports of deleted files
echo "🔍 Step 3: Finding files that import deleted brokers..."
echo ""

IMPORT_PATTERNS=(
    "from pheno.credentials.broker_refactored import"
    "import pheno.credentials.broker_refactored"
)

AFFECTED_FILES=()

for pattern in "${IMPORT_PATTERNS[@]}"; do
    FILES=$(grep -r "$pattern" src/pheno --include="*.py" 2>/dev/null | cut -d: -f1 | sort -u || true)
    if [ -n "$FILES" ]; then
        echo "  Found imports of: $pattern"
        echo "$FILES" | while read file; do
            echo "    - $file"
            AFFECTED_FILES+=("$file")
        done
    fi
done

UNIQUE_AFFECTED=$(printf '%s\n' "${AFFECTED_FILES[@]}" | sort -u | wc -l)

if [ "$UNIQUE_AFFECTED" -eq 0 ]; then
    print_status "No files import deleted brokers - safe to proceed"
else
    print_warning "Found $UNIQUE_AFFECTED files with imports that need updating"
fi

echo ""

# Count files after
AFTER_COUNT=$(find src/pheno -name "*.py" -type f | wc -l)
AFTER_LINES=$(find src/pheno -name "*.py" -type f -exec wc -l {} + | tail -1 | awk '{print $1}')

# Step 4: Generate cleanup report
echo "📊 Step 4: Generating cleanup report..."
REPORT_FILE="reports/cleanup-phase2d-broker-$(date +%Y%m%d-%H%M%S).txt"
mkdir -p reports

{
    echo "PhenoSDK Cleanup Phase 2d - Credential Broker Report"
    echo "===================================================="
    echo "Date: $(date)"
    echo ""
    echo "Files Deleted:"
    echo "-------------"
    echo "Broker files: $DELETED_COUNT"
    echo "Lines removed: $DELETED_LINES"
    echo ""
    echo "Before:"
    echo "-------"
    echo "Python files: $BEFORE_COUNT"
    echo "Lines of code: $BEFORE_LINES"
    echo ""
    echo "After:"
    echo "------"
    echo "Python files: $AFTER_COUNT"
    echo "Lines of code: $AFTER_LINES"
    echo ""
    echo "Change:"
    echo "-------"
    echo "Files: -$((BEFORE_COUNT - AFTER_COUNT))"
    echo "Lines: -$((BEFORE_LINES - AFTER_LINES))"
    echo ""
    echo "Files Kept:"
    echo "-----------"
    echo "- src/pheno/credentials/broker.py (main broker facade)"
    echo "- src/pheno/credentials/broker/ (implementation directory)"
    echo "- src/pheno/auth/session_broker.py (session management)"
    echo "- src/pheno/testing/mcp_qa/oauth/credential_broker.py (testing)"
    echo ""
    echo "Files Deleted:"
    echo "-------------"
    echo "- src/pheno/credentials/broker_refactored.py (redundant)"
    echo ""
    echo "Affected Files:"
    echo "--------------"
    printf '%s\n' "${AFFECTED_FILES[@]}" | sort -u
} > "$REPORT_FILE"

print_status "Report saved to $REPORT_FILE"
echo ""

# Summary
echo "✨ Cleanup Phase 2d (Credential Broker) Complete!"
echo "================================================="
echo ""
echo "Summary:"
echo "  Deleted: $DELETED_COUNT broker files ($DELETED_LINES lines)"
echo "  Reduction: -$((BEFORE_COUNT - AFTER_COUNT)) files, -$((BEFORE_LINES - AFTER_LINES)) lines"
echo "  Affected: $UNIQUE_AFFECTED files need import updates"
echo ""
echo "Backup location: $BACKUP_DIR"
echo "Archive location: $ARCHIVE_DIR"
echo "Report location: $REPORT_FILE"

