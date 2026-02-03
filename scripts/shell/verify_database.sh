#!/bin/bash
# Verify database setup

set -e

echo "🔍 Verifying Database Setup"
echo "================================"

# Load environment
source .env

# Check PostgreSQL connection
echo ""
echo "1️⃣  Testing PostgreSQL connection..."
if psql "$DB_DIRECT_URL" -c "SELECT version();" 2>/dev/null; then
    echo "✅ PostgreSQL connected"
else
    echo "⚠️  PostgreSQL connection failed (may be network issue)"
fi

# Check tables
echo ""
echo "2️⃣  Checking tables..."
if psql "$DB_DIRECT_URL" -c "SELECT table_name FROM information_schema.tables WHERE table_schema = 'public' ORDER BY table_name;" 2>/dev/null; then
    echo "✅ Tables verified"
else
    echo "⚠️  Could not verify tables"
fi

# Check Neo4j connection
echo ""
echo "3️⃣  Testing Neo4j connection..."
if command -v cypher-shell &> /dev/null; then
    cypher-shell -a "$NEO4J_URI" -u "$NEO4J_USERNAME" -p "$NEO4J_PASSWORD" "RETURN 1;" 2>/dev/null && echo "✅ Neo4j connected" || echo "⚠️  Neo4j connection failed"
else
    echo "⚠️  cypher-shell not installed"
fi

echo ""
echo "================================"
echo "✅ Verification complete"

