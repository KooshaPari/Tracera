#!/bin/bash
# Infrastructure Verification Script for TraceRTM
# Checks that all required services are running and accessible

set -e

echo "=========================================="
echo "TraceRTM Infrastructure Verification"
echo "=========================================="

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check PostgreSQL
echo ""
echo "1. Checking PostgreSQL..."
if brew services list | grep -q "postgresql.*started"; then
    echo -e "   ${GREEN}✅ PostgreSQL is running${NC}"

    # Test connection
    if psql -U tracertm -d tracertm -c "SELECT 1;" > /dev/null 2>&1; then
        echo -e "   ${GREEN}✅ Database connection successful${NC}"
    else
        echo -e "   ${RED}❌ Database connection failed${NC}"
        echo "   Run: ./scripts/setup_database.sh"
        exit 1
    fi
else
    echo -e "   ${RED}❌ PostgreSQL is not running${NC}"
    echo "   Run: brew services start postgresql@14"
    exit 1
fi

# Check Neo4j
echo ""
echo "2. Checking Neo4j..."
if brew services list | grep -q "neo4j.*started"; then
    echo -e "   ${GREEN}✅ Neo4j is running${NC}"

    # Check if Neo4j is accessible (requires credentials in .env)
    if [ -f ".env.go-backend" ]; then
        source .env.go-backend 2>/dev/null || true
        if [ -n "$NEO4J_URI" ] && [ -n "$NEO4J_USER" ] && [ -n "$NEO4J_PASSWORD" ]; then
            echo -e "   ${GREEN}✅ Neo4j credentials configured${NC}"
        else
            echo -e "   ${YELLOW}⚠️  Neo4j credentials not set in .env.go-backend${NC}"
        fi
    else
        echo -e "   ${YELLOW}⚠️  .env.go-backend not found${NC}"
    fi
else
    echo -e "   ${RED}❌ Neo4j is not running${NC}"
    echo "   Run: brew services start neo4j"
    exit 1
fi

# Check cache runtime (optional)
echo ""
echo "3. Checking cache runtime (optional)..."
if brew services list | grep -Eq "(redis|dragonfly).*started"; then
    echo -e "   ${GREEN}✅ Cache runtime is running${NC}"
else
    echo -e "   ${YELLOW}⚠️  Cache runtime is not running (optional service)${NC}"
    echo "   To start: bash scripts/shell/redis-if-not-running.sh"
fi

# Check NATS (optional)
echo ""
echo "4. Checking NATS (optional)..."
if pgrep -f "nats-server" > /dev/null; then
    echo -e "   ${GREEN}✅ NATS is running${NC}"
else
    echo -e "   ${YELLOW}⚠️  NATS is not running (optional service)${NC}"
    echo "   To start: nats-server -c nats.conf &"
fi

# Check environment files
echo ""
echo "5. Checking environment configuration..."
if [ -f ".env.go-backend" ]; then
    echo -e "   ${GREEN}✅ .env.go-backend exists${NC}"

    # Check required variables
    source .env.go-backend 2>/dev/null || true

    if [ -z "$DATABASE_URL" ]; then
        echo -e "   ${RED}❌ DATABASE_URL not set${NC}"
    else
        echo -e "   ${GREEN}✅ DATABASE_URL configured${NC}"
    fi

    if [ -z "$NEO4J_URI" ]; then
        echo -e "   ${YELLOW}⚠️  NEO4J_URI not set${NC}"
    else
        echo -e "   ${GREEN}✅ NEO4J_URI configured${NC}"
    fi
else
    echo -e "   ${RED}❌ .env.go-backend not found${NC}"
    echo "   Copy from .env.example and configure"
    exit 1
fi

echo ""
echo "=========================================="
echo -e "${GREEN}Infrastructure verification complete!${NC}"
echo "=========================================="
echo ""
echo "You can now start the backend:"
echo "cd backend && go run main.go"
echo ""
