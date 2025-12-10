#!/bin/bash

# TraceRTM Neo4j Setup Script
# This script sets up Neo4j and other infrastructure for local development

set -e

echo "╔════════════════════════════════════════════════════════════════╗"
echo "║         TraceRTM Neo4j Setup Script                           ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    exit 1
fi

echo "✓ Docker is installed"

# Check if docker-compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo "❌ docker-compose is not installed. Please install docker-compose first."
    exit 1
fi

echo "✓ docker-compose is installed"
echo ""

# Start services
echo "🚀 Starting infrastructure services..."
docker-compose -f docker-compose.neo4j.yml up -d

echo ""
echo "⏳ Waiting for services to be healthy..."
sleep 10

# Check Neo4j
echo ""
echo "🔍 Checking Neo4j..."
if docker exec tracertm-neo4j cypher-shell -u neo4j -p password "RETURN 1" > /dev/null 2>&1; then
    echo "✓ Neo4j is running"
else
    echo "❌ Neo4j failed to start"
    exit 1
fi

# Check Redis
echo "🔍 Checking Redis..."
if docker exec tracertm-redis redis-cli ping > /dev/null 2>&1; then
    echo "✓ Redis is running"
else
    echo "❌ Redis failed to start"
    exit 1
fi

# Check NATS
echo "🔍 Checking NATS..."
if docker exec tracertm-nats curl -s http://localhost:8222/healthz > /dev/null 2>&1; then
    echo "✓ NATS is running"
else
    echo "❌ NATS failed to start"
    exit 1
fi

# Check Meilisearch
echo "🔍 Checking Meilisearch..."
if docker exec tracertm-meilisearch curl -s http://localhost:7700/health > /dev/null 2>&1; then
    echo "✓ Meilisearch is running"
else
    echo "❌ Meilisearch failed to start"
    exit 1
fi

echo ""
echo "╔════════════════════════════════════════════════════════════════╗"
echo "║                    ✅ Setup Complete!                         ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""
echo "📍 Service URLs:"
echo "   Neo4j Browser:  http://localhost:7474"
echo "   Neo4j Bolt:     neo4j://localhost:7687"
echo "   Redis:          redis://localhost:6379"
echo "   NATS:           nats://localhost:4222"
echo "   Meilisearch:    http://localhost:7700"
echo ""
echo "🔐 Credentials:"
echo "   Neo4j User:     neo4j"
echo "   Neo4j Password: password"
echo ""
echo "📝 Next steps:"
echo "   1. Copy .env.neo4j.example to .env"
echo "   2. Update DATABASE_URL in .env"
echo "   3. Run: cd backend && go build -o tracertm-backend main.go"
echo "   4. Run: ./tracertm-backend"
echo ""
echo "🛑 To stop services:"
echo "   docker-compose -f docker-compose.neo4j.yml down"
echo ""

