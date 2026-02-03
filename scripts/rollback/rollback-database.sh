#!/bin/bash
# Database Rollback Script
# Rolls back database schema and data to last stable state

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
SNAPSHOT_DIR="${PROJECT_ROOT}/.deployments/snapshots/database"
STABLE_VERSION_FILE="${PROJECT_ROOT}/.deployments/database-stable-version.txt"
DB_HOST="${DB_HOST:-localhost}"
DB_PORT="${DB_PORT:-5432}"
DB_USER="${DB_USER:-tracertm}"
DB_NAME="${DB_NAME:-tracertm}"
DB_PASSWORD="${DB_PASSWORD:-tracertm_password}"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

log() {
    echo -e "${GREEN}[DATABASE-ROLLBACK]${NC} $*"
}

log_error() {
    echo -e "${RED}[DATABASE-ROLLBACK ERROR]${NC} $*" >&2
}

log_warning() {
    echo -e "${YELLOW}[DATABASE-ROLLBACK WARNING]${NC} $*"
}

# Get stable version
get_stable_version() {
    if [ -f "$STABLE_VERSION_FILE" ]; then
        cat "$STABLE_VERSION_FILE"
    else
        log_error "No stable version recorded"
        return 1
    fi
}

# Create pre-rollback backup
create_pre_rollback_backup() {
    local backup_dir="${PROJECT_ROOT}/.deployments/backups/database"
    mkdir -p "$backup_dir"
    local timestamp=$(date +%Y%m%d%H%M%S)
    local backup_file="${backup_dir}/pre-rollback-${timestamp}.sql"

    log "Creating pre-rollback backup: $backup_file"

    PGPASSWORD="$DB_PASSWORD" pg_dump \
        -h "$DB_HOST" \
        -p "$DB_PORT" \
        -U "$DB_USER" \
        -d "$DB_NAME" \
        -F p \
        -f "$backup_file"

    if [ $? -eq 0 ]; then
        log "Pre-rollback backup created successfully"
        # Compress the backup
        gzip "$backup_file"
        return 0
    else
        log_error "Failed to create pre-rollback backup"
        return 1
    fi
}

# Rollback database using Alembic
rollback_database_migrations() {
    local target_version="$1"

    log "Rolling back database migrations to version: $target_version"

    cd "$PROJECT_ROOT"

    # Check if Alembic is available
    if ! command -v alembic &>/dev/null; then
        log_error "Alembic not found - cannot rollback migrations"
        return 1
    fi

    # Get current migration version
    local current_version=$(alembic current 2>/dev/null | grep -oE '[a-f0-9]{12}' | head -1)
    log "Current migration version: ${current_version:-unknown}"

    # Rollback to target version
    if [ -n "$target_version" ] && [ "$target_version" != "base" ]; then
        log "Downgrading to migration: $target_version"
        alembic downgrade "$target_version"
    else
        log_warning "No specific migration version - using snapshot restore"
        return 1
    fi

    return 0
}

# Restore database from snapshot
restore_database_snapshot() {
    local stable_version="$1"
    local snapshot_file="${SNAPSHOT_DIR}/${stable_version}.sql"

    if [ ! -f "$snapshot_file" ]; then
        # Try compressed version
        snapshot_file="${SNAPSHOT_DIR}/${stable_version}.sql.gz"
        if [ ! -f "$snapshot_file" ]; then
            log_error "Database snapshot not found: ${SNAPSHOT_DIR}/${stable_version}.sql[.gz]"
            return 1
        fi
    fi

    log "Restoring database from snapshot: $snapshot_file"

    # Terminate all connections to the database
    log "Terminating active connections..."
    PGPASSWORD="$DB_PASSWORD" psql \
        -h "$DB_HOST" \
        -p "$DB_PORT" \
        -U "$DB_USER" \
        -d postgres \
        -c "SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE datname = '$DB_NAME' AND pid <> pg_backend_pid();" \
        >/dev/null 2>&1 || true

    # Drop and recreate database
    log "Recreating database..."
    PGPASSWORD="$DB_PASSWORD" psql \
        -h "$DB_HOST" \
        -p "$DB_PORT" \
        -U "$DB_USER" \
        -d postgres \
        -c "DROP DATABASE IF EXISTS $DB_NAME;" \
        >/dev/null 2>&1

    PGPASSWORD="$DB_PASSWORD" psql \
        -h "$DB_HOST" \
        -p "$DB_PORT" \
        -U "$DB_USER" \
        -d postgres \
        -c "CREATE DATABASE $DB_NAME OWNER $DB_USER;" \
        >/dev/null 2>&1

    # Restore from snapshot
    if [[ "$snapshot_file" == *.gz ]]; then
        log "Decompressing and restoring..."
        gunzip -c "$snapshot_file" | PGPASSWORD="$DB_PASSWORD" psql \
            -h "$DB_HOST" \
            -p "$DB_PORT" \
            -U "$DB_USER" \
            -d "$DB_NAME" \
            >/dev/null 2>&1
    else
        PGPASSWORD="$DB_PASSWORD" psql \
            -h "$DB_HOST" \
            -p "$DB_PORT" \
            -U "$DB_USER" \
            -d "$DB_NAME" \
            -f "$snapshot_file" \
            >/dev/null 2>&1
    fi

    if [ $? -eq 0 ]; then
        log "Database restored successfully"
        return 0
    else
        log_error "Failed to restore database"
        return 1
    fi
}

# Verify database health
verify_health() {
    log "Verifying database health..."

    # Check if database is accessible
    if ! PGPASSWORD="$DB_PASSWORD" pg_isready -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" >/dev/null 2>&1; then
        log_error "Database is not ready"
        return 1
    fi

    # Check if critical tables exist
    local critical_tables=("items" "projects" "users" "links")
    for table in "${critical_tables[@]}"; do
        local exists=$(PGPASSWORD="$DB_PASSWORD" psql \
            -h "$DB_HOST" \
            -p "$DB_PORT" \
            -U "$DB_USER" \
            -d "$DB_NAME" \
            -tAc "SELECT COUNT(*) FROM information_schema.tables WHERE table_name='$table';" 2>/dev/null)

        if [ "$exists" != "1" ]; then
            log_error "Critical table '$table' does not exist"
            return 1
        fi
    done

    # Check database connectivity with a simple query
    local result=$(PGPASSWORD="$DB_PASSWORD" psql \
        -h "$DB_HOST" \
        -p "$DB_PORT" \
        -U "$DB_USER" \
        -d "$DB_NAME" \
        -tAc "SELECT 1;" 2>/dev/null)

    if [ "$result" != "1" ]; then
        log_error "Database query test failed"
        return 1
    fi

    log "Database health verification passed"
    return 0
}

# Main
main() {
    log "Starting database rollback..."

    # Create pre-rollback backup
    if ! create_pre_rollback_backup; then
        log_error "Failed to create pre-rollback backup - aborting"
        exit 1
    fi

    local stable_version
    stable_version=$(get_stable_version)

    # Try migration-based rollback first (faster)
    log "Attempting migration-based rollback..."
    if rollback_database_migrations "$stable_version"; then
        log "Migration-based rollback successful"

        if verify_health; then
            log "Database rollback and health verification successful"
            exit 0
        fi
    fi

    # Fall back to snapshot restore
    log "Migration rollback failed or unavailable - using snapshot restore"
    if restore_database_snapshot "$stable_version"; then
        log "Snapshot restore successful"

        if verify_health; then
            log "Database rollback and health verification successful"
            exit 0
        else
            log_error "Database health verification failed after restore"
            exit 1
        fi
    else
        log_error "Database rollback failed"
        exit 1
    fi
}

main "$@"
