#!/bin/bash
# SDK Cleanup Script - Remove Duplicate Files
# Phase 1: Cleanup & Consolidation

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
ARCHIVE_DIR="archive/cleanup_$(date +%Y%m%d_%H%M%S)"
SRC_DIR="src/pheno"
DRY_RUN=false

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --dry-run)
            DRY_RUN=true
            shift
            ;;
        *)
            echo "Unknown option: $1"
            exit 1
            ;;
    esac
done

echo -e "${BLUE}╔══════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║                                                              ║${NC}"
echo -e "${BLUE}║           SDK Cleanup - Duplicate File Removal               ║${NC}"
echo -e "${BLUE}║                                                              ║${NC}"
echo -e "${BLUE}╚══════════════════════════════════════════════════════════════╝${NC}"
echo ""

if [ "$DRY_RUN" = true ]; then
    echo -e "${YELLOW}🔍 DRY RUN MODE - No files will be deleted${NC}"
    echo ""
fi

# Step 1: Find duplicate files
echo -e "${BLUE}Step 1: Finding duplicate files...${NC}"
OLD_FILES=$(find "$SRC_DIR" -type f -name "*_old.py" 2>/dev/null || true)
REFACTORED_FILES=$(find "$SRC_DIR" -type f -name "*_refactored.py" 2>/dev/null || true)
BACKUP_FILES=$(find "$SRC_DIR" -type f -name "*_backup.py" 2>/dev/null || true)

OLD_COUNT=$(echo "$OLD_FILES" | wc -l | tr -d ' ')
REFACTORED_COUNT=$(echo "$REFACTORED_FILES" | wc -l | tr -d ' ')
BACKUP_COUNT=$(echo "$BACKUP_FILES" | wc -l | tr -d ' ')
TOTAL_COUNT=$((OLD_COUNT + REFACTORED_COUNT + BACKUP_COUNT))

echo -e "  Found ${GREEN}$OLD_COUNT${NC} *_old.py files"
echo -e "  Found ${GREEN}$REFACTORED_COUNT${NC} *_refactored.py files"
echo -e "  Found ${GREEN}$BACKUP_COUNT${NC} *_backup.py files"
echo -e "  ${YELLOW}Total: $TOTAL_COUNT files${NC}"
echo ""

if [ "$TOTAL_COUNT" -eq 0 ]; then
    echo -e "${GREEN}✅ No duplicate files found!${NC}"
    exit 0
fi

# Step 2: Check for imports and separate safe files
echo -e "${BLUE}Step 2: Checking for active imports...${NC}"
SAFE_FILES=""
UNSAFE_FILES=""

for file in $OLD_FILES $REFACTORED_FILES $BACKUP_FILES; do
    if [ -z "$file" ]; then
        continue
    fi
    
    basename=$(basename "$file" .py)
    # Check if any file imports this
    if grep -r "import $basename\|from.*$basename" "$SRC_DIR" --exclude="*_old.py" --exclude="*_refactored.py" --exclude="*_backup.py" >/dev/null 2>&1; then
        echo -e "  ${RED}⚠️  Found imports of: $basename${NC}"
        UNSAFE_FILES="$UNSAFE_FILES $file"
    else
        echo -e "  ${GREEN}✓${NC} No imports found: $basename"
        SAFE_FILES="$SAFE_FILES $file"
    fi
done

SAFE_COUNT=$(echo "$SAFE_FILES" | wc -w)
UNSAFE_COUNT=$(echo "$UNSAFE_FILES" | wc -w)

echo -e "  ${GREEN}Safe to remove: $SAFE_COUNT files${NC}"
echo -e "  ${YELLOW}Unsafe (have imports): $UNSAFE_COUNT files${NC}"
echo ""

# Step 3: Create archive
if [ "$DRY_RUN" = false ]; then
    echo -e "${BLUE}Step 3: Creating archive...${NC}"
    mkdir -p "$ARCHIVE_DIR"
    
    # Archive all files (safe and unsafe)
    for file in $OLD_FILES $REFACTORED_FILES $BACKUP_FILES; do
        if [ -n "$file" ] && [ -f "$file" ]; then
            cp "$file" "$ARCHIVE_DIR/"
            echo -e "  ${GREEN}✓${NC} Archived: $(basename "$file")"
        fi
    done
    
    echo -e "  ${GREEN}✅ Archive created: $ARCHIVE_DIR${NC}"
else
    echo -e "${YELLOW}Step 3: Would create archive: $ARCHIVE_DIR${NC}"
fi
echo ""

# Step 4: Remove duplicate files (only safe ones)
echo -e "${BLUE}Step 4: Removing duplicate files...${NC}"

if [ "$DRY_RUN" = false ]; then
    # Remove only safe files
    if [ -n "$SAFE_FILES" ]; then
        echo "$SAFE_FILES" | while read -r file; do
            if [ -n "$file" ] && [ -f "$file" ]; then
                rm "$file"
                echo -e "  ${GREEN}✓${NC} Removed: $file"
            fi
        done
    fi
    
    # Report unsafe files that need manual attention
    if [ -n "$UNSAFE_FILES" ]; then
        echo -e "${YELLOW}⚠️  Files with active imports (not removed):${NC}"
        echo "$UNSAFE_FILES" | while read -r file; do
            if [ -n "$file" ]; then
                echo -e "  ${YELLOW}→${NC} $file"
            fi
        done
    fi
    
    echo -e "  ${GREEN}✅ Safe duplicate files removed${NC}"
else
    echo -e "${YELLOW}Would remove safe files:${NC}"
    for file in $SAFE_FILES; do
        if [ -n "$file" ]; then
            echo -e "  ${YELLOW}→${NC} $file"
        fi
    done
    
    if [ -n "$UNSAFE_FILES" ]; then
        echo -e "${YELLOW}Files with imports (would skip):${NC}"
        for file in $UNSAFE_FILES; do
            if [ -n "$file" ]; then
                echo -e "  ${YELLOW}→${NC} $file"
            fi
        done
    fi
fi
echo ""

# Step 5: Summary
echo -e "${BLUE}╔══════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║                         Summary                              ║${NC}"
echo -e "${BLUE}╚══════════════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "  Files found:     ${YELLOW}$TOTAL_COUNT${NC}"
echo -e "  Files archived:  ${GREEN}$TOTAL_COUNT${NC}"
echo -e "  Files removed:   ${GREEN}$SAFE_COUNT${NC}"
echo -e "  Files skipped:   ${YELLOW}$UNSAFE_COUNT${NC} (have active imports)"
echo ""

if [ "$DRY_RUN" = false ]; then
    echo -e "${GREEN}✅ Cleanup complete!${NC}"
    echo ""
    echo -e "${BLUE}Next steps:${NC}"
    echo -e "  1. Review refactored files manually"
    echo -e "  2. Run tests: ${YELLOW}pytest tests/ -v${NC}"
    echo -e "  3. Commit changes: ${YELLOW}git add -A && git commit -m 'chore: remove duplicate files'${NC}"
else
    echo -e "${YELLOW}🔍 Dry run complete - no changes made${NC}"
    echo ""
    echo -e "${BLUE}To actually remove files, run:${NC}"
    echo -e "  ${YELLOW}./scripts/cleanup_duplicates.sh${NC}"
fi
echo ""

