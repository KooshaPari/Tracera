#!/bin/bash
# Analyze files to delete and generate deletion report

set -e

echo "🔍 PhenoSDK Deletion Analysis"
echo "============================="
echo ""

# Output file
REPORT="reports/deletion_analysis_$(date +%Y%m%d-%H%M%S).txt"
mkdir -p reports

{
    echo "PhenoSDK Deletion Analysis Report"
    echo "=================================="
    echo "Date: $(date)"
    echo ""
    
    # 1. Old files
    echo "1. OLD FILES (*_old.py, *_backup.py, *_deprecated.py)"
    echo "======================================================"
    OLD_FILES=$(find src/pheno -name "*_old.py" -o -name "*_backup.py" -o -name "*_deprecated.py" 2>/dev/null || true)
    if [ -n "$OLD_FILES" ]; then
        echo "$OLD_FILES" | while read file; do
            lines=$(wc -l < "$file" 2>/dev/null || echo "0")
            echo "  $file ($lines lines)"
        done
        total_old=$(echo "$OLD_FILES" | wc -l)
        total_lines=$(echo "$OLD_FILES" | xargs wc -l 2>/dev/null | tail -1 | awk '{print $1}')
        echo ""
        echo "  Total: $total_old files, $total_lines lines"
    else
        echo "  None found"
    fi
    echo ""
    
    # 2. Old directories
    echo "2. OLD DIRECTORIES (*_old/)"
    echo "==========================="
    OLD_DIRS=$(find src/pheno -type d -name "*_old" 2>/dev/null || true)
    if [ -n "$OLD_DIRS" ]; then
        echo "$OLD_DIRS" | while read dir; do
            files=$(find "$dir" -name "*.py" 2>/dev/null | wc -l)
            lines=$(find "$dir" -name "*.py" -exec wc -l {} + 2>/dev/null | tail -1 | awk '{print $1}' || echo "0")
            echo "  $dir ($files files, $lines lines)"
        done
        total_dirs=$(echo "$OLD_DIRS" | wc -l)
        echo ""
        echo "  Total: $total_dirs directories"
    else
        echo "  None found"
    fi
    echo ""
    
    # 3. Factory files
    echo "3. FACTORY FILES (*_factory.py)"
    echo "==============================="
    FACTORY_FILES=$(find src/pheno/core -name "*_factory.py" 2>/dev/null || true)
    if [ -n "$FACTORY_FILES" ]; then
        echo "$FACTORY_FILES" | while read file; do
            lines=$(wc -l < "$file" 2>/dev/null || echo "0")
            echo "  $file ($lines lines)"
        done
        total_factories=$(echo "$FACTORY_FILES" | wc -l)
        total_lines=$(echo "$FACTORY_FILES" | xargs wc -l 2>/dev/null | tail -1 | awk '{print $1}')
        echo ""
        echo "  Total: $total_factories files, $total_lines lines"
        echo ""
        echo "  RECOMMENDATION: Keep only exception_factory.py, delete rest"
    else
        echo "  None found"
    fi
    echo ""
    
    # 4. Registry files
    echo "4. REGISTRY FILES (*_registry.py)"
    echo "================================="
    REGISTRY_FILES=$(find src/pheno/core -name "*_registry.py" 2>/dev/null || true)
    if [ -n "$REGISTRY_FILES" ]; then
        echo "$REGISTRY_FILES" | while read file; do
            lines=$(wc -l < "$file" 2>/dev/null || echo "0")
            echo "  $file ($lines lines)"
        done
        total_registries=$(echo "$REGISTRY_FILES" | wc -l)
        total_lines=$(echo "$REGISTRY_FILES" | xargs wc -l 2>/dev/null | tail -1 | awk '{print $1}')
        echo ""
        echo "  Total: $total_registries files, $total_lines lines"
        echo ""
        echo "  RECOMMENDATION: Keep only adapter_registry.py, delete rest"
    else
        echo "  None found"
    fi
    echo ""
    
    # 5. Unified files
    echo "5. UNIFIED FILES (unified_*.py)"
    echo "==============================="
    UNIFIED_FILES=$(find src/pheno -name "unified_*.py" 2>/dev/null || true)
    if [ -n "$UNIFIED_FILES" ]; then
        echo "$UNIFIED_FILES" | while read file; do
            lines=$(wc -l < "$file" 2>/dev/null || echo "0")
            echo "  $file ($lines lines)"
        done
        total_unified=$(echo "$UNIFIED_FILES" | wc -l)
        total_lines=$(echo "$UNIFIED_FILES" | xargs wc -l 2>/dev/null | tail -1 | awk '{print $1}')
        echo ""
        echo "  Total: $total_unified files, $total_lines lines"
        echo ""
        echo "  RECOMMENDATION: Consolidate to 5-10 files in adapters/, delete rest"
    else
        echo "  None found"
    fi
    echo ""
    
    # 6. Duplicate credential brokers
    echo "6. CREDENTIAL BROKER DUPLICATES"
    echo "================================"
    BROKER_FILES=$(find src/pheno/credentials -name "broker*.py" 2>/dev/null || true)
    if [ -n "$BROKER_FILES" ]; then
        echo "$BROKER_FILES" | while read file; do
            lines=$(wc -l < "$file" 2>/dev/null || echo "0")
            echo "  $file ($lines lines)"
        done
        echo ""
        echo "  RECOMMENDATION: Keep broker.py, merge features from broker_refactored.py, delete broker_old.py"
    else
        echo "  None found"
    fi
    echo ""
    
    # 7. __pycache__ directories
    echo "7. __pycache__ DIRECTORIES"
    echo "=========================="
    PYCACHE_COUNT=$(find src/pheno -type d -name "__pycache__" 2>/dev/null | wc -l)
    echo "  Total: $PYCACHE_COUNT directories"
    echo "  RECOMMENDATION: Delete all (should be in .gitignore)"
    echo ""
    
    # 8. .pyc files
    echo "8. .pyc FILES"
    echo "============="
    PYC_COUNT=$(find src/pheno -name "*.pyc" 2>/dev/null | wc -l)
    echo "  Total: $PYC_COUNT files"
    echo "  RECOMMENDATION: Delete all (should be in .gitignore)"
    echo ""
    
    # Summary
    echo "SUMMARY"
    echo "======="
    echo ""
    
    # Calculate totals
    total_old_files=$(find src/pheno -name "*_old.py" -o -name "*_backup.py" -o -name "*_deprecated.py" 2>/dev/null | wc -l || echo "0")
    total_old_dirs=$(find src/pheno -type d -name "*_old" 2>/dev/null | wc -l || echo "0")
    total_factories=$(find src/pheno/core -name "*_factory.py" 2>/dev/null | wc -l || echo "0")
    total_registries=$(find src/pheno/core -name "*_registry.py" 2>/dev/null | wc -l || echo "0")
    total_unified=$(find src/pheno -name "unified_*.py" 2>/dev/null | wc -l || echo "0")
    
    echo "Files to delete:"
    echo "  Old files: $total_old_files"
    echo "  Old directories: $total_old_dirs"
    echo "  Factories (keep 1): $((total_factories - 1))"
    echo "  Registries (keep 1): $((total_registries - 1))"
    echo "  Unified files (keep 5-10): $((total_unified - 7))"
    echo "  Credential brokers (keep 1): 2"
    echo "  __pycache__ dirs: $PYCACHE_COUNT"
    echo "  .pyc files: $PYC_COUNT"
    echo ""
    
    total_deletions=$((total_old_files + total_old_dirs + total_factories - 1 + total_registries - 1 + total_unified - 7 + 2))
    echo "TOTAL FILES/DIRS TO DELETE: ~$total_deletions"
    echo ""
    
    # Estimated line savings
    echo "ESTIMATED LINE SAVINGS"
    echo "======================"
    echo ""
    
    old_lines=$(find src/pheno -name "*_old.py" -o -name "*_backup.py" -o -name "*_deprecated.py" 2>/dev/null | xargs wc -l 2>/dev/null | tail -1 | awk '{print $1}' || echo "0")
    factory_lines=$(find src/pheno/core -name "*_factory.py" 2>/dev/null | xargs wc -l 2>/dev/null | tail -1 | awk '{print $1}' || echo "0")
    registry_lines=$(find src/pheno/core -name "*_registry.py" 2>/dev/null | xargs wc -l 2>/dev/null | tail -1 | awk '{print $1}' || echo "0")
    unified_lines=$(find src/pheno -name "unified_*.py" 2>/dev/null | xargs wc -l 2>/dev/null | tail -1 | awk '{print $1}' || echo "0")
    
    echo "  Old files: ~$old_lines lines"
    echo "  Factories: ~$factory_lines lines"
    echo "  Registries: ~$registry_lines lines"
    echo "  Unified files: ~$unified_lines lines"
    echo ""
    
    total_savings=$((old_lines + factory_lines + registry_lines + unified_lines))
    echo "TOTAL ESTIMATED SAVINGS: ~$total_savings lines"
    echo ""
    
    # Next steps
    echo "NEXT STEPS"
    echo "=========="
    echo ""
    echo "1. Review this report"
    echo "2. Create backup: cp -r src/pheno backups/pheno-$(date +%Y%m%d)"
    echo "3. Run cleanup script: ./scripts/cleanup_codebase.sh"
    echo "4. Review changes: git diff"
    echo "5. Run tests: pytest tests/"
    echo "6. Commit: git commit -m 'chore: cleanup phase 1'"
    echo ""
    
} | tee "$REPORT"

echo ""
echo "✅ Analysis complete!"
echo "Report saved to: $REPORT"
echo ""
echo "To proceed with cleanup:"
echo "  ./scripts/cleanup_codebase.sh"

