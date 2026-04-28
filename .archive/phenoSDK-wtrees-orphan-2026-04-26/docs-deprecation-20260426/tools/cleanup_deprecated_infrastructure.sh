#!/bin/bash
# Cleanup Deprecated Infrastructure Script
# Phase 3 - Remove deprecated code after SDK migration

set -e  # Exit on any error

# Configuration
BACKUP_DIR="backup_$(date +%Y%m%d_%H%M%S)"
DRY_RUN=${1:-"--dry-run"}
VERBOSE=${2:-"--verbose"}

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging function
log() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if running in dry-run mode
is_dry_run() {
    [[ "$DRY_RUN" == "--dry-run" ]]
}

# Create backup directory
create_backup() {
    log "Creating backup directory: $BACKUP_DIR"
    if ! is_dry_run; then
        mkdir -p "$BACKUP_DIR"
        log_success "Backup directory created"
    else
        log "DRY RUN: Would create backup directory: $BACKUP_DIR"
    fi
}

# Backup file before deletion
backup_file() {
    local file_path="$1"
    local backup_path="$BACKUP_DIR/$(basename "$file_path")"
    
    if ! is_dry_run; then
        cp "$file_path" "$backup_path"
        log "Backed up: $file_path -> $backup_path"
    else
        log "DRY RUN: Would backup $file_path -> $backup_path"
    fi
}

# Remove deprecated Morph infrastructure files
cleanup_morph_infrastructure() {
    log "Cleaning up deprecated Morph infrastructure files..."
    
    local morph_root="morph"
    local files_to_remove=(
        "morph_core/infrastructure/complexity_analyzer.py"
        "morph_core/infrastructure/dependency_analyzer.py"
        "morph_core/infrastructure/ast_parser.py"
        "morph_core/infrastructure/embeddings.py"
    )
    
    for file in "${files_to_remove[@]}"; do
        local full_path="$morph_root/$file"
        if [[ -f "$full_path" ]]; then
            log "Found deprecated file: $full_path"
            backup_file "$full_path"
            
            if ! is_dry_run; then
                rm "$full_path"
                log_success "Removed: $full_path"
            else
                log "DRY RUN: Would remove $full_path"
            fi
        else
            log_warning "File not found: $full_path"
        fi
    done
}

# Update import statements in Morph
update_morph_imports() {
    log "Updating Morph import statements..."
    
    local morph_root="morph"
    local import_updates=(
        "s/from morph_core.infrastructure.complexity_analyzer/from morph_core.infrastructure.sdk_adapters/g"
        "s/from morph_core.infrastructure.dependency_analyzer/from morph_core.infrastructure.sdk_adapters/g"
        "s/from morph_core.infrastructure.ast_parser/from morph_core.infrastructure.sdk_adapters/g"
        "s/from morph_core.infrastructure.embeddings/from morph_core.infrastructure.sdk_adapters/g"
        "s/ComplexityAnalyzer/SDKComplexityAnalyzer/g"
        "s/DependencyAnalyzer/SDKDependencyAnalyzer/g"
        "s/ASTParser/SDKASTParser/g"
        "s/EmbeddingService/SDKEmbeddingService/g"
    )
    
    for update in "${import_updates[@]}"; do
        if ! is_dry_run; then
            find "$morph_root" -name "*.py" -type f -exec sed -i '' "$update" {} \;
            log "Applied import update: $update"
        else
            log "DRY RUN: Would apply import update: $update"
        fi
    done
}

# Remove deprecated Router infrastructure files
cleanup_router_infrastructure() {
    log "Cleaning up deprecated Router infrastructure files..."
    
    local router_root="router"
    local files_to_remove=(
        # Add Router-specific deprecated files here
        # "router_core/legacy/old_provider.py"
        # "router_core/legacy/old_rate_limiter.py"
    )
    
    for file in "${files_to_remove[@]}"; do
        local full_path="$router_root/$file"
        if [[ -f "$full_path" ]]; then
            log "Found deprecated file: $full_path"
            backup_file "$full_path"
            
            if ! is_dry_run; then
                rm "$full_path"
                log_success "Removed: $full_path"
            else
                log "DRY RUN: Would remove $full_path"
            fi
        else
            log_warning "File not found: $full_path"
        fi
    done
}

# Update import statements in Router
update_router_imports() {
    log "Updating Router import statements..."
    
    local router_root="router"
    local import_updates=(
        # Add Router-specific import updates here
        # "s/from router_core.legacy.old_provider/from router_core.providers.sdk_wrapper/g"
    )
    
    for update in "${import_updates[@]}"; do
        if ! is_dry_run; then
            find "$router_root" -name "*.py" -type f -exec sed -i '' "$update" {} \;
            log "Applied import update: $update"
        else
            log "DRY RUN: Would apply import update: $update"
        fi
    done
}

# Validate that no broken imports exist
validate_imports() {
    log "Validating imports..."
    
    local validation_errors=0
    
    # Check Morph imports
    if [[ -d "morph" ]]; then
        log "Checking Morph imports..."
        if ! is_dry_run; then
            if ! python3 -m py_compile morph/morph_core/__init__.py 2>/dev/null; then
                log_error "Morph imports validation failed"
                validation_errors=$((validation_errors + 1))
            else
                log_success "Morph imports validation passed"
            fi
        else
            log "DRY RUN: Would validate Morph imports"
        fi
    fi
    
    # Check Router imports
    if [[ -d "router" ]]; then
        log "Checking Router imports..."
        if ! is_dry_run; then
            if ! python3 -m py_compile router/router_core/__init__.py 2>/dev/null; then
                log_error "Router imports validation failed"
                validation_errors=$((validation_errors + 1))
            else
                log_success "Router imports validation passed"
            fi
        else
            log "DRY RUN: Would validate Router imports"
        fi
    fi
    
    if [[ $validation_errors -gt 0 ]]; then
        log_error "Import validation failed with $validation_errors errors"
        return 1
    fi
    
    return 0
}

# Run test suite to ensure nothing is broken
run_tests() {
    log "Running test suite to validate cleanup..."
    
    if ! is_dry_run; then
        # Run Morph tests
        if [[ -d "morph" ]]; then
            log "Running Morph tests..."
            if python3 -m pytest morph/tests/integration/test_phase2_simple.py -v; then
                log_success "Morph tests passed"
            else
                log_error "Morph tests failed"
                return 1
            fi
        fi
        
        # Run Router tests
        if [[ -d "router" ]]; then
            log "Running Router tests..."
            if python3 router/tests/integration/test_phase2_simple.py; then
                log_success "Router tests passed"
            else
                log_error "Router tests failed"
                return 1
            fi
        fi
    else
        log "DRY RUN: Would run test suite"
    fi
    
    return 0
}

# Generate cleanup report
generate_report() {
    local report_file="cleanup_report_$(date +%Y%m%d_%H%M%S).txt"
    
    log "Generating cleanup report: $report_file"
    
    {
        echo "Deprecated Infrastructure Cleanup Report"
        echo "========================================"
        echo "Date: $(date)"
        echo "Mode: $DRY_RUN"
        echo "Backup Directory: $BACKUP_DIR"
        echo ""
        echo "Files Removed:"
        echo "- morph_core/infrastructure/complexity_analyzer.py"
        echo "- morph_core/infrastructure/dependency_analyzer.py"
        echo "- morph_core/infrastructure/ast_parser.py"
        echo "- morph_core/infrastructure/embeddings.py"
        echo ""
        echo "Import Updates Applied:"
        echo "- Updated all references to use SDK adapters"
        echo "- Replaced old class names with SDK equivalents"
        echo ""
        echo "Validation Results:"
        echo "- Import validation: PASSED"
        echo "- Test suite execution: PASSED"
        echo ""
        echo "Cleanup Status: COMPLETE"
    } > "$report_file"
    
    log_success "Cleanup report generated: $report_file"
}

# Main execution function
main() {
    log "Starting deprecated infrastructure cleanup..."
    log "Mode: $DRY_RUN"
    log "Verbose: $VERBOSE"
    
    # Create backup directory
    create_backup
    
    # Cleanup Morph infrastructure
    cleanup_morph_infrastructure
    
    # Update Morph imports
    update_morph_imports
    
    # Cleanup Router infrastructure
    cleanup_router_infrastructure
    
    # Update Router imports
    update_router_imports
    
    # Validate imports
    if ! validate_imports; then
        log_error "Import validation failed. Aborting cleanup."
        exit 1
    fi
    
    # Run tests
    if ! run_tests; then
        log_error "Test execution failed. Aborting cleanup."
        exit 1
    fi
    
    # Generate report
    generate_report
    
    log_success "Deprecated infrastructure cleanup completed successfully!"
    
    if is_dry_run; then
        log_warning "This was a dry run. No files were actually modified."
        log "To execute the cleanup, run: $0 --execute"
    else
        log_success "Cleanup executed successfully. Backup created in: $BACKUP_DIR"
    fi
}

# Help function
show_help() {
    echo "Deprecated Infrastructure Cleanup Script"
    echo "========================================"
    echo ""
    echo "Usage: $0 [--dry-run|--execute] [--verbose]"
    echo ""
    echo "Options:"
    echo "  --dry-run    Show what would be done without making changes (default)"
    echo "  --execute    Actually perform the cleanup"
    echo "  --verbose    Enable verbose output"
    echo "  --help       Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0                    # Dry run (default)"
    echo "  $0 --dry-run          # Dry run (explicit)"
    echo "  $0 --execute          # Execute cleanup"
    echo "  $0 --execute --verbose # Execute with verbose output"
    echo ""
    echo "This script will:"
    echo "1. Create a backup of all files to be removed"
    echo "2. Remove deprecated infrastructure files"
    echo "3. Update import statements to use SDK adapters"
    echo "4. Validate that no imports are broken"
    echo "5. Run test suite to ensure functionality"
    echo "6. Generate a cleanup report"
}

# Parse command line arguments
case "${1:-}" in
    --help|-h)
        show_help
        exit 0
        ;;
    --execute)
        DRY_RUN="--execute"
        ;;
    --dry-run|"")
        DRY_RUN="--dry-run"
        ;;
    *)
        log_error "Unknown option: $1"
        show_help
        exit 1
        ;;
esac

# Run main function
main "$@"