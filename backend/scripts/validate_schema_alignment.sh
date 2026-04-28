#!/bin/bash

# Schema Alignment Validation Script
# Validates alignment between migrations, GORM models, and sqlc models
# Exit codes: 0 = aligned, 1 = mismatches found, 2 = setup error

set -euo pipefail

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Counters
TOTAL_CHECKS=0
PASSED_CHECKS=0
FAILED_CHECKS=0
WARNINGS=0

# Validation tracking
declare -A TABLE_STATUS

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║       Schema Alignment Validation (CI/CD Ready)           ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""

# ============================================================================
# CONFIGURATION
# ============================================================================

# Use test database for validation
TEST_DB_NAME="${TEST_DB_NAME:-trace_validation_test}"
DB_HOST="${DB_HOST:-localhost}"
DB_PORT="${DB_PORT:-5432}"
DB_USER="${DB_USER:-postgres}"
DB_PASSWORD="${DB_PASSWORD:-postgres}"
DB_SCHEMA="${DB_SCHEMA:-public}"

MIGRATIONS_DIR="$PROJECT_ROOT/internal/db/migrations"
GORM_MODELS_FILE="$PROJECT_ROOT/internal/models/models.go"
SQLC_MODELS_FILE="$PROJECT_ROOT/internal/db/models.go"
SQLC_CONFIG="$PROJECT_ROOT/sqlc.yaml"

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

log_info() {
    echo -e "${BLUE}ℹ${NC} $1"
}

log_success() {
    echo -e "${GREEN}✅${NC} $1"
    ((PASSED_CHECKS++))
}

log_error() {
    echo -e "${RED}❌${NC} $1"
    ((FAILED_CHECKS++))
}

log_warning() {
    echo -e "${YELLOW}⚠️${NC} $1"
    ((WARNINGS++))
}

check_prerequisites() {
    log_info "Checking prerequisites..."

    local missing_tools=()

    if ! command -v psql &> /dev/null; then
        missing_tools+=("psql")
    fi

    if ! command -v go &> /dev/null; then
        missing_tools+=("go")
    fi

    if ! command -v sqlc &> /dev/null; then
        missing_tools+=("sqlc")
    fi

    if [ ${#missing_tools[@]} -gt 0 ]; then
        log_error "Missing required tools: ${missing_tools[*]}"
        echo "Please install missing tools and try again."
        exit 2
    fi

    log_success "All required tools found"
}

setup_test_database() {
    log_info "Setting up test database: $TEST_DB_NAME"

    # Drop and recreate test database
    PGPASSWORD=$DB_PASSWORD psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d postgres -c "DROP DATABASE IF EXISTS $TEST_DB_NAME;" 2>/dev/null || true
    PGPASSWORD=$DB_PASSWORD psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d postgres -c "CREATE DATABASE $TEST_DB_NAME;" || {
        log_error "Failed to create test database"
        exit 2
    }

    # Enable required extensions
    PGPASSWORD=$DB_PASSWORD psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$TEST_DB_NAME" <<EOF
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";
CREATE EXTENSION IF NOT EXISTS "vector";
EOF

    log_success "Test database created"
}

apply_migrations() {
    log_info "Applying migrations to test database..."

    # Apply migrations in order
    for migration in $(ls -1 "$MIGRATIONS_DIR"/*.sql 2>/dev/null | grep -v "atlas.sum" | sort); do
        local migration_name=$(basename "$migration")
        log_info "  Applying: $migration_name"

        PGPASSWORD=$DB_PASSWORD psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$TEST_DB_NAME" -f "$migration" || {
            log_error "Failed to apply migration: $migration_name"
            return 1
        }
    done

    log_success "All migrations applied successfully"
}

get_db_tables() {
    PGPASSWORD=$DB_PASSWORD psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$TEST_DB_NAME" -t -c "
        SELECT table_name
        FROM information_schema.tables
        WHERE table_schema = '$DB_SCHEMA'
        AND table_type = 'BASE TABLE'
        ORDER BY table_name;
    " | sed 's/^[[:space:]]*//;s/[[:space:]]*$//' | grep -v '^$'
}

get_table_columns() {
    local table_name=$1
    PGPASSWORD=$DB_PASSWORD psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$TEST_DB_NAME" -t -c "
        SELECT
            column_name,
            data_type,
            is_nullable,
            column_default
        FROM information_schema.columns
        WHERE table_schema = '$DB_SCHEMA'
        AND table_name = '$table_name'
        ORDER BY ordinal_position;
    " | sed 's/^[[:space:]]*//;s/[[:space:]]*$//' | grep -v '^$'
}

parse_gorm_models() {
    log_info "Parsing GORM models..."

    if [ ! -f "$GORM_MODELS_FILE" ]; then
        log_warning "GORM models file not found: $GORM_MODELS_FILE"
        return 1
    fi

    # Extract struct definitions and fields
    # Format: ModelName:field_name:type
    go run - <<'EOF'
package main

import (
    "fmt"
    "go/ast"
    "go/parser"
    "go/token"
    "os"
    "regexp"
    "strings"
)

func main() {
    fset := token.NewFileSet()
    node, err := parser.ParseFile(fset, os.Args[1], nil, parser.ParseComments)
    if err != nil {
        fmt.Fprintf(os.Stderr, "Error parsing file: %v\n", err)
        os.Exit(1)
    }

    gormTagRegex := regexp.MustCompile(`gorm:"([^"]*)"`)

    for _, decl := range node.Decls {
        genDecl, ok := decl.(*ast.GenDecl)
        if !ok || genDecl.Tok != token.TYPE {
            continue
        }

        for _, spec := range genDecl.Specs {
            typeSpec, ok := spec.(*ast.TypeSpec)
            if !ok {
                continue
            }

            structType, ok := typeSpec.Type.(*ast.StructType)
            if !ok {
                continue
            }

            modelName := typeSpec.Name.Name

            for _, field := range structType.Fields.List {
                if len(field.Names) == 0 {
                    continue
                }

                fieldName := field.Names[0].Name
                fieldType := ""

                switch t := field.Type.(type) {
                case *ast.Ident:
                    fieldType = t.Name
                case *ast.SelectorExpr:
                    if ident, ok := t.X.(*ast.Ident); ok {
                        fieldType = ident.Name + "." + t.Sel.Name
                    }
                case *ast.StarExpr:
                    if ident, ok := t.X.(*ast.Ident); ok {
                        fieldType = "*" + ident.Name
                    }
                }

                // Extract column name from gorm tag
                columnName := strings.ToLower(fieldName)
                if field.Tag != nil {
                    tagValue := field.Tag.Value
                    if matches := gormTagRegex.FindStringSubmatch(tagValue); len(matches) > 1 {
                        tags := matches[1]
                        for _, tag := range strings.Split(tags, ";") {
                            parts := strings.SplitN(tag, ":", 2)
                            if len(parts) == 2 && parts[0] == "column" {
                                columnName = parts[1]
                            }
                        }
                    }
                }

                fmt.Printf("%s:%s:%s\n", modelName, columnName, fieldType)
            }
        }
    }
}
EOF
    "$GORM_MODELS_FILE" 2>/dev/null | sort
}

parse_sqlc_models() {
    log_info "Parsing sqlc models..."

    if [ ! -f "$SQLC_MODELS_FILE" ]; then
        log_warning "sqlc models file not found: $SQLC_MODELS_FILE"
        return 1
    fi

    # Extract struct definitions from sqlc generated code
    # Format: ModelName:field_name:type
    grep -E '^\s+(type|[A-Z][a-zA-Z0-9_]*)\s+' "$SQLC_MODELS_FILE" | \
    awk '
    /^type [A-Z]/ {
        current_model = $2
        next
    }
    current_model && /^\s+[A-Z]/ {
        # Parse field: FieldName Type `db:"column"`
        field_name = $1
        field_type = $2

        # Extract db tag
        if (match($0, /db:"([^"]+)"/, arr)) {
            column_name = arr[1]
        } else {
            column_name = tolower(field_name)
        }

        print current_model ":" column_name ":" field_type
    }
    /^}/ {
        current_model = ""
    }
    ' | sort
}

validate_table_alignment() {
    local table_name=$1

    echo ""
    echo -e "${BLUE}─────────────────────────────────────────────────────────${NC}"
    log_info "Validating table: $table_name"

    ((TOTAL_CHECKS++))

    # Get database columns
    local db_columns=$(get_table_columns "$table_name" | awk -F'|' '{print $1}' | sed 's/^[[:space:]]*//;s/[[:space:]]*$//')

    # Find corresponding GORM model
    local model_name=$(echo "$table_name" | sed 's/_//g' | awk '{for(i=1;i<=NF;i++) sub(/./,toupper(substr($i,1,1)),$i)}1')
    local gorm_fields=$(parse_gorm_models | grep "^$model_name:" | cut -d: -f2)

    # Find corresponding sqlc model
    local sqlc_fields=$(parse_sqlc_models | grep -i "^${model_name}:" | cut -d: -f2)

    local has_gorm=false
    local has_sqlc=false
    local all_aligned=true

    if [ -n "$gorm_fields" ]; then
        has_gorm=true
        log_info "  Found GORM model: $model_name"
    else
        log_warning "  No GORM model found for table: $table_name"
        all_aligned=false
    fi

    if [ -n "$sqlc_fields" ]; then
        has_sqlc=true
        log_info "  Found sqlc model: $model_name"
    else
        log_warning "  No sqlc model found for table: $table_name"
        all_aligned=false
    fi

    # Compare database columns with GORM fields
    if [ "$has_gorm" = true ]; then
        local gorm_missing=0
        local gorm_extra=0

        # Check for columns in DB but not in GORM
        while IFS= read -r column; do
            if ! echo "$gorm_fields" | grep -q "^${column}$"; then
                log_error "    GORM missing column: $column"
                ((gorm_missing++))
                all_aligned=false
            fi
        done <<< "$db_columns"

        # Check for fields in GORM but not in DB
        while IFS= read -r field; do
            if ! echo "$db_columns" | grep -q "^${field}$"; then
                log_error "    GORM extra field: $field (not in DB)"
                ((gorm_extra++))
                all_aligned=false
            fi
        done <<< "$gorm_fields"

        if [ $gorm_missing -eq 0 ] && [ $gorm_extra -eq 0 ]; then
            log_success "  GORM model aligned with database"
        else
            log_error "  GORM misalignment: $gorm_missing missing, $gorm_extra extra"
        fi
    fi

    # Compare database columns with sqlc fields
    if [ "$has_sqlc" = true ]; then
        local sqlc_missing=0
        local sqlc_extra=0

        # Check for columns in DB but not in sqlc
        while IFS= read -r column; do
            if ! echo "$sqlc_fields" | grep -q "^${column}$"; then
                log_error "    sqlc missing column: $column"
                ((sqlc_missing++))
                all_aligned=false
            fi
        done <<< "$db_columns"

        # Check for fields in sqlc but not in DB
        while IFS= read -r field; do
            if ! echo "$db_columns" | grep -q "^${field}$"; then
                log_error "    sqlc extra field: $field (not in DB)"
                ((sqlc_extra++))
                all_aligned=false
            fi
        done <<< "$sqlc_fields"

        if [ $sqlc_missing -eq 0 ] && [ $sqlc_extra -eq 0 ]; then
            log_success "  sqlc model aligned with database"
        else
            log_error "  sqlc misalignment: $sqlc_missing missing, $sqlc_extra extra"
        fi
    fi

    # Set overall table status
    if [ "$all_aligned" = true ]; then
        TABLE_STATUS[$table_name]="✅ ALIGNED"
        log_success "Table '$table_name' is fully aligned"
    else
        TABLE_STATUS[$table_name]="❌ MISALIGNED"
        log_error "Table '$table_name' has alignment issues"
    fi
}

verify_sqlc_queries() {
    log_info "Verifying sqlc query coverage..."

    # Run sqlc generate to ensure queries compile
    cd "$PROJECT_ROOT"
    if sqlc generate 2>&1; then
        log_success "sqlc queries generated successfully"
    else
        log_error "sqlc generation failed - check queries"
        return 1
    fi
}

generate_report() {
    echo ""
    echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${BLUE}║                   VALIDATION REPORT                        ║${NC}"
    echo -e "${BLUE}╚════════════════════════════════════════════════════════════╝${NC}"
    echo ""

    # Summary by table
    echo "Table Alignment Summary:"
    echo "─────────────────────────────────────────────────────────"
    for table in "${!TABLE_STATUS[@]}"; do
        echo "  $table: ${TABLE_STATUS[$table]}"
    done | sort

    echo ""
    echo "Statistics:"
    echo "─────────────────────────────────────────────────────────"
    echo "  Total Checks:   $TOTAL_CHECKS"
    echo "  Passed:         $PASSED_CHECKS (${GREEN}✅${NC})"
    echo "  Failed:         $FAILED_CHECKS (${RED}❌${NC})"
    echo "  Warnings:       $WARNINGS (${YELLOW}⚠️${NC})"

    echo ""

    if [ $FAILED_CHECKS -eq 0 ]; then
        echo -e "${GREEN}╔════════════════════════════════════════════════════════════╗${NC}"
        echo -e "${GREEN}║          ✅ ALL SCHEMAS ALIGNED - VALIDATION PASSED        ║${NC}"
        echo -e "${GREEN}╚════════════════════════════════════════════════════════════╝${NC}"
        return 0
    else
        echo -e "${RED}╔════════════════════════════════════════════════════════════╗${NC}"
        echo -e "${RED}║         ❌ SCHEMA MISMATCHES FOUND - VALIDATION FAILED     ║${NC}"
        echo -e "${RED}╚════════════════════════════════════════════════════════════╝${NC}"
        echo ""
        echo "Action Required:"
        echo "  1. Review migration files"
        echo "  2. Update GORM models to match database schema"
        echo "  3. Regenerate sqlc models: sqlc generate"
        echo "  4. Re-run this validation script"
        return 1
    fi
}

cleanup() {
    if [ "${KEEP_TEST_DB:-false}" != "true" ]; then
        log_info "Cleaning up test database..."
        PGPASSWORD=$DB_PASSWORD psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d postgres -c "DROP DATABASE IF EXISTS $TEST_DB_NAME;" 2>/dev/null || true
    else
        log_info "Keeping test database: $TEST_DB_NAME (KEEP_TEST_DB=true)"
    fi
}

# ============================================================================
# MAIN EXECUTION
# ============================================================================

main() {
    # Trap cleanup on exit
    trap cleanup EXIT

    # Step 1: Prerequisites
    check_prerequisites

    # Step 2: Setup test database
    setup_test_database

    # Step 3: Apply migrations
    apply_migrations || {
        log_error "Migration application failed"
        exit 1
    }

    # Step 4: Get list of tables
    log_info "Discovering database tables..."
    local tables=$(get_db_tables)
    local table_count=$(echo "$tables" | wc -l | tr -d ' ')
    log_info "Found $table_count tables"

    # Step 5: Validate each table
    while IFS= read -r table; do
        validate_table_alignment "$table"
    done <<< "$tables"

    # Step 6: Verify sqlc queries
    verify_sqlc_queries || true

    # Step 7: Generate report
    echo ""
    generate_report
    local exit_code=$?

    exit $exit_code
}

# Run main function
main "$@"
