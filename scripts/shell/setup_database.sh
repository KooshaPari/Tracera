#!/bin/bash
# Database Setup Script for TraceRTM
# Sets up PostgreSQL database and user with correct permissions

set -e

echo "=========================================="
echo "TraceRTM Database Setup"
echo "=========================================="

# Database configuration
DB_NAME="tracertm"
DB_USER="tracertm"
DB_PASSWORD="tracertm_password"

echo ""
echo "1. Creating database user..."
psql -d postgres -c "CREATE USER $DB_USER WITH PASSWORD '$DB_PASSWORD' CREATEDB;" 2>/dev/null || echo "   User $DB_USER already exists, skipping..."

echo ""
echo "2. Creating database..."
psql -d postgres -c "CREATE DATABASE $DB_NAME OWNER $DB_USER;" 2>/dev/null || echo "   Database $DB_NAME already exists, skipping..."

echo ""
echo "3. Granting database permissions..."
psql -d postgres -c "GRANT ALL PRIVILEGES ON DATABASE $DB_NAME TO $DB_USER;"

echo ""
echo "4. Setting database owner..."
psql -d postgres -c "ALTER DATABASE $DB_NAME OWNER TO $DB_USER;"

echo ""
echo "5. Granting schema permissions..."
psql -d $DB_NAME <<EOF
GRANT ALL PRIVILEGES ON SCHEMA public TO $DB_USER;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO $DB_USER;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO $DB_USER;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO $DB_USER;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO $DB_USER;
EOF

echo ""
echo "6. Testing connection..."
if psql -U $DB_USER -d $DB_NAME -c "SELECT version();" > /dev/null 2>&1; then
    echo "   ✅ Connection test successful!"
else
    echo "   ❌ Connection test failed!"
    exit 1
fi

echo ""
echo "=========================================="
echo "Database setup completed successfully!"
echo "=========================================="
echo ""
echo "Database URL for .env.go-backend:"
echo "DATABASE_URL=postgres://$DB_USER:$DB_PASSWORD@localhost:5432/$DB_NAME"
echo ""
echo "To test the connection:"
echo "psql -U $DB_USER -d $DB_NAME"
echo ""
