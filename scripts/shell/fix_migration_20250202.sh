#!/bin/bash
# Fix migration 20250202000000 if it failed mid-execution

set -e

echo "🔧 Fixing migration 20250202000000..."

# Database credentials
DB_USER="${POSTGRES_USER:-tracertm}"
DB_NAME="${POSTGRES_DB:-tracertm}"

# Check if migration failed
psql -U "$DB_USER" -d "$DB_NAME" -c "SELECT version, dirty FROM schema_migrations WHERE version = 20250202000000;" 2>/dev/null || {
    echo "❌ Could not check migration status"
    exit 1
}

# If dirty flag is true, reset it
echo "Checking if migration is marked as dirty..."
DIRTY=$(psql -U "$DB_USER" -d "$DB_NAME" -t -c "SELECT dirty FROM schema_migrations WHERE version = 20250202000000;" 2>/dev/null | tr -d ' ')

if [ "$DIRTY" = "t" ]; then
    echo "⚠️  Migration marked as dirty, resetting..."
    psql -U "$DB_USER" -d "$DB_NAME" -c "UPDATE schema_migrations SET dirty = false WHERE version = 20250202000000;"
    echo "✅ Migration status reset"
else
    echo "✅ Migration not dirty, no reset needed"
fi

# Verify indexes exist
echo ""
echo "📊 Checking existing indexes..."
psql -U "$DB_USER" -d "$DB_NAME" -c "
    SELECT
        indexname,
        CASE
            WHEN indexdef LIKE '%GIN%' THEN 'GIN'
            WHEN indexdef LIKE '%HNSW%' THEN 'HNSW'
            WHEN indexdef LIKE '%BTREE%' THEN 'BTREE'
            ELSE 'OTHER'
        END as index_type
    FROM pg_indexes
    WHERE tablename = 'items'
    AND indexname LIKE '%search%' OR indexname LIKE '%trgm%' OR indexname LIKE '%embedding%'
    ORDER BY indexname;
"

echo ""
echo "✅ Migration fix complete!"
echo ""
echo "To re-run migrations, restart your backend server:"
echo "  cd backend && go run main.go"
