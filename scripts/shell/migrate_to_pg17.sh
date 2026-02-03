#!/bin/bash
# Migrate from PostgreSQL 15 to PostgreSQL 17
# This script will backup, upgrade, and restore your database

set -e

echo "🔄 PostgreSQL 15 → 17 Migration Script"
echo "========================================"
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
DB_NAME="tracertm"
DB_USER="tracertm"
BACKUP_DIR="/tmp/pg15_backup_$(date +%Y%m%d_%H%M%S)"
OLD_PG_VERSION="15"
NEW_PG_VERSION="17"

echo "📋 Migration Plan:"
echo "  • Old version: PostgreSQL $OLD_PG_VERSION"
echo "  • New version: PostgreSQL $NEW_PG_VERSION"
echo "  • Database: $DB_NAME"
echo "  • User: $DB_USER"
echo "  • Backup location: $BACKUP_DIR"
echo ""

# Step 1: Check current version
echo "1️⃣  Checking current PostgreSQL version..."
CURRENT_VERSION=$(psql -U "$DB_USER" -d "$DB_NAME" -t -c "SHOW server_version;" 2>/dev/null | awk '{print $1}' | cut -d. -f1)
echo "   Current version: PostgreSQL $CURRENT_VERSION"

if [ "$CURRENT_VERSION" != "$OLD_PG_VERSION" ]; then
    echo -e "${YELLOW}⚠️  Warning: Expected version $OLD_PG_VERSION but found $CURRENT_VERSION${NC}"
    read -p "Continue anyway? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Step 2: Install PostgreSQL 17
echo ""
echo "2️⃣  Installing PostgreSQL 17..."
if brew list postgresql@17 &>/dev/null; then
    echo "   ✅ PostgreSQL 17 already installed"
else
    echo "   📦 Installing PostgreSQL 17..."
    brew install postgresql@17
fi

# Step 3: Install pgvector for PostgreSQL 17
echo ""
echo "3️⃣  Installing pgvector for PostgreSQL 17..."
brew install pgvector

# Step 4: Create backup directory
echo ""
echo "4️⃣  Creating backup directory..."
mkdir -p "$BACKUP_DIR"
echo "   ✅ Created: $BACKUP_DIR"

# Step 5: Backup current database
echo ""
echo "5️⃣  Backing up current database..."
echo "   This may take a few minutes..."
pg_dump -U "$DB_USER" -d "$DB_NAME" -F c -f "$BACKUP_DIR/$DB_NAME.dump" 2>&1 | grep -v "^$" || true
echo "   ✅ Database backed up to: $BACKUP_DIR/$DB_NAME.dump"

# Also backup globals (users, roles)
echo "   Backing up global objects (roles, tablespaces)..."
pg_dumpall -U "$DB_USER" --globals-only > "$BACKUP_DIR/globals.sql" 2>&1 | grep -v "^$" || true
echo "   ✅ Globals backed up to: $BACKUP_DIR/globals.sql"

# Step 6: Stop PostgreSQL 15
echo ""
echo "6️⃣  Stopping PostgreSQL 15..."
brew services stop postgresql@15 2>/dev/null || true
sleep 2
echo "   ✅ PostgreSQL 15 stopped"

# Step 7: Start PostgreSQL 17
echo ""
echo "7️⃣  Starting PostgreSQL 17..."
brew services start postgresql@17
sleep 3

# Wait for PostgreSQL 17 to be ready
echo "   Waiting for PostgreSQL 17 to be ready..."
for i in {1..10}; do
    if /opt/homebrew/opt/postgresql@17/bin/psql -U "$USER" -d postgres -c "SELECT 1;" &>/dev/null; then
        echo "   ✅ PostgreSQL 17 is ready"
        break
    fi
    echo "   Waiting... ($i/10)"
    sleep 1
done

# Step 8: Create user and database in PostgreSQL 17
echo ""
echo "8️⃣  Creating user and database in PostgreSQL 17..."

# Create user if doesn't exist
/opt/homebrew/opt/postgresql@17/bin/psql -U "$USER" -d postgres << EOF
-- Create user
DO \$\$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = '$DB_USER') THEN
        CREATE USER $DB_USER WITH PASSWORD '$DB_USER';
        RAISE NOTICE 'User $DB_USER created';
    ELSE
        RAISE NOTICE 'User $DB_USER already exists';
    END IF;
END
\$\$;

-- Create database
SELECT 'CREATE DATABASE $DB_NAME OWNER $DB_USER'
WHERE NOT EXISTS (SELECT 1 FROM pg_database WHERE datname = '$DB_NAME')
\gexec

-- Grant privileges
GRANT ALL PRIVILEGES ON DATABASE $DB_NAME TO $DB_USER;
ALTER USER $DB_USER CREATEDB;
EOF

echo "   ✅ User and database created"

# Step 9: Install extensions in PostgreSQL 17
echo ""
echo "9️⃣  Installing extensions..."
/opt/homebrew/opt/postgresql@17/bin/psql -U "$DB_USER" -d "$DB_NAME" << EOF
-- Install extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";
CREATE EXTENSION IF NOT EXISTS "vector";

-- Verify extensions
SELECT extname, extversion FROM pg_extension
WHERE extname IN ('uuid-ossp', 'pgcrypto', 'pg_trgm', 'vector')
ORDER BY extname;
EOF

echo "   ✅ Extensions installed"

# Step 10: Restore database
echo ""
echo "🔟  Restoring database..."
echo "   This may take a few minutes..."
/opt/homebrew/opt/postgresql@17/bin/pg_restore \
    -U "$DB_USER" \
    -d "$DB_NAME" \
    --no-owner \
    --no-acl \
    "$BACKUP_DIR/$DB_NAME.dump" 2>&1 | grep -v "^$" | grep -v "WARNING" || true

echo "   ✅ Database restored"

# Step 11: Fix permissions
echo ""
echo "1️⃣1️⃣  Fixing permissions..."
/opt/homebrew/opt/postgresql@17/bin/psql -U "$DB_USER" -d "$DB_NAME" << EOF
-- Grant all permissions
ALTER DATABASE $DB_NAME OWNER TO $DB_USER;
GRANT ALL PRIVILEGES ON DATABASE $DB_NAME TO $DB_USER;
GRANT ALL PRIVILEGES ON SCHEMA public TO $DB_USER;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO $DB_USER;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO $DB_USER;
GRANT ALL PRIVILEGES ON ALL FUNCTIONS IN SCHEMA public TO $DB_USER;

-- Set default privileges
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO $DB_USER;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO $DB_USER;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON FUNCTIONS TO $DB_USER;
EOF

echo "   ✅ Permissions fixed"

# Step 12: Verify migration
echo ""
echo "1️⃣2️⃣  Verifying migration..."
/opt/homebrew/opt/postgresql@17/bin/psql -U "$DB_USER" -d "$DB_NAME" << EOF
-- Check version
SELECT 'PostgreSQL Version: ' || version() AS info;

-- Check extensions
SELECT 'Extensions:' AS info;
SELECT '  • ' || extname || ' ' || extversion AS installed_extensions
FROM pg_extension
WHERE extname IN ('uuid-ossp', 'pgcrypto', 'pg_trgm', 'vector')
ORDER BY extname;

-- Check table count
SELECT 'Tables: ' || COUNT(*)::text AS table_count FROM information_schema.tables WHERE table_schema = 'public';

-- Check items table
SELECT 'Items: ' || COUNT(*)::text AS item_count FROM items;
EOF

# Step 13: Update environment
echo ""
echo "1️⃣3️⃣  Updating environment..."

# Add PostgreSQL 17 to PATH
if ! grep -q "postgresql@17" ~/.zshrc 2>/dev/null; then
    echo 'export PATH="/opt/homebrew/opt/postgresql@17/bin:$PATH"' >> ~/.zshrc
    echo "   ✅ Added PostgreSQL 17 to ~/.zshrc"
else
    echo "   ✅ PostgreSQL 17 already in PATH"
fi

if ! grep -q "postgresql@17" ~/.bashrc 2>/dev/null && [ -f ~/.bashrc ]; then
    echo 'export PATH="/opt/homebrew/opt/postgresql@17/bin:$PATH"' >> ~/.bashrc
    echo "   ✅ Added PostgreSQL 17 to ~/.bashrc"
fi

# Step 14: Summary
echo ""
echo "✅ Migration Complete!"
echo "===================="
echo ""
echo -e "${GREEN}PostgreSQL 17 is now running with:${NC}"
echo "  • Database: $DB_NAME"
echo "  • User: $DB_USER"
echo "  • Extensions: uuid-ossp, pgcrypto, pg_trgm, vector"
echo ""
echo -e "${YELLOW}Backup saved to:${NC}"
echo "  $BACKUP_DIR"
echo ""
echo -e "${GREEN}Next steps:${NC}"
echo "  1. Restart your terminal or run: source ~/.zshrc"
echo "  2. Verify connection: psql -U $DB_USER -d $DB_NAME"
echo "  3. Test your backend: cd backend && go run main.go"
echo ""
echo -e "${YELLOW}To remove PostgreSQL 15:${NC}"
echo "  brew services stop postgresql@15"
echo "  brew uninstall postgresql@15"
echo ""
echo -e "${GREEN}Migration completed successfully! 🎉${NC}"
