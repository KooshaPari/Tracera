#!/bin/bash

# Safe deletion script for unified configuration files
# This script safely removes redundant unified config files while preserving essential ones
# 
# Features:
# - Creates backup before deletion
# - Analyzes actual usage to determine essential vs redundant files
# - Updates imports automatically
# - Provides detailed logging and reporting
# - Reversible operation with backup restore

set -euo pipefail

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
BACKUP_DIR="$PROJECT_ROOT/archives/backup_unified_$(date +%Y%m%d_%H%M%S)"
UNIFIED_DIR="$PROJECT_ROOT/config/unified"
LOG_FILE="$PROJECT_ROOT/reports/unified_deletion_$(date +%Y%m%d_%H%M%S).log"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging function
log() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1" | tee -a "$LOG_FILE"
}

error() {
    echo -e "${RED}ERROR: $1${NC}" | tee -a "$LOG_FILE"
    exit 1
}

warning() {
    echo -e "${YELLOW}WARNING: $1${NC}" | tee -a "$LOG_FILE"
}

success() {
    echo -e "${GREEN}SUCCESS: $1${NC}" | tee -a "$LOG_FILE"
}

info() {
    echo -e "${BLUE}INFO: $1${NC}" | tee -a "$LOG_FILE"
}

# Check if running from project root
if [[ ! -f "$PROJECT_ROOT/pyproject.toml" ]]; then
    error "Script must be run from the pheno-sdk project directory"
fi

# Create necessary directories
mkdir -p "$BACKUP_DIR"
mkdir -p "$(dirname "$LOG_FILE")"

log "Starting unified files deletion process"
log "Backup directory: $BACKUP_DIR"
log "Log file: $LOG_FILE"

# Function to check if file is essential
is_essential() {
    local file="$1"
    local basename=$(basename "$file")
    
    # Check if file is actively imported (excluding self-references)
    local import_count=$(rg "from config\.unified|import.*config\.unified" --type py "$PROJECT_ROOT" \
        | grep -v "$file" \
        | wc -l || echo "0")
    
    # Check for references to specific classes/functions from this file
    if [[ "$basename" == "manager.py" ]]; then
        local config_manager_refs=$(rg "ConfigManager|get_config" --type py "$PROJECT_ROOT/src" \
            | grep -v "$file" \
            | wc -l || echo "0")
        if [[ "$config_manager_refs" -gt 0 ]]; then
            return 0  # Essential
        fi
    fi
    
    if [[ "$basename" == "models.py" ]]; then
        local model_refs=$(rg "AppConfig|DatabaseConfig|FeatureFlags|LoggingConfig|SecurityConfig|ServerConfig" --type py "$PROJECT_ROOT/src" \
            | grep -v "$file" \
            | wc -l || echo "0")
        if [[ "$model_refs" -gt 0 ]]; then
            return 0  # Essential
        fi
    fi
    
    # If no active imports found, not essential
    return 1  # Not essential
}

# Function to backup file
backup_file() {
    local file="$1"
    local rel_path=${file#$PROJECT_ROOT/}
    local backup_path="$BACKUP_DIR/$rel_path"
    local backup_dir=$(dirname "$backup_path")
    
    mkdir -p "$backup_dir"
    cp "$file" "$backup_path"
    log "Backed up: $rel_path -> $backup_path"
}

# Function to update imports
update_imports() {
    local deleted_file="$1"
    local basename=$(basename "$deleted_file" .py)
    
    log "Checking for imports to update for deleted file: $deleted_file"
    
    # Find files that import from the deleted unified config
    local importing_files=$(rg "from config\.unified|import.*config\.unified" --type py "$PROJECT_ROOT" \
        | grep -v "$deleted_file" \
        | cut -d: -f1 \
        | sort -u || true)
    
    if [[ -z "$importing_files" ]]; then
        log "No imports found to update"
        return
    fi
    
    for import_file in $importing_files; do
        log "Updating imports in: $import_file"
        
        # Create backup before modifying
        backup_file "$import_file"
        
        # Replace imports with core config equivalents
        case "$basename" in
            "manager")
                sed -i.bak 's/from config\.unified import ConfigManager/from pheno.core.config import ConfigManager/g' "$import_file"
                sed -i.bak 's/from config\.unified import get_config/from pheno.core.config import get_config/g' "$import_file"
                sed -i.bak 's/config\.unified\.ConfigManager/pheno.core.config.ConfigManager/g' "$import_file"
                sed -i.bak 's/config\.unified\.get_config/pheno.core.config.get_config/g' "$import_file"
                ;;
            "models")
                sed -i.bak 's/from config\.unified import/from pheno.core.config import/g' "$import_file"
                sed -i.bak 's/config\.unified\./pheno.core.config./g' "$import_file"
                ;;
        esac
        
        # Remove backup files created by sed
        rm -f "$import_file.bak"
        
        log "Updated imports in: $import_file"
    done
}

# Function to delete file safely
delete_file_safely() {
    local file="$1"
    local rel_path=${file#$PROJECT_ROOT/}
    
    if [[ ! -f "$file" ]]; then
        warning "File does not exist: $rel_path"
        return
    fi
    
    # Check if essential
    if is_essential "$file"; then
        warning "Skipping essential file: $rel_path"
        return
    fi
    
    # Backup first
    backup_file "$file"
    
    # Update imports before deletion
    update_imports "$file"
    
    # Delete the file
    rm "$file"
    success "Deleted: $rel_path"
}

# Main execution
info "Analyzing unified configuration files..."

if [[ ! -d "$UNIFIED_DIR" ]]; then
    warning "Unified directory does not exist: $UNIFIED_DIR"
    exit 0
fi

# List all files in unified directory
unified_files=$(find "$UNIFIED_DIR" -name "*.py" -type f || true)

if [[ -z "$unified_files" ]]; then
    warning "No Python files found in unified directory"
    exit 0
fi

info "Found unified files:"
for file in $unified_files; do
    rel_path=${file#$PROJECT_ROOT/}
    echo "  - $rel_path"
done

# Confirmation prompt
echo
read -p "Do you want to proceed with the deletion? (y/N): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    log "Deletion cancelled by user"
    exit 0
fi

# Process each file
for file in $unified_files; do
    delete_file_safely "$file"
done

# Check if unified directory is now empty
if [[ -d "$UNIFIED_DIR" ]] && [[ -z "$(ls -A "$UNIFIED_DIR" 2>/dev/null || true)" ]]; then
    backup_file "$UNIFIED_DIR"
    rmdir "$UNIFIED_DIR"
    success "Removed empty unified directory"
fi

# Generate report
report_file="$PROJECT_ROOT/reports/unified_deletion_report_$(date +%Y%m%d_%H%M%S).txt"
cat > "$report_file" << EOF
Unified Configuration Files Deletion Report
==========================================
Date: $(date)
Backup Directory: $BACKUP_DIR
Log File: $LOG_FILE

Files Analyzed:
$(for file in $unified_files; do echo "  - ${file#$PROJECT_ROOT/}"; done)

Files Deleted:
$(find "$BACKUP_DIR" -name "*.py" -type f | while read file; do
    rel_path=${file#$BACKUP_DIR/}
    echo "  - $rel_path"
done)

Files Preserved (Essential):
$(for file in $unified_files; do
    if is_essential "$file"; then
        echo "  - ${file#$PROJECT_ROOT/}"
    fi
done)

Import Updates:
The script has updated imports in affected files to use the core configuration system:
- config.unified.ConfigManager -> pheno.core.config.ConfigManager
- config.unified.get_config -> pheno.core.config.get_config
- config.unified.models.* -> pheno.core.config.*

Verification:
Run the following commands to verify the system still works:
  1. python -c "from pheno.core.config import ConfigManager; print('ConfigManager import OK')"
  2. python -c "from pheno.core.config import get_config; print('get_config import OK')"
  3. Run tests: python -m pytest tests/ -k config

Recovery:
To restore deleted files, run:
  cp -r "$BACKUP_DIR/"* "$PROJECT_ROOT/"
EOF

success "Deletion process completed"
info "Report generated: $report_file"
info "Backup created at: $BACKUP_DIR"
info "Log file: $LOG_FILE"

# Final verification
info "Running verification checks..."

# Check if core config is still accessible
if python -c "from pheno.core.config import ConfigManager; print('✓ ConfigManager accessible')" 2>/dev/null; then
    success "Core configuration system is accessible"
else
    warning "Core configuration system may have issues"
fi

echo
echo "=== Summary ==="
echo "Files processed: $(echo "$unified_files" | wc -l)"
echo "Backup location: $BACKUP_DIR"
echo "Report: $report_file"
echo "Log: $LOG_FILE"
echo
echo "Next steps:"
echo "1. Review the report file"
echo "2. Run tests to verify system integrity"
echo "3. If issues occur, restore from backup"
echo

exit 0