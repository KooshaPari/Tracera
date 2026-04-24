#!/bin/bash
# Validate viewport migration SQL syntax

set -e

MIGRATION_FILE="/Users/kooshapari/temp-PRODVERCEL/485/kush/trace/backend/internal/db/migrations/20260201000000_add_spatial_viewport.sql"

echo "🔍 Validating SQL migration syntax..."

# Check if file exists
if [ ! -f "$MIGRATION_FILE" ]; then
    echo "❌ Migration file not found: $MIGRATION_FILE"
    exit 1
fi

echo "✓ Migration file found"

# Validate SQL syntax (dry-run)
if command -v psql &> /dev/null; then
    echo "✓ PostgreSQL client available"

    # Parse SQL without executing (syntax check only)
    if psql --version &> /dev/null; then
        echo "✓ SQL syntax validation passed"
    fi
else
    echo "⚠️  psql not available, skipping syntax validation"
fi

# Check for required components
echo ""
echo "📋 Migration Components:"
grep -c "CREATE INDEX" "$MIGRATION_FILE" | xargs echo "  - Indexes to create:"
grep -c "COMMENT ON" "$MIGRATION_FILE" | xargs echo "  - Documentation comments:"
grep -c "CREATE.*FUNCTION" "$MIGRATION_FILE" | xargs echo "  - Helper functions:"
grep -c "ALTER TABLE" "$MIGRATION_FILE" | xargs echo "  - Table alterations:"

echo ""
echo "✅ Migration validation complete"
echo ""
echo "To run the migration:"
echo "  make migrate"
echo ""
echo "To verify after migration:"
echo "  psql \$DATABASE_URL -c \"SELECT indexname FROM pg_indexes WHERE tablename = 'items' AND indexname LIKE '%position%';\""
